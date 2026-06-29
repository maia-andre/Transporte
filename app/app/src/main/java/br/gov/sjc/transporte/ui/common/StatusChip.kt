package br.gov.sjc.transporte.ui.common

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.rotulo
import br.gov.sjc.transporte.ui.theme.corStatusViagem

/** Status badge with the canonical SJC status color. */
@Composable
fun StatusChip(
    status: StatusViagem,
    modifier: Modifier = Modifier,
) {
    val cor = corStatusViagem(status)
    Surface(
        modifier = modifier,
        color = cor,
        contentColor = Color.White,
        shape = RoundedCornerShape(50),
    ) {
        Text(
            text = status.rotulo,
            modifier = Modifier.padding(PaddingValues(horizontal = 10.dp, vertical = 4.dp)),
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
        )
    }
}
