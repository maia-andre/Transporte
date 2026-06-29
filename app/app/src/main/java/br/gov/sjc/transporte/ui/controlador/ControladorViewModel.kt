package br.gov.sjc.transporte.ui.controlador

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.sjc.transporte.auth.SessionManager
import br.gov.sjc.transporte.data.RepositoryProvider
import br.gov.sjc.transporte.domain.model.Motorista
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import java.time.LocalDate

data class ControladorUiState(
    val usuario: Usuario,
    val contagemPorStatus: Map<StatusViagem, Int> = emptyMap(),
    val total: Int = 0,
    val viagensHoje: List<Viagem> = emptyList(),
    val secretarias: Map<Int, Secretaria> = emptyMap(),
    val motoristas: Map<String, Motorista> = emptyMap(),
    val veiculos: Map<String, Veiculo> = emptyMap(),
)

/** Read-mostly overview for the controller: counts by status and today's trips. */
class ControladorViewModel : ViewModel() {

    private val repository = RepositoryProvider.repository()
    private val usuario: Usuario = requireNotNull(SessionManager.currentUser.value) {
        "ControladorViewModel created without an authenticated user"
    }

    val uiState: StateFlow<ControladorUiState> = combine(
        repository.observarViagens(),
        repository.observarSecretarias(),
        repository.observarMotoristas(),
        repository.observarVeiculos(),
    ) { viagens, secretarias, motoristas, veiculos ->
        val hoje = LocalDate.now()
        ControladorUiState(
            usuario = usuario,
            contagemPorStatus = viagens.groupingBy { it.status }.eachCount(),
            total = viagens.size,
            viagensHoje = viagens
                .filter { it.dataHoraSaida.toLocalDate() == hoje }
                .sortedBy { it.dataHoraSaida },
            secretarias = secretarias.associateBy { it.codigo },
            motoristas = motoristas.associateBy { it.id },
            veiculos = veiculos.associateBy { it.id },
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = ControladorUiState(usuario = usuario),
    )
}
