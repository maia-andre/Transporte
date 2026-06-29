package br.gov.sjc.transporte.domain.model

import java.time.LocalDate

/**
 * Firestore: `motoristas/{id}`. [usuarioId] links to the Auth user when the driver uses the app.
 */
data class Motorista(
    val id: String,
    val nome: String,
    val matricula: String,
    val cargo: String,
    val secretariaId: Int,
    val telefone: String,
    val cnhNumero: String,
    val cnhCategoria: String,
    val cnhValidade: LocalDate,
    val usuarioId: String? = null,
    val status: StatusMotorista = StatusMotorista.ATIVO,
)
