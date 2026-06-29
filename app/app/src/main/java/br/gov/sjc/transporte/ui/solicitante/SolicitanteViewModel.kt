package br.gov.sjc.transporte.ui.solicitante

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.sjc.transporte.auth.SessionManager
import br.gov.sjc.transporte.data.RepositoryProvider
import br.gov.sjc.transporte.domain.model.Motorista
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class SolicitanteUiState(
    val usuario: Usuario,
    val viagens: List<Viagem> = emptyList(),
    val secretarias: Map<Int, Secretaria> = emptyMap(),
    val motoristas: Map<String, Motorista> = emptyMap(),
    val veiculos: Map<String, Veiculo> = emptyMap(),
)

/** Lists the requester's own trips (live) and cancels pending ones. */
class SolicitanteViewModel : ViewModel() {

    private val repository = RepositoryProvider.repository()
    private val usuario: Usuario = requireNotNull(SessionManager.currentUser.value) {
        "SolicitanteViewModel created without an authenticated user"
    }

    val uiState: StateFlow<SolicitanteUiState> = combine(
        repository.observarViagensPorSolicitante(usuario.uid),
        repository.observarSecretarias(),
        repository.observarMotoristas(),
        repository.observarVeiculos(),
    ) { viagens, secretarias, motoristas, veiculos ->
        SolicitanteUiState(
            usuario = usuario,
            viagens = viagens,
            secretarias = secretarias.associateBy { it.codigo },
            motoristas = motoristas.associateBy { it.id },
            veiculos = veiculos.associateBy { it.id },
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = SolicitanteUiState(usuario = usuario),
    )

    fun cancelar(viagemId: String) {
        viewModelScope.launch { repository.cancelarViagem(viagemId) }
    }
}
