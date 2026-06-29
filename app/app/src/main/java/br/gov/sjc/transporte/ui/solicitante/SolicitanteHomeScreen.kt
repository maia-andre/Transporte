package br.gov.sjc.transporte.ui.solicitante

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.ui.common.AppTopBar
import br.gov.sjc.transporte.ui.common.ViagemCard

@Composable
fun SolicitanteHomeScreen(
    onNovaRequisicao: () -> Unit,
    onLogout: () -> Unit,
    viewModel: SolicitanteViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            AppTopBar(
                titulo = "Minhas requisições",
                subtitulo = state.usuario.nome,
                onLogout = onLogout,
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = onNovaRequisicao,
                icon = { Icon(Icons.Filled.Add, contentDescription = null) },
                text = { Text("Nova requisição") },
            )
        },
    ) { innerPadding ->
        if (state.viagens.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(24.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "Você ainda não tem requisições.\nToque em \"Nova requisição\" para começar.",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(
                    start = 16.dp,
                    end = 16.dp,
                    top = innerPadding.calculateTopPadding() + 12.dp,
                    bottom = innerPadding.calculateBottomPadding() + 96.dp,
                ),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                items(state.viagens, key = { it.id }) { viagem ->
                    val veiculo = viagem.veiculoId?.let { state.veiculos[it] }
                    val motorista = viagem.motoristaId?.let { state.motoristas[it] }
                    ViagemCard(
                        viagem = viagem,
                        secretariaSigla = state.secretarias[viagem.secretariaId]?.sigla,
                        motoristaNome = motorista?.nome,
                        veiculoDescricao = veiculo?.let { "${it.prefixo} · ${it.marcaModelo}" },
                    ) {
                        if (viagem.status == StatusViagem.PENDENTE) {
                            TextButton(onClick = { viewModel.cancelar(viagem.id) }) {
                                Text("Cancelar", color = MaterialTheme.colorScheme.error)
                            }
                        }
                    }
                }
            }
        }
    }
}
