# SafeLab — Arquitetura

Este documento descreve **a base técnica do projeto** e **como o domínio
químico/laboratorial foi estruturado** sobre ela. (No código, o nome interno
do projeto ainda aparece como BioLab.)

---

## 1. Base técnica

### 1.1 Stack
| Camada | Tecnologia |
|---|---|
| Backend | Django + DRF + SimpleJWT + django-filter + drf-spectacular |
| Auth | JWT em cookie HttpOnly + fallback `Authorization: Bearer` |
| Banco | SQLite em dev (`DATABASES` parametrizável por env) |
| Frontend | Next.js (App Router) + TypeScript + Tailwind + lucide-react + axios |
| Documentação API | Swagger UI / ReDoc em `/api/docs/` (somente DEBUG) |

### 1.2 Estrutura de pastas e padrão de apps Django
Cada app segue o mesmo molde:
```
backend/<app>/
  __init__.py
  apps.py
  models.py
  serializers.py
  views.py
  urls.py
  admin.py
  migrations/__init__.py
```

### 1.3 Configuração
- `config/settings.py`: `INSTALLED_APPS` + `MIDDLEWARE` + `REST_FRAMEWORK` + `SIMPLE_JWT` +
  CORS + cookie config + `SPECTACULAR_SETTINGS` + `LOGGING`.
- `config/urls.py`: prefixo `/api/` + Swagger só em DEBUG.
- `accounts/authentication.py`: `CookieJWTAuthentication` — lê o JWT do cookie
  HttpOnly e cai pro header como fallback.

### 1.4 Padrões adotados
- **AbstractUser** customizado, login por email, `username = None`.
- Cookies HttpOnly para o access/refresh token (set/delete em `LoginView` / `LogoutView`).
- `PermissionClass` `IsSupervisorOrReadOnly`: leitura para qualquer usuário autenticado,
  escrita apenas para supervisores.
- Frontend com `AuthProvider` exportando `login/register/logout/refresh` e hidratação
  via `GET /auth/me/` no mount.
- `next.config.js` com `rewrites()` proxiando `/api/*` e `/media/*` para `localhost:8000`.
- Tailwind theme com paleta e tipografia próprias.
- Guard `<AuthGate>` que aguarda `loading=false` e redireciona pro /login.

---

## 2. Como o domínio (químico/laboratorial) foi estruturado

### 2.1 Apps Django

| App | Responsabilidade | Modelos |
|---|---|---|
| `accounts` | Autenticação e perfis de laboratório | `User` (analyst / supervisor) |
| `hazards` | Catálogo canônico de riscos GHS | `Hazard` |
| `substances` | Cadastro de reagentes + propriedades + EPIs + storage | `Substance` |
| `compatibility` | Registros curados + motor de regras + endpoint de check | `CompatibilityRecord` |

### 2.2 Modelagem chave

**`Substance`** — guarda identificação (nome, fórmula, CAS, descrição), propriedades
físicas (estado, pH, massa molar) e — crucialmente — **flags reativos discretos**
(`is_acid`, `is_base`, `is_water`, `is_organic_solvent`). Esses flags existem para que
o motor de regras possa raciocinar deterministicamente sobre o pares.

Conexão M2M com `Hazard` via tabela canônica de códigos estáveis (`flammable`,
`oxidizer`, `reactive_water`, etc.). O motor referencia hazards por `code`, nunca por
PK ou nome — o que torna o seed e as regras estáveis ao longo do tempo.

**`CompatibilityRecord`** — par curado entre duas substâncias. Sempre normalizado
para `substance_a.id < substance_b.id` (via `save()` + `CheckConstraint`), garantindo
no máximo uma linha por par independentemente da ordem em que foi inserido.

### 2.3 Motor de regras (`compatibility/rules.py`)

Coração determinístico do sistema. Diretrizes obedecidas literalmente:
- **Sem IA em runtime.** Decisões são função pura dos atributos da substância.
- **Regras explícitas e separadas.** Cada regra é uma função `(a, b) -> RuleFinding | None`.
- **Simétricas.** Helper `_either(a, b, pred_a, pred_b)` evita repetição de código.
- **Falta de dado = unknown.** Se nenhuma regra dispara e não há registro curado,
  o serviço retorna `unknown` com alerta de risco desconhecido (jamais `safe`).
- **Worst wins.** Consolidação sempre escolhe o pior status e o maior risco — uma
  regra `safe` não pode "abaixar" um `unsafe` de outra regra.

