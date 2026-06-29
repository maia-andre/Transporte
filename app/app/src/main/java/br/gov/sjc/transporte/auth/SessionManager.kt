package br.gov.sjc.transporte.auth

import br.gov.sjc.transporte.domain.model.Usuario
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Holds the currently "authenticated" user for the mock build. The whole UI observes
 * [currentUser] to decide between the login screen and the role-based home.
 *
 * When real auth lands, back this with Firebase Auth state (FirebaseAuth.addAuthStateListener)
 * and load the matching `usuarios/{uid}` profile — the public API here can stay the same.
 */
object SessionManager {

    private val _currentUser = MutableStateFlow<Usuario?>(null)
    val currentUser: StateFlow<Usuario?> = _currentUser.asStateFlow()

    fun login(usuario: Usuario) {
        _currentUser.value = usuario
    }

    fun logout() {
        _currentUser.value = null
    }
}
