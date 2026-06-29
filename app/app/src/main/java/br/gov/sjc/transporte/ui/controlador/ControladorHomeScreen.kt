package br.gov.sjc.transporte.ui.controlador

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.rotulo
import br.gov.sjc.transporte.ui.common.AppTopBar
import br.gov.sjc.transporte.ui.common.ViagemCard
import br.gov.sjc.transporte.ui.theme.corStatusViagem

@Composable
fun ControladorHomeScreen(
    onLogout: () -> Unit,
    viewModel: ControladorViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            AppTopBar(
                titulo = "Visão geral",
                subtitulo = state.usuario.nome,
                onLogout = onLogout,
            )
        },
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier.fillMaxWidth(),
            contentPadding = PaddingValues(
                start = 16.dp,
                end = 16.dp,
                top = innerPadding.calculateTopPadding() + 12.dp,
                bottom = innerPadding.calculateBottomPadding() + 16.dp,
            ),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item {
                Text(
                    text = "Total de viagens: ${state.total}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
            }

            // Status counts, two cards per row.
            items(StatusViagem.entries.chunked(2)) { par ->
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    par.forEach { status ->
                        StatCard(
                            status = status,
                            contagem = state.contagemPorStatus[status] ?: 0,
                            modifier = Modifier.weight(1f),
                        )
                    }
                    if (par.size == 1) Spacer(Modifier.weight(1f))
                }
            }

            item {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Viagens de hoje",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
            }

            if (state.viagensHoje.isEmpty()) {
                item {
                    Text(
                        text = "Nenhuma viagem agendada para hoje.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            } else {
                items(state.viagensHoje, key = { it.id }) { viagem ->
                    val veiculo = viagem.veiculoId?.let { state.veiculos[it] }
                    val motorista = viagem.motoristaId?.let { state.motoristas[it] }
                    ViagemCard(
                        viagem = viagem,
                        secretariaSigla = state.secretarias[viagem.secretariaId]?.sigla,
                        motoristaNome = motorista?.nome,
                        veiculoDescricao = veiculo?.let { "${it.prefixo} · ${it.marcaModelo}" },
                    )
                }
            }
        }
    }
}

@Composable
private fun StatCard(
    status: StatusViagem,
    contagem: Int,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    modifier = Modifier.size(12.dp),
                    shape = CircleShape,
                    color = corStatusViagem(status),
                ) {}
                Spacer(Modifier.size(8.dp))
                Text(
                    text = status.rotulo,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Spacer(Modifier.height(4.dp))
            Text(
                text = contagem.toString(),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = corStatusViagem(status),
            )
        }
    }
}
