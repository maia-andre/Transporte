package br.gov.sjc.transporte.ui.common

import androidx.compose.foundation.layout.Column
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarColors
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import br.gov.sjc.transporte.ui.theme.Azul

/** App bar in SJC blue with an optional subtitle and a "Sair" (logout) action. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppTopBar(
    titulo: String,
    subtitulo: String? = null,
    onLogout: (() -> Unit)? = null,
) {
    val cores: TopAppBarColors = TopAppBarDefaults.topAppBarColors(
        containerColor = Azul,
        titleContentColor = Color.White,
        actionIconContentColor = Color.White,
    )
    TopAppBar(
        title = {
            Column {
                Text(titulo, fontWeight = FontWeight.SemiBold)
                if (subtitulo != null) {
                    Text(subtitulo, style = MaterialTheme.typography.labelSmall, color = Color.White)
                }
            }
        },
        colors = cores,
        actions = {
            if (onLogout != null) {
                TextButton(onClick = onLogout) {
                    Text("Sair", color = Color.White)
                }
            }
        },
    )
}
