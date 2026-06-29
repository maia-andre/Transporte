package br.gov.sjc.transporte.data

import br.gov.sjc.transporte.domain.model.Motorista
import br.gov.sjc.transporte.domain.model.Role
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.Flow

/**
 * Single data-access boundary for the whole app. The UI/ViewModels depend ONLY on this
 * interface, so swapping the in-memory [MockTransporteRepository] for the real
 * [FirebaseTransporteRepository] is a one-line change in [RepositoryProvider].
 *
 * Reactive reads return [Flow] so screens update live (mirrors Firestore snapshot listeners).
 * Writes are `suspend` (mirrors Firestore `await()` calls).
 */
interface TransporteRepository {

    // ----- Secretarias -----
    fun observarSecretarias(): Flow<List<Secretaria>>
    suspend fun getSecretarias(): List<Secretaria>

    // ----- Usuarios (used by mock auth) -----
    suspend fun getUsuarios(): List<Usuario>
    suspend fun getUsuarioPorEmail(email: String): Usuario?
    suspend fun getUsuariosPorRole(role: Role): List<Usuario>

    // ----- Motoristas -----
    fun observarMotoristas(): Flow<List<Motorista>>
    suspend fun getMotoristas(secretariaId: Int? = null): List<Motorista>
    suspend fun getMotoristaPorUsuario(usuarioId: String): Motorista?

    // ----- Veiculos -----
    fun observarVeiculos(): Flow<List<Veiculo>>
    suspend fun getVeiculos(secretariaId: Int? = null): List<Veiculo>

    // ----- Viagens (reads) -----
    fun observarViagens(): Flow<List<Viagem>>
    fun observarViagensPorSolicitante(solicitanteId: String): Flow<List<Viagem>>
    fun observarViagensPorMotorista(motoristaId: String): Flow<List<Viagem>>

    // ----- Viagens (writes / state machine) -----
    /** Creates a new PENDENTE trip. Returns the stored copy (with generated id, if any). */
    suspend fun criarViagem(viagem: Viagem): Viagem

    /** Generic update used for edge cases; prefer the explicit transitions below. */
    suspend fun atualizarViagem(viagem: Viagem)

    /** SOLICITANTE/CONTROLADOR: move a non-final trip to CANCELADA. */
    suspend fun cancelarViagem(viagemId: String)

    /** CONTROLADOR: PENDENTE -> ACEITA, assigning a driver + vehicle. */
    suspend fun aceitarViagem(
        viagemId: String,
        motoristaId: String,
        veiculoId: String,
        decididoPor: String,
    )

    /** CONTROLADOR: PENDENTE -> REJEITADA with a mandatory justification. */
    suspend fun rejeitarViagem(viagemId: String, motivo: String, decididoPor: String)

    /** MOTORISTA: ACEITA -> EM_ANDAMENTO. */
    suspend fun iniciarViagem(viagemId: String)

    /** MOTORISTA: EM_ANDAMENTO -> CONCLUIDA. */
    suspend fun concluirViagem(viagemId: String)
}
