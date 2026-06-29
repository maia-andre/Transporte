# 🎯 Superplano — Transporte SJC

> Plano-mestre do projeto: do painel web ao app, fase a fase, com identidade visual,
> modelo de dados final, segurança e critérios de "pronto". É o **/goal da sessão** e o
> documento de referência para "botar a mão na massa". Termos de domínio em português;
> trechos técnicos misturam inglês onde é o padrão (Firebase/Streamlit/Android).

---

## 0. Como usar este plano

- Cada **fase** tem: *objetivo*, *entregáveis*, *pronto quando* (critério de aceite) e
  *dependências*. Atacar em ordem; cada fase deixa algo demonstrável.
- O **contrato compartilhado** (modelo de dados + enums + regras) é o que mantém painel e app
  em sincronia — mudou aqui, muda nos dois clientes.

---

## 1. Decisões travadas

| Tema | Decisão |
|------|---------|
| **Auth** | Firebase Auth e-mail/senha · auto-cadastro **restrito a `@sjc.sp.gov.br`** · e-mail verificado · novo usuário = `SOLICITANTE`; controlador promove |
| **Secretarias** | Coleção própria, id = código. Seed: `5` Gabinete do Prefeito · `10` Sec. de Governança · `15` Sec. de Assuntos Jurídicos |
| **Motorista** | + `telefone`, `cnhNumero`, `cnhCategoria`, `cnhValidade` |
| **Veículo** | + `placaPatrimonial`, `capacidade`, `combustivel`, `ano` |
| **Identidade** | Azul institucional (primária), dourado (destaque), verde (toque) |
| **Stack** | Python + Streamlit (web) · Kotlin/Android (app) · Firebase (Firestore/Auth/FCM) |

---

## 2. Identidade visual (design system)

Paleta inicial (confirmar com manual de marca oficial de SJC antes do piloto):

| Token | Hex | Uso |
|-------|-----|-----|
| `azul` | `#0B3C7A` | primária: cabeçalhos, navegação, botões primários |
| `azulClaro` | `#1565C0` | links, hover, informações |
| `dourado` | `#C8A24B` | destaque: badges, realces, ações-chave |
| `verde` | `#2E7D32` | sucesso/positivo (aceita, disponível, concluída) |
| `vermelho` | `#C62828` | erro/negativo (rejeitada, cancelada) |
| `textoEscuro` | `#1A2733` | texto |
| `superficie` | `#F2F5F9` | fundos secundários, cards |

**Cores de status (iguais nos dois clientes):**

| Status viagem | Cor |
|---------------|-----|
| `PENDENTE` | dourado |
| `ACEITA` | azul |
| `EM_ANDAMENTO` | azulClaro |
| `CONCLUIDA` | verde |
| `REJEITADA` / `CANCELADA` | vermelho |

**Web — `web/.streamlit/config.toml`:**
```toml
[theme]
primaryColor = "#0B3C7A"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F2F5F9"
textColor = "#1A2733"
font = "sans serif"
```
Dourado/verde entram via CSS de componentes e chips de status. Cabeçalho com brasão/nome da
prefeitura. Logo e favicon em `web/assets/`.

**App — Android (Material 3):** mesmos tokens no `colorScheme` (primary = azul,
secondary/tertiary = dourado/verde). Componentes Material + chips de status reaproveitando o
mapa de cores acima.

---

## 3. Modelo de dados final (Firestore)

> Coleção é o **contrato de integração**. Datas como `Timestamp` (UTC); exibir em
> America/Sao_Paulo.

```
secretarias/{codigo}
  codigo:int  nome:str  sigla:str

usuarios/{uid}                       # espelha o Auth user
  nome  email  role(SOLICITANTE|MOTORISTA|CONTROLADOR)
  secretariaId  fcmTokens[]  criadoEm

motoristas/{id}
  nome  matricula  cargo  secretariaId
  telefone  cnhNumero  cnhCategoria  cnhValidade
  usuarioId?(link Auth)  status(ATIVO|INATIVO)

veiculos/{id}
  prefixo  placa  placaPatrimonial  marcaModelo  ano
  capacidade:int  combustivel(GASOLINA|ETANOL|DIESEL|FLEX|ELETRICO|GNV)
  secretariaId  status(DISPONIVEL|EM_USO|MANUTENCAO)

viagens/{id}                         # núcleo do sistema
  # solicitação
  solicitanteId  solicitanteNome  secretariaId
  origem  destino  dataHoraSaida  dataHoraRetorno
  numPassageiros  finalidade
  # decisão / escala
  status  motoristaId?  veiculoId?
  decididoPor?  decididoEm?  motivoRejeicao?
  # auditoria
  criadoEm  atualizadoEm
```

