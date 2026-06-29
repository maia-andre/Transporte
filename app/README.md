# App Android — Transporte SJC (Kotlin + Jetpack Compose)

Aplicativo dos três papéis — **solicitante** (agenda e acompanha viagens),
**motorista** (vê sua escala e avança status) e **controlador** (visão geral).
Hoje roda **100% mockado em memória**, com a arquitetura pronta para plugar o
Firebase (mesmo contrato de dados do painel web).

## Como abrir, compilar e rodar (Android Studio)

> ⚠️ O wrapper binário (`gradle/wrapper/gradle-wrapper.jar`) **não** está versionado.
> Abra pelo Android Studio (que provê o Gradle) ou gere o wrapper uma vez via terminal.

1. **Android Studio** (Koala/2024.1+ recomendado) → *Open* → selecione a pasta `app/`.
2. Aguarde o *Gradle sync* (baixa AGP 8.5.2, Kotlin 1.9.24, Compose BOM 2024.06).
3. Rode no emulador/dispositivo (API 24+). App ID: `br.gov.sjc.transporte`.

Gerar o wrapper pelo terminal (se tiver o Gradle instalado), dentro de `app/`:
```bash
gradle wrapper        # cria o gradle-wrapper.jar; depois use ./gradlew ...
./gradlew assembleDebug
./gradlew installDebug
```

## Testando os papéis (login mock)

A tela de login **não verifica senha** (sem backend). Há botões de **acesso rápido**
("Entrar como Solicitante/Motorista/Controlador"). Por e-mail, use um dos semeados
(qualquer senha): `ana.lima@`, `bruno.alves@` (solicitantes), `carlos.souza@`
(motorista), `diana.rocha@` (controlador) — todos `@sjc.sp.gov.br`.

- **Solicitante**: lista suas viagens (cores de status) · "Nova requisição" (cria PENDENTE) · cancelar pendente.
- **Motorista**: viagens atribuídas · iniciar (ACEITA→EM_ANDAMENTO) e concluir (→CONCLUÍDA).
- **Controlador**: visão geral (contagens por status / viagens de hoje). A triagem completa fica no painel web.

## Testes (JVM)

```bash
./gradlew test               # unit tests do MockTransporteRepository / máquina de estados
```
Arquivo: `app/src/test/java/br/gov/sjc/transporte/data/MockTransporteRepositoryTest.kt`.

## Estrutura

```
app/app/src/main/java/br/gov/sjc/transporte/
├── domain/model/      # entidades + enums (contrato compartilhado com o web)
├── data/              # TransporteRepository (interface) + Mock + Firebase (skeleton)
│                      #   + RepositoryProvider (switch point) + SeedData
├── auth/              # SessionManager (sessão mock)
├── ui/                # theme (cores SJC) · login · solicitante · motorista · controlador · navigation
└── util/              # DataHora (formatação)
```

## Ponto de troca para Firebase (switch point)

Toda a UI depende só da interface `TransporteRepository`. Para ir ao ar:

1. Habilite as dependências Firebase (comentadas) em `app/build.gradle.kts` e aplique
   o plugin `google-services`; adicione `google-services.json` em `app/app/`.
2. Implemente os corpos `// TODO` de `data/FirebaseTransporteRepository.kt` (Firestore/Auth).
3. Em `data/RepositoryProvider.kt`, troque **a única linha**:
   `MockTransporteRepository()` → `FirebaseTransporteRepository()`.

Nada mais na UI muda. Os enums em `domain/model/Enums.kt` são **contrato**: mantenha
idênticos aos do web (`web/domain`) e do Firestore.

## ⚠️ Status / não verificado aqui

Este projeto foi escrito sem um ambiente Android/Gradle disponível, então **não foi
compilado nem executado** aqui. O código é idiomático e consistente, mas ao abrir no
Android Studio podem surgir ajustes de versão. Suposições de versão: AGP 8.5.2,
Kotlin 1.9.24, Compose Compiler 1.5.14, Compose BOM 2024.06.00, Navigation 2.7.7,
JDK 17. `google-services.json` e `local.properties` não são versionados.
