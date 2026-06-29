package br.gov.sjc.transporte.domain.model

import java.time.LocalDateTime

/**
 * Firestore: `viagens/{id}` — the heart of the system (trip request + decision + audit).
 *
 * State machine:
 * ```
 * PENDENTE ─┬─► ACEITA (motoristaId + veiculoId) ─► EM_ANDAMENTO ─► CONCLUIDA
 *           ├─► REJEITADA (exige motivoRejeicao)
 *           └─► CANCELADA (qualquer estado não-final)
 * ```
 *
 * Date fields use [LocalDateTime] consistently across the app. In Firestore these map to
 * `Timestamp` (UTC) — convert at the repository boundary (see FirebaseTransporteRepository).
 */
data class Viagem(
    val id: String,
    // --- request ---
    val solicitanteId: String,
    val solicitanteNome: String,
    val secretariaId: Int,
    val origem: String,
    val destino: String,
    val dataHoraSaida: LocalDateTime,
    val dataHoraRetorno: LocalDateTime,
    val numPassageiros: Int,
    val finalidade: String,
    // --- decision / assignment ---
    val status: StatusViagem = StatusViagem.PENDENTE,
    val motoristaId: String? = null,
    val veiculoId: String? = null,
    val decididoPor: String? = null,
    val decididoEm: LocalDateTime? = null,
    val motivoRejeicao: String? = null,
    // --- audit ---
    val criadoEm: LocalDateTime,
    val atualizadoEm: LocalDateTime,
)