**Máquina de estados da viagem:**
```
PENDENTE ─┬─► ACEITA(motoristaId+veiculoId) ─► EM_ANDAMENTO ─► CONCLUIDA
          ├─► REJEITADA (exige motivoRejeicao)
          └─► CANCELADA            (qualquer estado não-final)
```

**Enums = contrato versionado.** Valores idênticos em `web/domain` (Python) e no app (Kotlin).

**Índices prováveis** (`firestore.indexes.json`): `viagens` por `status`+`dataHoraSaida`;
por `solicitanteId`+`criadoEm`; por `motoristaId`+`dataHoraSaida`.

---

## 4. Segurança & papéis

**Camadas:**
1. **Blocking Function `beforeUserCreated`** — rejeita e-mail fora de `@sjc.sp.gov.br`.
2. **Custom claim `role`** — definido pelo painel (Admin SDK) ao promover usuário; é a fonte da
   verdade para as regras. `usuarios/{uid}.role` é espelho para a UI.
3. **`firestore.rules`** — fronteira real do app cliente:

| Coleção | SOLICITANTE | MOTORISTA | CONTROLADOR |
|---------|-------------|-----------|-------------|
| `viagens` | cria; lê/cancela **as próprias** | lê onde `motoristaId==self`; avança status da própria | total |
| `motoristas`/`veiculos`/`secretarias` | leitura | leitura | total |
| `usuarios` | o próprio doc | o próprio doc | total |

O painel Streamlit usa **Admin SDK** → ignora as regras (back-office confiável). UI escondendo
botão **não é** segurança — a regra é.

---

## 5. Arquitetura técnica (detalhes)

- **Web (`web/`)**: Streamlit multipage (`app.py` + `pages/`). Camadas: `services/` (init
  `firebase_admin`, repositórios por coleção), `domain/` (entidades, enums, regra de conflito),
  `assets/`. Credenciais via `.streamlit/secrets.toml` (service account) — fora do git.
- **App (`app/`)**: Kotlin/Android, MVVM. Firebase client SDK (Firestore listeners, Auth, FCM).
  `google-services.json` fora do git. Navegação por papel após login.
- **Backend (`firebase/`)**: `firestore.rules`, `firestore.indexes.json`, `firebase.json`,
  Cloud Functions (blocking auth + disparo de notificações).
- **Regra anti-conflito** (em `web/domain`, aplicada ao aceitar): bloquear se o motorista **ou**
  o veículo escolhido tiver viagem `ACEITA`/`EM_ANDAMENTO` sobrepondo `[dataHoraSaida,
  dataHoraRetorno]`.
- **Notificações (FCM)** via Cloud Functions on-write em `viagens`: nova `PENDENTE` →
  controladores; decisão (`ACEITA`/`REJEITADA`) → solicitante; escala → motorista.
- **Dev local**: Firebase Emulators (Firestore/Auth/Functions) para não tocar produção.

---

## 6. Roadmap em fases

> **Estado atual (2026-06-28)** — entrega "funcional para testes, com dados mockados,
> pronto para Firebase":
> - 🟡 **Fase 0** — estrutura do monorepo, contrato de dados e tema SJC prontos;
>   projeto Firebase / regras / emuladores ainda pendentes.
> - ✅ **Fase 1** — painel web: CRUD de motoristas (com CNH), veículos (com placa
>   patrimonial/combustível/capacidade/ano), secretarias e usuários/papéis. Mockado.
> - ✅ **Fase 2** — painel web: calendário/agenda, aceitar+escalar com checagem de
>   conflito, rejeitar com justificativa, simular requisição. Mockado e com testes.
> - ✅ **Fases 3–4** — app Kotlin (solicitante/motorista/controlador) entregue: mockado,
>   pronto para Firebase, com testes JVM (`./gradlew test`). Compilação/execução no Android
>   Studio ainda a validar (sem SDK Android no ambiente de build).
> - ⬜ **Fases 5–6** — dependem do Firebase real.
>
> Camada de dados abstraída (`Repository`): a troca Mock → Firebase é um único ponto
> (`web/services/get_repository`). Testes web: `cd web && .venv/bin/python -m pytest`.

### Fase 0 — Fundação 🧱
**Objetivo:** projeto Firebase de pé e contrato de dados materializado.
**Entregáveis:** projeto Firebase criado · monorepo `web/ app/ firebase/ docs/` · `.gitignore` +
templates `*.example` de segredos · `firestore.rules` v1 + índices · seed das 3 secretarias ·
tema `config.toml` + assets de marca · emuladores rodando.
**Pronto quando:** `firebase emulators:start` sobe; seed visível; regras carregam.

