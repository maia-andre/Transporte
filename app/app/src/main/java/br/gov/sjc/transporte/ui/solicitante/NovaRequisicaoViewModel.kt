package br.gov.sjc.transporte.ui.solicitante

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.sjc.transporte.auth.SessionManager
import br.gov.sjc.transporte.data.RepositoryProvider
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDateTime

data class NovaRequisicaoUiState(
    val origem: String = "",
    val destino: String = "",
    val dataHoraSaida: LocalDateTime = LocalDateTime.now().plusDays(1).withHour(8).withMinute(0).withSecond(0).withNano(0),
    val dataHoraRetorno: LocalDateTime = LocalDateTime.now().plusDays(1).withHour(12).withMinute(0).withSecond(0).withNano(0),
    val numPassageiros: String = "1",
    val finalidade: String = "",
    val erro: String? = null,
    val salvando: Boolean = false,
)

/** Holds the "Nova requisição" form state, validates it, and creates a PENDENTE trip. */
class NovaRequisicaoViewModel : ViewModel() {

    private val repository = RepositoryProvider.repository()
    private val usuario: Usuario = requireNotNull(SessionManager.currentUser.value) {
        "NovaRequisicaoViewModel created without an authenticated user"
    }

    private val _state = MutableStateFlow(NovaRequisicaoUiState())
    val state: StateFlow<NovaRequisicaoUiState> = _state.asStateFlow()

    fun onOrigem(v: String) = _state.update { it.copy(origem = v, erro = null) }
    fun onDestino(v: String) = _state.update { it.copy(destino = v, erro = null) }
    fun onSaida(v: LocalDateTime) = _state.update { it.copy(dataHoraSaida = v, erro = null) }
    fun onRetorno(v: LocalDateTime) = _state.update { it.copy(dataHoraRetorno = v, erro = null) }
    fun onNumPassageiros(v: String) =
        _state.update { it.copy(numPassageiros = v.filter(Char::isDigit), erro = null) }
    fun onFinalidade(v: String) = _state.update { it.copy(finalidade = v, erro = null) }

    /** Validates and creates the trip; invokes [onSucesso] on success. */
    fun salvar(onSucesso: () -> Unit) {
        val s = _state.value
        val passageiros = s.numPassageiros.toIntOrNull() ?: 0
        val erro = when {
            s.origem.isBlank() -> "Informe a origem."
            s.destino.isBlank() -> "Informe o destino."
            s.finalidade.isBlank() -> "Informe a finalidade."
            passageiros <= 0 -> "Número de passageiros deve ser maior que zero."
            !s.dataHoraRetorno.isAfter(s.dataHoraSaida) -> "O retorno deve ser depois da saída."
            else -> null
        }
        if (erro != null) {
            _state.update { it.copy(erro = erro) }
            return
        }

        _state.update { it.copy(salvando = true, erro = null) }
        viewModelScope.launch {
            val agora = LocalDateTime.now()
            repository.criarViagem(
                Viagem(
                    id = "",
                    solicitanteId = usuario.uid,
                    solicitanteNome = usuario.nome,
                    secretariaId = usuario.secretariaId,
                    origem = s.origem.trim(),
                    destino = s.destino.trim(),
                    dataHoraSaida = s.dataHoraSaida,
                    dataHoraRetorno = s.dataHoraRetorno,
                    numPassageiros = passageiros,
                    finalidade = s.finalidade.trim(),
                    criadoEm = agora,
                    atualizadoEm = agora,
                ),
            )
            _state.update { it.copy(salvando = false) }
            onSucesso()
        }
    }
}
