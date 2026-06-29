package br.gov.sjc.transporte.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import br.gov.sjc.transporte.auth.SessionManager
import br.gov.sjc.transporte.domain.model.Role
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.ui.controlador.ControladorHomeScreen
import br.gov.sjc.transporte.ui.login.LoginScreen
import br.gov.sjc.transporte.ui.motorista.MotoristaHomeScreen
import br.gov.sjc.transporte.ui.solicitante.NovaRequisicaoScreen
import br.gov.sjc.transporte.ui.solicitante.SolicitanteHomeScreen

/**
 * Root composable. Observes the (mock) session: shows the login screen when signed out, and a
 * role-based navigation graph when signed in. Logging out tears the whole graph down, clearing
 * the role ViewModels so the next login starts fresh.
 */
@Composable
fun TransporteApp() {
    val usuario by SessionManager.currentUser.collectAsStateWithLifecycle()

    when (val u = usuario) {
        null -> LoginScreen()
        else -> AppNavHost(usuario = u)
    }
}

@Composable
private fun AppNavHost(usuario: Usuario) {
    val navController = rememberNavController()
    val onLogout: () -> Unit = { SessionManager.logout() }

    val startDestination = when (usuario.role) {
        Role.SOLICITANTE -> Rotas.SOLICITANTE_HOME
        Role.MOTORISTA -> Rotas.MOTORISTA_HOME
        Role.CONTROLADOR -> Rotas.CONTROLADOR_HOME
    }

    NavHost(navController = navController, startDestination = startDestination) {
        composable(Rotas.SOLICITANTE_HOME) {
            SolicitanteHomeScreen(
                onNovaRequisicao = { navController.navigate(Rotas.NOVA_REQUISICAO) },
                onLogout = onLogout,
            )
        }
        composable(Rotas.NOVA_REQUISICAO) {
            NovaRequisicaoScreen(onVoltar = { navController.popBackStack() })
        }
        composable(Rotas.MOTORISTA_HOME) {
            MotoristaHomeScreen(onLogout = onLogout)
        }
        composable(Rotas.CONTROLADOR_HOME) {
            ControladorHomeScreen(onLogout = onLogout)
        }
    }
}
