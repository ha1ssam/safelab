# BioLab — Consulta de Substâncias e Compatibilidade Química

Sistema acadêmico (Biomedicina) para auxiliar profissionais de laboratório a consultar
informações sobre substâncias químicas e verificar compatibilidades entre elas, com foco
em segurança.

> **Aviso:** Sistema educacional e de apoio. Não substitui normas oficiais (NR, FISPQ, GHS, etc.).

## Stack

- **Backend:** Django 6 + DRF + SimpleJWT (cookie-based) + django-filter + drf-spectacular
- **Frontend:** Next.js 13 (App Router) + TypeScript + Tailwind CSS + lucide-react + axios
- **Banco:** SQLite em desenvolvimento

## Estrutura

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

## Como rodar

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata initial_data
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Diretrizes críticas

- **Sem IA em runtime.** Toda lógica é determinística, baseada em dados e regras.
- **Nunca assumir segurança.** Falta de dado → resposta `unknown` com alerta de risco.
- **Regras explícitas e separadas** do CRUD, fáceis de expandir.
