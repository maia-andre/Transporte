# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Status:** Greenfield. This document describes the *target* architecture agreed with the
> product owner. Most directories below do not exist yet — create them as work proceeds and
> keep this file in sync as decisions change. Domain terminology is kept in Brazilian
> Portuguese on purpose, because it mirrors the real data model and the city-hall vocabulary.

## Project Overview

**Transporte** is a fleet-scheduling system for a municipal government (*prefeitura*). It
coordinates **drivers (motoristas)** and **vehicles (veículos)** against **trip requests
(requisições de viagem)** raised by city-hall staff.

There are **two clients sharing one backend**:

1. **Web control panel** — Python + **Streamlit**. Used by the **controller (controlador)** to
   register drivers/vehicles and to triage incoming trip requests on a calendar (accept +
   assign driver/vehicle, or reject + justify).
2. **Mobile app** — **Kotlin / Android**. Three roles in one app:
   - **Solicitante** (requester): schedule trips and track the status of their requests.
   - **Motorista** (driver): see where/when they are assigned.
   - **Controlador**: a read-mostly overview of the general status on the go.

The backend is **Firebase** (Firestore + Auth + Cloud Messaging), shared by both clients. The
key product loop: a request created in the app **immediately appears** in the web panel's
calendar; the controller's decision **immediately reflects back** to the requester and driver.

## Architecture

```
  ┌────────────────────┐         ┌───────────────────────────┐
  │  Streamlit panel    │         │   Kotlin / Android app     │
  │  (controlador)      │         │  solicitante/motorista/    │
  │                     │         │  controlador               │
  │  firebase-admin SDK │         │  Firebase client SDK       │
  │  (privileged,       │         │  (constrained by Security  │
  │   service account)  │         │   Rules + auth role)       │
  └─────────┬──────────┘         └─────────────┬─────────────┘
            │                                   │
            └───────────────┬───────────────────┘
                            ▼
              ┌──────────────────────────────┐
              │           Firebase            │
              │  Firestore  ·  Auth  ·  FCM   │
              └──────────────────────────────┘
```

- **The Streamlit panel uses the Firebase Admin SDK** (server-side, service-account
  credentials). It bypasses Security Rules and has full read/write — it is the trusted
  back-office.
- **The Kotlin app uses the Firebase *client* SDK**. Its access is constrained by **Firestore
  Security Rules** keyed on the authenticated `uid` and the user's `role`. Never assume the app
  can do something just because the panel can.
- **Firestore is the single source of truth** and the integration contract between the two
  clients. The data model below is therefore the most important shared artifact in the repo —
  changing a collection/field affects both clients and must be done deliberately.
- **Real-time** updates (panel calendar, app tracking) rely on Firestore listeners. **Push
  notifications** to the app use **FCM** (new request → controllers; decision → requester;
  assignment → driver).

## Repository structure (target monorepo)

```
Transporte/
├── CLAUDE.md
├── README.md
├── web/                     # Streamlit control panel (Python)
│   ├── app.py               # entry point (Home)
│   ├── pages/               # Streamlit multipage (Dashboard, Motoristas, Veículos, Calendário…)
│   ├── services/            # Firebase access layer (firebase_admin init + repositories)
│   ├── domain/              # entities, enums (status), business rules (conflict detection)
│   ├── requirements.txt
│   └── .streamlit/
│       ├── config.toml
│       └── secrets.toml     # service-account creds + config — NOT committed
├── app/                     # Kotlin / Android (Gradle project)
│   └── …                    # google-services.json lives here — NOT committed
├── firebase/                # shared backend definition
│   ├── firebase.json
│   ├── firestore.rules      # access model — the security contract for the app
│   └── firestore.indexes.json
└── docs/
```

Keep the **web** and **app** clients in lockstep against the **firebase** definitions. The
`firebase/` folder (rules + indexes) is the canonical description of how the constrained client
is allowed to touch data.

## Firestore data model

Collections and their key fields. Portuguese field names match the domain.

- **`secretarias/{codigo}`** — doc id **is** the numeric `codigo`. `codigo`, `nome`, `sigla`.
  Seed: `5` = Gabinete do Prefeito (GP), `10` = Secretaria de Governança (SG),
  `15` = Secretaria de Assuntos Jurídicos (SAJ). More are added later by the controller.
- **`usuarios/{uid}`** — mirrors a Firebase Auth user. `nome`, `email`, `role`
  (`SOLICITANTE | MOTORISTA | CONTROLADOR`), `secretariaId`, `fcmTokens[]`.
  Self-signup is **restricted to `@sjc.sp.gov.br`** e-mails and defaults `role = SOLICITANTE`;
  the controller promotes to `MOTORISTA`/`CONTROLADOR` from the panel.
- **`motoristas/{id}`** — `nome`, `matricula`, `cargo`, `secretariaId`, optional `usuarioId`
  (links to the Auth user if the driver uses the app), `status` (`ATIVO | INATIVO`).
  Plus: `telefone`, `cnhNumero`, `cnhCategoria`, `cnhValidade`.
- **`veiculos/{id}`** — `prefixo`, `placa`, `placaPatrimonial`, `marcaModelo`, `secretariaId`,
  `status` (`DISPONIVEL | EM_USO | MANUTENCAO`). Plus: `capacidade` (passengers),
  `combustivel` (`GASOLINA | ETANOL | DIESEL | FLEX | ELETRICO | GNV`), optional `ano`.