Regras implementadas (ponto de partida — é trivial estender):
| Regra | Disparo | Veredicto típico |
|---|---|---|
| `acid_plus_water` | ácido + água | safe / médio + aviso "ácido na água" |
| `acid_plus_base` | ácido + base (não-água) | unsafe / alto |
| `oxidizer_plus_flammable` | oxidante + inflamável | unsafe / alto |
| `oxidizer_plus_organic` | oxidante + solvente orgânico | unsafe / alto |
| `water_reactive_plus_water` | reativo-água + água | unsafe / alto |
| `toxic_pair_advisory` | ambos tóxicos | unknown / médio (advisory) |
| `corrosive_pair` | ambos corrosivos mesma classe | unknown / médio |

### 2.4 Pipeline do `/api/compatibility/check/`

`compatibility/services.py::check_compatibility(ids)`:
```
1. Carrega substâncias por id (validando que existem)
2. Para cada par C(n,2):
   2a. Busca CompatibilityRecord curado (par normalizado)
   2b. Roda motor de regras → lista de RuleFindings
   2c. Consolida APENAS os layers que firaram (sem misturar default unknown)
   2d. Se nada firou em nenhum layer → unknown + RISK_MEDIUM por política
3. Agrega EPIs e alertas críticos das substâncias envolvidas
4. Consolida overall_status como o pior status entre todos os pares
```

### 2.5 Endpoints

```
POST   /api/auth/register/               criar conta
POST   /api/auth/login/                  login (define cookie HttpOnly)
POST   /api/auth/logout/                 logout (limpa cookie + blacklist refresh)
GET    /api/auth/me/                     perfil do usuário autenticado
PATCH  /api/auth/me/                     atualizar perfil

GET    /api/substances/                  listar (search por nome/fórmula/CAS)
POST   /api/substances/                  criar (supervisor)
GET    /api/substances/{id}/             detalhe completo
PATCH  /api/substances/{id}/             editar (supervisor)
DELETE /api/substances/{id}/             excluir (supervisor)

GET    /api/hazards/                     listar categorias canônicas
POST   /api/hazards/                     criar (supervisor)
GET    /api/hazards/{id}/                detalhe

GET    /api/compatibility/records/       listar registros curados
POST   /api/compatibility/records/       criar (supervisor)
GET    /api/compatibility/records/{id}/  detalhe
POST   /api/compatibility/check/         **motor: receber [ids] e retornar veredicto**
```

### 2.6 Frontend — telas

| Rota | Conteúdo |
|---|---|
| `/` | Landing pública com CTA para login/registro |
| `/login`, `/register` | Auth (JWT cookie) |
| `/dashboard` | Lista pesquisável de substâncias |
| `/substances/[id]` | Detalhe (propriedades, riscos, EPIs, manuseio, armazenamento) |
| `/check` | **Verificador de compatibilidade** — adiciona N substâncias e mostra veredicto + alertas + detalhes por par |
| `/hazards` | Catálogo de categorias de risco |

### 2.7 Dados iniciais (`python manage.py seed_data`)

- **10 categorias de risco** GHS-inspiradas
- **12 substâncias** comuns de laboratório (água, HCl, NaOH, H2SO4, HNO3, etanol,
  acetona, KMnO4, H2O2, NaClO, Na metálico, NH3 aq.)
- **9 registros de compatibilidade** curados cobrindo combinações clássicas
  (HCl + NaClO → Cl2; H2O2 + acetona → TATP; Na + H2O; etc.)

---

## 3. Resumo de qualidade

- **Separação de responsabilidades:** modelos / serializers / views / serviços / regras
  estão em arquivos distintos. Views só fazem orquestração; toda lógica de
  compatibilidade vive em `compatibility/services.py` + `compatibility/rules.py`.
- **Reutilização:** `_either`, `consolidate`, `_evaluate_pair` evitam duplicação ao
  comparar pares; `IsSupervisorOrReadOnly` é a mesma classe nos 3 apps.
- **Extensibilidade:** adicionar uma nova regra é uma função + um item em `RULES`;
  adicionar um novo hazard é um `Hazard.Code` + uma linha no seed.
- **Auditabilidade:** o response do `/check/` retorna `sources` (record / rules /
  fallback) e a lista completa de `findings` (cada regra que disparou, com seu
  `rule_id`), de modo que cada veredicto é totalmente rastreável.
