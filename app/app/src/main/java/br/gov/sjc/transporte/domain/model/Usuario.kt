package br.gov.sjc.transporte.domain.model

/**
 * Firestore: `usuarios/{uid}` — mirrors a Firebase Auth user.
 * Self-signup is restricted to `@sjc.sp.gov.br` and defaults to [Role.SOLICITANTE];
 * the controller promotes roles from the web panel.
 */
data class Usuario(
    val uid: String,
    val nome: String,
    val email: String,
    val role: Role,
    val secretariaId: Int,
    val fcmTokens: List<String> = emptyList(),
)