- **`viagens/{id}`** — the trip request, the heart of the system:
  - request: `solicitanteId`, `solicitanteNome`, `secretariaId`, `origem`, `destino`,
    `dataHoraSaida`, `dataHoraRetorno`, `numPassageiros`, `finalidade`.
  - decision/assignment: `motoristaId`, `veiculoId`, `decididoPor` (controller uid),
    `decididoEm`, `motivoRejeicao`.
  - lifecycle: `status`, `criadoEm`, `atualizadoEm`.

### Trip lifecycle (state machine)

```
                       ┌──────────► REJEITADA   (requires motivoRejeicao)
   PENDENTE ───────────┤
   (created in app)     └──────────► ACEITA ──► EM_ANDAMENTO ──► CONCLUIDA
                                       │            (driver starts → finishes)
   any non-final state ──► CANCELADA   │
                                       ▼ (assignment set: motoristaId + veiculoId)
```

- **`PENDENTE`** is created by the app (requester). It lands in the panel calendar.
- **`ACEITA`** requires both `motoristaId` and `veiculoId` to be set.
- **`REJEITADA`** requires `motivoRejeicao` (non-empty justification).
- **`EM_ANDAMENTO` / `CONCLUIDA`** are driven by the driver.
- **`CANCELADA`** is requester- or controller-initiated before completion.
- Status is an explicit enum shared by **both** clients — keep the values identical in Python
  (`web/domain`) and Kotlin. Treat the enum as a versioned contract.

### Core business rule — no double-booking

When accepting a request, validate that **neither the chosen driver nor the chosen vehicle has
an overlapping `ACEITA`/`EM_ANDAMENTO` trip** in `[dataHoraSaida, dataHoraRetorno]`. This
conflict check lives in `web/domain` and is the main invariant of the system.

## Access model (roles)

| Role          | Can do                                                                          |
|---------------|---------------------------------------------------------------------------------|
| `SOLICITANTE` | create `viagens`; read/cancel **own**                                            |
| `MOTORISTA`   | read `viagens` where `motoristaId == self`; advance own to `EM_ANDAMENTO`/`CONCLUIDA` |
| `CONTROLADOR` | full read/write on all collections (and is what the Streamlit panel acts as)    |

The Streamlit panel runs as Admin and is effectively always `CONTROLADOR`. The app's actual
permissions must be **enforced in `firestore.rules`**, not just in UI — the UI hiding a button
is not security.

## Authentication

- **Firebase Auth, e-mail/senha.** Self-signup only — but **restricted to the
  `@sjc.sp.gov.br` domain**. Enforce this in a **`beforeUserCreated` blocking Cloud Function**
  (the authoritative check), not just client-side, and require **e-mail verification**.
- New accounts default to `role = SOLICITANTE`. The controller promotes users to
  `MOTORISTA`/`CONTROLADOR` from the panel — this writes `usuarios/{uid}.role` **and** sets a
  matching Auth **custom claim** (via Admin SDK) so `firestore.rules` can read the role.
- Treat the custom claim as the source of truth for rules; the `usuarios` doc is for the UI.

## Visual identity (SJC)

Institutional look of São José dos Campos: **institutional blue** (primary), **gold** (accent),
**a touch of green**. Starting palette (confirm against official brand assets before launch):

| Token       | Hex       | Use                                            |
|-------------|-----------|------------------------------------------------|
| `azul`      | `#0B3C7A` | primary — headers, nav, primary buttons        |
| `azulClaro` | `#1565C0` | links, hover, info                             |
| `dourado`   | `#C8A24B` | accent — highlights, badges, key actions        |
| `verde`     | `#2E7D32` | success/positive (e.g. `ACEITA`, available)     |
| `cinza`     | `#1A2733` | body text · `#F2F5F9` surfaces                   |

- **Web**: set the palette in `web/.streamlit/config.toml` `[theme]` (primaryColor = `azul`),
  with gold/green applied to custom components and status chips.
- **App**: mirror the same tokens in the Android theme (Material color scheme) so both clients
  feel like one product. Keep status colors consistent: green = aceita/concluída, gold =
  pendente/atenção, red = rejeitada/cancelada.

## Development commands

> Greenfield: these are the intended commands once each part is scaffolded.

**Web (Streamlit):**
```bash
cd web
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py                  # serves on http://localhost:8501
```

**Mobile (Kotlin/Android):**
```bash
cd app
./gradlew assembleDebug                # build
./gradlew installDebug                 # install on connected device/emulator
./gradlew test                         # unit tests
./gradlew test --tests "*ViagemTest"   # single test class
```

**Firebase:**
```bash
firebase emulators:start                       # local Firestore/Auth/FCM for dev
firebase deploy --only firestore:rules         # ship security rules
firebase deploy --only firestore:indexes
```

## Conventions & gotchas

- **Secrets stay out of git.** `web/.streamlit/secrets.toml`, the service-account JSON, and
  `app/google-services.json` are credentials — gitignore them and provide
  `*.example` templates instead.
- **Develop against the Firebase emulators** when possible to avoid touching production data
  and to keep the two clients' assumptions honest.
- **Schema changes are cross-client.** A field rename in `viagens` breaks the Kotlin app
  silently. Change the model in `firebase/`, `web/domain`, and the app together, and bump the
  status/enum contract if it moves.
- **Timestamps**: store as Firestore `Timestamp` (UTC); the panel/app convert to local
  (America/Sao_Paulo) for display.
