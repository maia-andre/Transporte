package br.gov.sjc.transporte.ui.motorista

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.sjc.transporte.auth.SessionManager
import br.gov.sjc.transporte.data.RepositoryProvider
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class MotoristaUiState(
    val usuario: Usuario,
    val motoristaVinculado: Boolean = true,
    val viagens: List<Viagem> = emptyList(),
    val secretarias: Map<Int, Secretaria> = emptyMap(),
    val veiculos: Map<String, Veiculo> = emptyMap(),
)

/**
 * Lists the trips assigned to the logged-in driver and advances their status
 * (ACEITA -> EM_ANDAMENTO -> CONCLUIDA). The driver's `motoristas` id is resolved from the
 * user's uid via [getMotoristaPorUsuario].
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class MotoristaViewModel : ViewModel() {

    private val repository = RepositoryProvider.repository()
    private val usuario: Usuario = requireNotNull(SessionManager.currentUser.value) {
        "MotoristaViewModel created without an authenticated user"
    }

    // Resolved asynchronously; null until loaded (or if no driver record links to this user).
    private val motoristaId = MutableStateFlow<String?>(null)
    private val motoristaCarregado = MutableStateFlow(false)

    val uiState: StateFlow<MotoristaUiState>

    init {
        viewModelScope.launch {
            motoristaId.value = repository.getMotoristaPorUsuario(usuario.uid)?.id
            motoristaCarregado.value = true
        }

        val viagensFlow = motoristaId.flatMapLatest { id ->
            if (id == null) flowOf(emptyList()) else repository.observarViagensPorMotorista(id)
        }

        uiState = combine(
            viagensFlow,
            repository.observarSecretarias(),
            repository.observarVeiculos(),
            motoristaCarregado,
            motoristaId,
        ) { viagens, secretarias, veiculos, carregado, id ->
            MotoristaUiState(
                usuario = usuario,
                motoristaVinculado = !carregado || id != null,
                viagens = viagens,
                secretarias = secretarias.associateBy { it.codigo },
                veiculos = veiculos.associateBy { it.id },
            )
        }.stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = MotoristaUiState(usuario = usuario),
        )
    }

    fun iniciar(viagemId: String) {
        viewModelScope.launch { repository.iniciarViagem(viagemId) }
    }

    fun concluir(viagemId: String) {
        viewModelScope.launch { repository.concluirViagem(viagemId) }
    }
}
