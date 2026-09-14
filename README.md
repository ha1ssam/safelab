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
│   ├── compatibility/      # registros + motor de regras determinístico
│   └── fispq/              # dados de FISPQ/GHS + importação do PubChem
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
python manage.py seed_data                   # dados iniciais: riscos, substâncias e compatibilidades
# python manage.py import_pubchem --catalog  # (opcional) importa o catálogo de reagentes do PubChem (requer internet)
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

- `node_modules`, `.next`, `venv`, arquivos `.env` e o banco `db.sqlite3` não são versionados (veja `.gitignore`).
- O banco SQLite é apenas para desenvolvimento local: cada pessoa gera o seu com `migrate` + `seed_data`.
- Para produção, configure um banco de dados adequado e as variáveis de `backend/.env.example` — em especial `DJANGO_DEBUG=False` e uma `DJANGO_SECRET_KEY` secreta (o backend não inicia com a chave de desenvolvimento).

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
