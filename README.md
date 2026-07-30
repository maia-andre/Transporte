<div align="center">

# 🚐 Transporte SJC

### Gestão de escala de motoristas e veículos da Prefeitura

Painel web de controle **+** app móvel, sobre um backend único no Firebase.

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-0B3C7A?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-C8A24B?style=for-the-badge&logo=streamlit&logoColor=white)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9-0B3C7A?style=for-the-badge&logo=kotlin&logoColor=white)
![Jetpack Compose](https://img.shields.io/badge/Jetpack%20Compose-M3-C8A24B?style=for-the-badge&logo=jetpackcompose&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Firestore%20·%20Auth%20·%20FCM-0B3C7A?style=for-the-badge&logo=firebase&logoColor=white)
![Android](https://img.shields.io/badge/Android-API%2024+-2E7D32?style=for-the-badge&logo=android&logoColor=white)

![Testes](https://img.shields.io/badge/testes-28%20passando-2E7D32?style=for-the-badge&logo=pytest&logoColor=white)
![Status](https://img.shields.io/badge/status-MVP%20mockado-2E7D32?style=for-the-badge)
![Backend](https://img.shields.io/badge/Firebase-pronto%20p/%20conectar-C8A24B?style=for-the-badge)
![Licença](https://img.shields.io/badge/licença-a%20definir-lightgrey?style=for-the-badge)

</div>

---

## 📖 Sobre

O **Transporte SJC** centraliza o pedido, a aprovação e a escala de viagens da frota
municipal. Um servidor pede uma viagem pelo **app**; a requisição entra **em tempo real** no
**calendário do painel web**; o **controlador** aceita (atribuindo motorista e veículo) ou
rejeita com justificativa; a decisão volta na hora para quem pediu e para o motorista escalado.

> 🧭 O acompanhamento e a ampliação do projeto são feitos pelo **[`docs/PLANO.md`](./docs/PLANO.md)**
> (superplano por fases). Arquitetura e modelo de dados detalhados no **[`CLAUDE.md`](./CLAUDE.md)**.

## 🏗️ Arquitetura

```mermaid
flowchart TB
    subgraph CLIENTES[" "]
        direction LR
        WEB["🖥️ Painel Web<br/><b>Streamlit</b> · controlador<br/><i>Admin SDK (acesso total)</i>"]
        APP["📱 App Android<br/><b>Kotlin + Compose</b><br/>solicitante · motorista · controlador<br/><i>SDK cliente (restrito por regras)</i>"]
    end

    subgraph FIREBASE["☁️ Firebase — backend compartilhado"]
        direction LR
        FS[("🔥 Firestore<br/>fonte única da verdade")]
        AUTH["🔐 Auth<br/>e-mail @sjc.sp.gov.br"]
        FCM["🔔 Cloud Messaging<br/>notificações push"]
    end

    WEB <-->|"CRUD + triagem"| FS
    APP <-->|"requisita + acompanha"| FS
    WEB --- AUTH
    APP --- AUTH
    FCM -. avisa .-> APP

    classDef blue fill:#0B3C7A,stroke:#06294f,color:#fff;
    classDef gold fill:#C8A24B,stroke:#9c7d36,color:#1A2733;
    classDef green fill:#2E7D32,stroke:#1f5a23,color:#fff;
    class WEB,APP blue;
    class FS,AUTH gold;
    class FCM green;
```

A UI de cada cliente fala **apenas com uma interface de repositório** — hoje implementada com
dados mockados, e com a troca para o Firebase concentrada em **um único ponto** por cliente.

## 🔁 Ciclo de vida de uma viagem

```mermaid
stateDiagram-v2
    [*] --> PENDENTE: solicitante cria (app)
    PENDENTE --> ACEITA: controlador escala motorista + veículo
    PENDENTE --> REJEITADA: justificativa obrigatória
    PENDENTE --> CANCELADA: cancelada
    ACEITA --> EM_ANDAMENTO: motorista inicia
    ACEITA --> CANCELADA: cancelada
    EM_ANDAMENTO --> CONCLUIDA: motorista conclui
    REJEITADA --> [*]
    CONCLUIDA --> [*]
    CANCELADA --> [*]
```

> 🛡️ **Invariante central:** ao aceitar, o sistema bloqueia **conflito de agenda** — um motorista
> ou veículo não pode estar escalado em duas viagens que se sobreponham no tempo.

## ✨ Funcionalidades

O **painel web** agora tem **login com dois papéis** — auto-cadastro é livre e sempre
vira solicitante; controlador só promove quem já tem conta (autenticação local por
enquanto, sem Firebase — ver [`web/README.md`](./web/README.md)).

| 🖥️ Painel Web — Controlador | 🖥️ Painel Web — Solicitante | 📱 App (solicitante / motorista / controlador) |
|---|---|---|
| Cadastro de **motoristas** (nome, matrícula, cargo, secretaria, telefone, CNH) | Criar **nova requisição** de viagem | **Solicitante:** criar requisição e acompanhar status |
| Cadastro de **veículos** (prefixo, placa, **placa patrimonial**, modelo, ano, capacidade, combustível) | Acompanhar **minhas requisições** e cancelar (antes de em andamento) | **Motorista:** ver escala · iniciar e concluir viagem |
| Cadastro de **secretarias** e gestão de **papéis** | | **Controlador:** visão geral (status do dia) |
| **Calendário/triagem:** aceitar e escalar · rejeitar e justificar | | Login institucional `@sjc.sp.gov.br` |
| Checagem de **conflito de agenda** | | Cores de status consistentes com o painel |

## 🧱 Stack

- **Painel web:** Python + **Streamlit** · `firebase-admin` (Admin SDK)
- **App:** **Kotlin** + Jetpack Compose (Material 3), MVVM
- **Backend:** **Firebase** — Firestore (dados), Auth (e-mail/senha restrito a `@sjc.sp.gov.br`), Cloud Messaging (push)

## 🗂️ Estrutura

```
Transporte/
├── web/        # Painel Streamlit (domínio + Repository Mock/Firebase + páginas + testes)
├── app/        # App Android Kotlin/Compose (mesmo contrato + Mock/Firebase + testes)
├── firebase/   # (próx. fase) regras, índices, config
├── docs/
│   └── PLANO.md   # superplano / acompanhamento por fases
├── CLAUDE.md   # arquitetura e modelo de dados
└── README.md
```

## 🚀 Como rodar

**Painel web** (Linux/Debian — use venv!). Mais em [`web/README.md`](./web/README.md):

```bash
cd web
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py            # http://localhost:8501
.venv/bin/python -m pytest      # 28 testes (unit + integração + smoke de UI)
```

**App Android** — abra a pasta `app/` no Android Studio e rode no emulador (API 24+).
Login mock com botões de acesso por papel. Mais em [`app/README.md`](./app/README.md):

```bash
cd app
./gradlew test                  # unit tests (JVM)
./gradlew installDebug          # requer gradle-wrapper (ver app/README.md)
```

**Backend local (quando o Firebase entrar):** `firebase emulators:start`

## 🗺️ Roadmap

- [~] **Fase 0 — Fundação:** monorepo, contrato de dados e tema SJC ✅; projeto Firebase + regras + emuladores pendentes
- [x] **Fase 1 — Painel web (MVP):** login (dois papéis, auth local) + cadastros e papéis *(mock)*
- [x] **Fase 2 — Calendário:** triagem com checagem de conflito *(mock, com testes)*
- [~] **Fase 3 — Solicitante:** criar requisição e acompanhar, hoje **no app e no painel** *(mock)*; auto-cadastro `@sjc.sp.gov.br` + verificação de e-mail pendem do Firebase
- [x] **Fase 4 — App (motorista/controlador):** escala, avançar status, visão geral *(mock)*
- [ ] **Fase 5 — Notificações (FCM) + relatórios**
- [ ] **Fase 6 — Hardening + piloto**

> **Estado atual:** painel web e app **funcionais para teste com dados mockados**, prontos para
> ligar o Firebase (ponto de troca único em cada cliente).

## 🎨 Identidade visual (SJC)

<div align="center">

![Azul institucional](https://img.shields.io/badge/Azul%20institucional-%230B3C7A-0B3C7A?style=flat-square)
![Dourado](https://img.shields.io/badge/Dourado-%23C8A24B-C8A24B?style=flat-square)
![Verde](https://img.shields.io/badge/Verde-%232E7D32-2E7D32?style=flat-square)

</div>

Azul institucional (primária), dourado (destaque) e verde (positivo), aplicados igualmente nos
dois clientes. *Paleta a confirmar com o manual de marca oficial antes do piloto.*

---

<div align="center">
🏛️ Projeto para a <b>Prefeitura de São José dos Campos</b> · feito com Streamlit, Kotlin e Firebase
</div>
