# Painel Web — Transporte SJC (Streamlit)

Painel de controle do controlador: cadastros de motoristas/veículos/secretarias,
gestão de papéis e o **calendário de requisições** (aceitar+escalar / rejeitar).
Hoje roda com **dados mockados em memória**; a troca para Firebase é um único ponto.

## Como rodar (Linux/Debian — use venv!)

> No Debian o Python do sistema é gerenciado; **sempre** use um virtualenv para não
> colidir com os pacotes do SO.

```bash
cd web
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py            # abre em http://localhost:8501
```

Sem ativar o venv, prefixe os comandos: `.venv/bin/streamlit run app.py`.

## Testes

```bash
cd web
.venv/bin/python -m pytest        # unitários + integração + smoke da UI (AppTest)
.venv/bin/python -m pytest tests/test_rules.py            # um arquivo
.venv/bin/python -m pytest -k conflito                    # por palavra-chave
```

- `tests/test_models.py` — mapeamento entidade ⇄ documento (pronto p/ Firestore).
- `tests/test_rules.py` — conflito de escala e máquina de estados.
- `tests/test_mock_repository.py` — fluxo do controlador ponta a ponta.
- `tests/test_app_smoke.py` — roda o app real e cada página headless (`AppTest`).

## Estrutura

```
web/
├── app.py                  # Dashboard (entry point)
├── pages/                  # Calendário, Motoristas, Veículos, Secretarias, Usuários
├── domain/                 # entidades, enums (contrato), regras (conflito + estados)
├── services/               # Repository (interface) + Mock + Firebase (skeleton) + factory
├── components/theme.py     # identidade visual SJC + helpers de UI
├── tests/
└── .streamlit/
    ├── config.toml         # tema SJC
    └── secrets.toml.example # modelo de credenciais (copie p/ secrets.toml)
```

## Conectar ao Firebase (depois)

A camada de dados é abstraída em `services/Repository`. Para ligar o Firestore:

1. `pip install -r requirements.txt` (já inclui `firebase-admin`).
2. Copie `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` e cole as
   credenciais do service account na seção `[firebase]`.
3. Defina `data_source = "firebase"` em `secrets.toml`.

`services/get_repository()` passa a devolver `FirebaseRepository` automaticamente —
**nenhuma página muda**. Revise os `# TODO` em `services/firebase_repository.py` ao
validar contra um projeto real (índices, regras de segurança, custom claims).

> `secrets.toml` e o JSON do service account **não** são versionados (`.gitignore`).
