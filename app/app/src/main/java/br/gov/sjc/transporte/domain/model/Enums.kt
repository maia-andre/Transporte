package br.gov.sjc.transporte.domain.model

/**
 * Shared enum contract — these values MUST stay byte-for-byte identical to the web client
 * (`web/domain`, Python) and the Firestore documents. Treat them as a versioned contract:
 * renaming a value here is a breaking, cross-client change.
 */

enum class Role { SOLICITANTE, MOTORISTA, CONTROLADOR }

enum class StatusViagem { PENDENTE, ACEITA, EM_ANDAMENTO, CONCLUIDA, REJEITADA, CANCELADA }

enum class StatusMotorista { ATIVO, INATIVO }

enum class StatusVeiculo { DISPONIVEL, EM_USO, MANUTENCAO }

enum class Combustivel { GASOLINA, ETANOL, DIESEL, FLEX, ELETRICO, GNV }

/** Human-friendly (pt-BR) labels for the UI. The enum *name* remains the stored contract value. */
val Role.rotulo: String
    get() = when (this) {
        Role.SOLICITANTE -> "Solicitante"
        Role.MOTORISTA -> "Motorista"
        Role.CONTROLADOR -> "Controlador"
    }

val StatusViagem.rotulo: String
    get() = when (this) {
        StatusViagem.PENDENTE -> "Pendente"
        StatusViagem.ACEITA -> "Aceita"
        StatusViagem.EM_ANDAMENTO -> "Em andamento"
        StatusViagem.CONCLUIDA -> "Concluída"
        StatusViagem.REJEITADA -> "Rejeitada"
        StatusViagem.CANCELADA -> "Cancelada"
    }

val StatusMotorista.rotulo: String
    get() = when (this) {
        StatusMotorista.ATIVO -> "Ativo"
        StatusMotorista.INATIVO -> "Inativo"
    }

val StatusVeiculo.rotulo: String
    get() = when (this) {
        StatusVeiculo.DISPONIVEL -> "Disponível"
        StatusVeiculo.EM_USO -> "Em uso"
        StatusVeiculo.MANUTENCAO -> "Manutenção"
    }

val Combustivel.rotulo: String
    get() = when (this) {
        Combustivel.GASOLINA -> "Gasolina"
        Combustivel.ETANOL -> "Etanol"
        Combustivel.DIESEL -> "Diesel"
        Combustivel.FLEX -> "Flex"
        Combustivel.ELETRICO -> "Elétrico"
        Combustivel.GNV -> "GNV"
    }
