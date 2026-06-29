package br.gov.sjc.transporte.ui.common

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.Viagem
import br.gov.sjc.transporte.ui.theme.Vermelho
import br.gov.sjc.transporte.util.DataHora

/**
 * Reusable card rendering a [Viagem] with its status chip and (optional) resolved
 * secretaria / motorista / veiculo labels. Trailing [acoes] render role-specific buttons.
 */
@Composable
fun ViagemCard(
    viagem: Viagem,
    secretariaSigla: String?,
    motoristaNome: String?,
    veiculoDescricao: String?,
    modifier: Modifier = Modifier,
    acoes: @Composable RowScope.() -> Unit = {},
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top,
            ) {
                Text(
                    text = "${viagem.origem}  →  ${viagem.destino}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.weight(1f),
                )
                StatusChip(status = viagem.status, modifier = Modifier.padding(start = 8.dp))
            }

            Spacer(Modifier.height(8.dp))
            LinhaInfo("Saída", DataHora.formatar(viagem.dataHoraSaida))
            LinhaInfo("Retorno", DataHora.formatar(viagem.dataHoraRetorno))
            LinhaInfo("Passageiros", viagem.numPassageiros.toString())
            if (secretariaSigla != null) LinhaInfo("Secretaria", secretariaSigla)
            LinhaInfo("Finalidade", viagem.finalidade)

            if (motoristaNome != null) LinhaInfo("Motorista", motoristaNome)
            if (veiculoDescricao != null) LinhaInfo("Veículo", veiculoDescricao)

            if (viagem.status == StatusViagem.REJEITADA && !viagem.motivoRejeicao.isNullOrBlank()) {
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "Motivo: ${viagem.motivoRejeicao}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Vermelho,
                )
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically,
                content = acoes,
            )
        }
    }
}

@Composable
private fun LinhaInfo(rotulo: String, valor: String) {
    Row(modifier = Modifier.padding(vertical = 1.dp)) {
        Text(
            text = "$rotulo: ",
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
        )
        Text(
            text = valor,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}
