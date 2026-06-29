package br.gov.sjc.transporte.ui.solicitante

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import br.gov.sjc.transporte.ui.common.DateTimeField
import br.gov.sjc.transporte.ui.theme.Azul

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NovaRequisicaoScreen(
    onVoltar: () -> Unit,
    viewModel: NovaRequisicaoViewModel = viewModel(),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Nova requisição") },
                navigationIcon = {
                    IconButton(onClick = onVoltar) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Voltar")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Azul,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White,
                ),
            )
        },
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            OutlinedTextField(
                value = state.origem,
                onValueChange = viewModel::onOrigem,
                label = { Text("Origem") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.destino,
                onValueChange = viewModel::onDestino,
                label = { Text("Destino") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )

            DateTimeField(
                label = "Data/hora de saída",
                value = state.dataHoraSaida,
                onValueChange = viewModel::onSaida,
            )
            DateTimeField(
                label = "Data/hora de retorno",
                value = state.dataHoraRetorno,
                onValueChange = viewModel::onRetorno,
            )

            OutlinedTextField(
                value = state.numPassageiros,
                onValueChange = viewModel::onNumPassageiros,
                label = { Text("Nº de passageiros") },
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.finalidade,
                onValueChange = viewModel::onFinalidade,
                label = { Text("Finalidade") },
                minLines = 2,
                modifier = Modifier.fillMaxWidth(),
            )

            if (state.erro != null) {
                Text(
                    text = state.erro!!,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                )
            }

            Spacer(Modifier.height(8.dp))

            Button(
                onClick = { viewModel.salvar(onSucesso = onVoltar) },
                enabled = !state.salvando,
                modifier = Modifier.fillMaxWidth(),
            ) {
                if (state.salvando) {
                    CircularProgressIndicator(
                        modifier = Modifier.height(20.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                } else {
                    Text("Enviar requisição")
                }
            }
        }
    }
}
