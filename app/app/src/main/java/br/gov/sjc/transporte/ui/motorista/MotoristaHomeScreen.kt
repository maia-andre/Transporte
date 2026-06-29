package br.gov.sjc.transporte.ui.motorista

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
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
import br.gov.sjc.transporte.ui.theme.AzulClaro
import br.gov.sjc.transporte.ui.theme.Verde

@Composable
fun MotoristaHomeScreen(
    onLogout: () -> Unit,
    viewModel: MotoristaViewModel = viewModel(),
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            AppTopBar(
                titulo = "Minhas escalas",
                subtitulo = state.usuario.nome,
                onLogout = onLogout,
            )
        },
    ) { innerPadding ->
        when {
            !state.motoristaVinculado -> CentralMensagem(
                modifier = Modifier.padding(innerPadding),
                texto = "Seu usuário não está vinculado a um cadastro de motorista.\n" +
                    "Solicite ao controlador o vínculo no painel.",
            )

            state.viagens.isEmpty() -> CentralMensagem(
                modifier = Modifier.padding(innerPadding),
                texto = "Nenhuma viagem atribuída a você no momento.",
            )

            else -> LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(
                    start = 16.dp,
                    end = 16.dp,
                    top = innerPadding.calculateTopPadding() + 12.dp,
                    bottom = innerPadding.calculateBottomPadding() + 16.dp,
                ),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                items(state.viagens, key = { it.id }) { viagem ->
                    val veiculo = viagem.veiculoId?.let { state.veiculos[it] }
                    ViagemCard(
                        viagem = viagem,
                        secretariaSigla = state.secretarias[viagem.secretariaId]?.sigla,
                        motoristaNome = null,
                        veiculoDescricao = veiculo?.let { "${it.prefixo} · ${it.marcaModelo} (${it.placa})" },
                    ) {
                        when (viagem.status) {
                            StatusViagem.ACEITA -> Button(
                                onClick = { viewModel.iniciar(viagem.id) },
                                colors = ButtonDefaults.buttonColors(containerColor = AzulClaro),
                            ) { Text("Iniciar viagem") }

                            StatusViagem.EM_ANDAMENTO -> Button(
                                onClick = { viewModel.concluir(viagem.id) },
                                colors = ButtonDefaults.buttonColors(containerColor = Verde),
                            ) { Text("Concluir viagem") }

                            else -> Unit
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CentralMensagem(texto: String, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = texto,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
    }
}
