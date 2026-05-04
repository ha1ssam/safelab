# SafeLab — Consulta de Substâncias e Compatibilidade Química


Sistema acadêmico para auxiliar profissionais de laboratório a consultar informações sobre substâncias químicas e verificar compatibilidades entre elas, com foco em segurança.


> **Aviso:** Sistema educacional e de apoio. Não substitui normas oficiais (NR, FISPQ, GHS, etc.).

Repositório: https://github.com/ha1ssam/safelab.git

## Stack

- **Backend:** Django 6 + DRF + SimpleJWT (cookie-based) + django-filter + drf-spectacular
- **Frontend:** Next.js 13 (App Router) + TypeScript + Tailwind CSS + lucide-react + axios
- **Banco:** SQLite (apenas para desenvolvimento)

## Estrutura de Pastas

```
.
├── backend/
│   ├── config/             # settings, urls, wsgi, asgi
│   ├── accounts/           # autenticação JWT por cookie
│   ├── substances/         # cadastro de substâncias
│   ├── hazards/            # riscos (GHS) associados
│   └── compatibility/      # registros + motor de regras determinístico
└── frontend/
    └── src/
        ├── app/            # rotas (Next.js App Router)
        ├── components/     # UI reutilizável
        └── lib/            # api, auth, types
```

## Como rodar o projeto

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
# (Opcional) Carregar dados iniciais, se disponível
# python manage.py loaddata initial_data
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Observações importantes

- O diretório `node_modules` não é versionado (veja `.gitignore`).
- O banco `db.sqlite3` é apenas para desenvolvimento local.
- Para produção, configure um banco de dados adequado e variáveis de ambiente.