### Fase 1 — Painel: login + cadastros 🗂️
**Objetivo:** controlador entra e gerencia frota.
**Entregáveis:** login (Admin/controlador) com tema SJC · CRUD **motoristas** (com CNH) · CRUD
**veículos** (com placa patrimonial, combustível, capacidade, ano) · CRUD **secretarias** ·
gestão de **usuários/papéis** (promover SOLICITANTE→MOTORISTA/CONTROLADOR, setar custom claim).
**Pronto quando:** dá pra cadastrar/editar/inativar motoristas e veículos e promover um usuário.
**Depende:** Fase 0.

### Fase 2 — Painel: calendário + triagem ⚖️
**Objetivo:** o loop central de aprovação.
**Entregáveis:** **calendário** de requisições por dia/semana com cores de status · detalhe da
viagem · **aceitar** (atribuir motorista+veículo com **checagem de conflito**) · **rejeitar**
(justificativa obrigatória) · filtros (secretaria/status/período).
**Pronto quando:** uma `PENDENTE` (semeada/manual) é aceita com escala sem conflito, ou rejeitada
com justificativa, e o status muda.
**Depende:** Fase 1.

### Fase 3 — App: solicitante 📱
**Objetivo:** fechar o ciclo ponta-a-ponta.
**Entregáveis:** auto-cadastro `@sjc.sp.gov.br` + verificação de e-mail · escolha de secretaria ·
**nova requisição** de viagem · **lista/acompanhamento** dos próprios pedidos em tempo real ·
cancelar pendente · tema SJC.
**Pronto quando:** requisição criada no app aparece no calendário do painel; decisão do painel
reflete no app.
**Depende:** Fase 2.

### Fase 4 — App: motorista + controlador 🚗
**Objetivo:** demais papéis no app.
**Entregáveis:** **motorista** vê suas escalas e avança `EM_ANDAMENTO`→`CONCLUIDA` ·
**controlador** com visão geral (status do dia) read-mostly.
**Pronto quando:** motorista vê viagem atribuída e a conclui; mudança reflete no painel.
**Depende:** Fase 3.

### Fase 5 — Notificações + relatórios 🔔
**Entregáveis:** FCM (nova requisição→controlador; decisão→solicitante; escala→motorista) ·
relatórios/exportações no painel (viagens por período/secretaria/motorista/veículo, KM se houver).
**Depende:** Fases 2–4.

### Fase 6 — Hardening + piloto 🚀
**Entregáveis:** revisão das regras de segurança · validação da paleta com manual de marca ·
testes (regra de conflito, máquina de estados) · deploy (Streamlit hospedado + regras/functions)
· piloto com 1 secretaria.
**Depende:** todas.

---

## 7. Sequenciamento

```
Fase 0 ─► Fase 1 ─► Fase 2 ─► Fase 3 ─► Fase 4 ─► Fase 5 ─► Fase 6
                       (painel pronto)   (app pronto)  (avisos)  (piloto)
```
Caminho crítico: 0→1→2 entrega o **painel utilizável**; 3→4 entrega o **app**; 5 enriquece; 6
endurece. Notificações (5) podem começar em paralelo assim que 2 estabilizar.

---

## 8. Riscos & mitigações

| Risco | Mitigação |
|-------|-----------|
| Mudança de schema quebra o app silenciosamente | tratar enums/coleções como contrato versionado; mudar `firebase/`+web+app juntos |
| Restrição de domínio burlável no cliente | impor via blocking function no servidor |
| Double-booking | regra de conflito server-trusted no aceite + índices |
| Cores fora do padrão oficial | validar paleta com manual de marca na Fase 6 |
| Hospedagem do Streamlit p/ órgão público | definir hosting cedo (Fase 6) |

---

## 9. Próximo passo imediato

Painel web e app (mockados) entregues para teste. Próximos passos, em ordem:

1. **Validar o app no Android Studio** (abrir `app/`, sincronizar Gradle, rodar no emulador).
2. **Fechar a Fase 0 do Firebase**: criar o projeto, `firestore.rules` v1 + índices, seed das
   secretarias, e subir os emuladores.
3. **Ligar o backend**: preencher `web/.streamlit/secrets.toml`, `data_source = "firebase"`,
   revisar os `# TODO` de `firebase_repository.py`; plugar o mesmo no app (switch point documentado).
4. **Fase 5** — notificações (FCM) e relatórios. **Fase 6** — hardening + piloto.
