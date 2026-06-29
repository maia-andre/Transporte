package br.gov.sjc.transporte.ui.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.sjc.transporte.auth.SessionManager
import br.gov.sjc.transporte.data.RepositoryProvider
import br.gov.sjc.transporte.domain.model.Role
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

private const val DOMINIO = "@sjc.sp.gov.br"

data class LoginUiState(
    val email: String = "",
    val senha: String = "",
    val carregando: Boolean = false,
    val erro: String? = null,
)

/**
 * MOCK auth. No real backend: it validates the `@sjc.sp.gov.br` domain as a UX hint and then
 * looks up a seeded [br.gov.sjc.transporte.domain.model.Usuario] by e-mail. Quick-login buttons
 * let testers enter as any role. Real auth = Firebase Auth (see CLAUDE.md / PLANO.md).
 */
class LoginViewModel : ViewModel() {

    private val repository = RepositoryProvider.repository()

    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state.asStateFlow()

    fun onEmailChange(value: String) = _state.update { it.copy(email = value, erro = null) }
    fun onSenhaChange(value: String) = _state.update { it.copy(senha = value, erro = null) }

    fun entrar() {
        val email = _state.value.email.trim()
        val senha = _state.value.senha
        when {
            email.isBlank() || senha.isBlank() -> {
                setErro("Informe e-mail e senha.")
                return
            }
            !email.endsWith(DOMINIO, ignoreCase = true) -> {
                setErro("Use um e-mail institucional ($DOMINIO).")
                return
            }
        }
        _state.update { it.copy(carregando = true, erro = null) }
        viewModelScope.launch {
            val usuario = repository.getUsuarioPorEmail(email)
            if (usuario == null) {
                setErro("Usuário não encontrado (mock). Use um e-mail semeado ou os botões de teste abaixo.")
            } else {
                // Mock: password is not verified.
                SessionManager.login(usuario)
            }
            _state.update { it.copy(carregando = false) }
        }
    }

    /** Test shortcut: enter as the first seeded user of [role]. */
    fun entrarComoTeste(role: Role) {
        viewModelScope.launch {
            val usuario = repository.getUsuariosPorRole(role).firstOrNull()
            if (usuario != null) {
                SessionManager.login(usuario)
            } else {
                setErro("Sem usuário mock para ${role.name}.")
            }
        }
    }

    private fun setErro(mensagem: String) {
        _state.update { it.copy(erro = mensagem, carregando = false) }
    }
}
