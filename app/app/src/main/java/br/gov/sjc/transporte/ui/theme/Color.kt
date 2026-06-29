package br.gov.sjc.transporte.ui.theme

import androidx.compose.ui.graphics.Color
import br.gov.sjc.transporte.domain.model.StatusViagem

// ----- SJC institutional palette (mirror res/values/colors.xml) -----
val Azul = Color(0xFF0B3C7A)        // primary
val AzulClaro = Color(0xFF1565C0)   // links / info / em_andamento
val Dourado = Color(0xFFC8A24B)     // accent / pendente
val Verde = Color(0xFF2E7D32)       // success / concluida
val Vermelho = Color(0xFFC62828)    // error / rejeitada / cancelada
val TextoEscuro = Color(0xFF1A2733) // body text
val Superficie = Color(0xFFF2F5F9)  // secondary surfaces / cards
val Branco = Color(0xFFFFFFFF)

// Soft tints derived from the palette for Material containers.
val AzulContainer = Color(0xFFD6E2F2)
val DouradoContainer = Color(0xFFF3E7C9)
val VerdeContainer = Color(0xFFCDE9CE)
val VermelhoContainer = Color(0xFFF6D6D6)

/**
 * Canonical status -> color mapping. Keep identical to the web client's status chips.
 */
fun corStatusViagem(status: StatusViagem): Color = when (status) {
    StatusViagem.PENDENTE -> Dourado
    StatusViagem.ACEITA -> Azul
    StatusViagem.EM_ANDAMENTO -> AzulClaro
    StatusViagem.CONCLUIDA -> Verde
    StatusViagem.REJEITADA -> Vermelho
    StatusViagem.CANCELADA -> Vermelho
}
