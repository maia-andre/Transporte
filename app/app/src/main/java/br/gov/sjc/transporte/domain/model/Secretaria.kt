package br.gov.sjc.transporte.domain.model

/**
 * Firestore: `secretarias/{codigo}` — the document id IS the numeric [codigo].
 */
data class Secretaria(
    val codigo: Int,
    val nome: String,
    val sigla: String,
)
