package br.gov.sjc.transporte.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

/**
 * SJC Material 3 theme. Brand consistency is intentional, so dynamic color is NOT used.
 * A single light scheme is provided (a dark scheme can be added later if needed).
 */
private val SjcLightColors = lightColorScheme(
    primary = Azul,
    onPrimary = Branco,
    primaryContainer = AzulContainer,
    onPrimaryContainer = Azul,

    secondary = Dourado,
    onSecondary = TextoEscuro,
    secondaryContainer = DouradoContainer,
    onSecondaryContainer = TextoEscuro,

    tertiary = Verde,
    onTertiary = Branco,
    tertiaryContainer = VerdeContainer,
    onTertiaryContainer = Verde,

    error = Vermelho,
    onError = Branco,
    errorContainer = VermelhoContainer,
    onErrorContainer = Vermelho,

    background = Branco,
    onBackground = TextoEscuro,
    surface = Branco,
    onSurface = TextoEscuro,
    surfaceVariant = Superficie,
    onSurfaceVariant = TextoEscuro,
)

@Composable
fun TransporteSJCTheme(
    // Kept for API symmetry; the app uses the light brand scheme regardless for now.
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = SjcLightColors,
        typography = TransporteTypography,
        content = content,
    )
}
