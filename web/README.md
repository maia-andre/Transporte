# Painel Web — Transporte SJC (Streamlit)

Painel com **login e dois papéis**: **controlador** (cadastros de
motoristas/veículos/secretarias, gestão de papéis e o **calendário de requisições** —
aceitar+escalar / rejeitar) e **solicitante** (criar e acompanhar/cancelar as próprias
requisições, sem precisar do app). Auto-cadastro é livre e sempre vira solicitante; o
papel de controlador só é concedido por um controlador já existente (tela Usuários).
Hoje roda com **dados mockados em memória** e autenticação local (sem Firebase ainda);
a troca para Firebase é um único ponto — ver `services/get_repository`.

## Login (demonstração)

Sem Firebase, o login usa e-mail/senha guardados no próprio mock store (hash
PBKDF2-HMAC-SHA256, `domain/auth.py`). Contas semeadas (`services/mock_data.py`), todas
com a senha `transporte123`:

| E-mail | Papel |
|---|---|
| `ana.controle@sjc.sp.gov.br` | Controlador |
| `carlos.silva@sjc.sp.gov.br` | Solicitante |
| `beatriz.souza@sjc.sp.gov.br` | Solicitante |
| `joao.motorista@sjc.sp.gov.br` | Motorista *(sem tela própria no painel ainda — ver CLAUDE.md)* |

Pela aba "Criar conta" também dá pra se auto-cadastrar como solicitante (sem
restrição de e-mail por enquanto — isso volta quando o Firebase Auth entrar).

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
- `tests/test_auth.py` — hash de senha e login/cadastro no `MockRepository`.
- `tests/test_app_smoke.py` — roda o app real headless (`AppTest`): login, cadastro e
  controle de acesso por papel em cada página.

## Estrutura

```
web/
├── app.py                  # roteador: login gate + st.navigation por papel
├── pages/                  # 0 Dashboard, 1 Calendário, 2-5 cadastros (controlador)
│                           # 6 Nova Requisição, 7 Minhas Requisições (solicitante)
├── domain/                 # entidades, enums (contrato), regras (conflito + estados),
│                           # auth.py (hash de senha, independente de backend)
├── services/               # Repository (interface) + Mock + Firebase (skeleton) + factory
├── components/
│   ├── theme.py            # identidade visual SJC + helpers de UI + sidebar
│   ├── auth.py              # sessão do usuário logado + exigir_papel (por página)
│   └── login.py             # tela de login + auto-cadastro
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
