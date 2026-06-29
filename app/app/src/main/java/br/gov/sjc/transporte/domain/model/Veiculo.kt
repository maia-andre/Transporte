package br.gov.sjc.transporte.domain.model

/**
 * Firestore: `veiculos/{id}`.
 */
data class Veiculo(
    val id: String,
    val prefixo: String,
    val placa: String,
    val placaPatrimonial: String,
    val marcaModelo: String,
    val ano: Int,
    val capacidade: Int,
    val combustivel: Combustivel,
    val secretariaId: Int,
    val status: StatusVeiculo = StatusVeiculo.DISPONIVEL,
)
