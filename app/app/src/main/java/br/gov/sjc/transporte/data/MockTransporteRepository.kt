package br.gov.sjc.transporte.data

import br.gov.sjc.transporte.domain.model.Motorista
import br.gov.sjc.transporte.domain.model.Role
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.update
import java.time.LocalDateTime
import java.util.UUID

/**
 * In-memory implementation backed by [MutableStateFlow]s, so observers update live exactly
 * like Firestore snapshot listeners would. This is the active repository in the mock build.
 *
 * State is process-scoped: it resets when the app process is killed (seeded again on start).
 */
class MockTransporteRepository : TransporteRepository {

    private val secretariasFlow = MutableStateFlow(SeedData.secretarias)
    private val usuariosFlow = MutableStateFlow(SeedData.usuarios)
    private val motoristasFlow = MutableStateFlow(SeedData.motoristas)
    private val veiculosFlow = MutableStateFlow(SeedData.veiculos)
    private val viagensFlow = MutableStateFlow(SeedData.viagens)

    // ----- Secretarias -----
    override fun observarSecretarias(): Flow<List<Secretaria>> = secretariasFlow.asStateFlow()
    override suspend fun getSecretarias(): List<Secretaria> = secretariasFlow.value

    // ----- Usuarios -----
    override suspend fun getUsuarios(): List<Usuario> = usuariosFlow.value

    override suspend fun getUsuarioPorEmail(email: String): Usuario? =
        usuariosFlow.value.firstOrNull { it.email.equals(email.trim(), ignoreCase = true) }

    override suspend fun getUsuariosPorRole(role: Role): List<Usuario> =
        usuariosFlow.value.filter { it.role == role }

    // ----- Motoristas -----
    override fun observarMotoristas(): Flow<List<Motorista>> = motoristasFlow.asStateFlow()

    override suspend fun getMotoristas(secretariaId: Int?): List<Motorista> =
        motoristasFlow.value.filter { secretariaId == null || it.secretariaId == secretariaId }

    override suspend fun getMotoristaPorUsuario(usuarioId: String): Motorista? =
        motoristasFlow.value.firstOrNull { it.usuarioId == usuarioId }

    // ----- Veiculos -----
    override fun observarVeiculos(): Flow<List<Veiculo>> = veiculosFlow.asStateFlow()

    override suspend fun getVeiculos(secretariaId: Int?): List<Veiculo> =
        veiculosFlow.value.filter { secretariaId == null || it.secretariaId == secretariaId }

    // ----- Viagens (reads) -----
    override fun observarViagens(): Flow<List<Viagem>> =
        viagensFlow.map { lista -> lista.sortedByDescending { it.dataHoraSaida } }

    override fun observarViagensPorSolicitante(solicitanteId: String): Flow<List<Viagem>> =
        viagensFlow.map { lista ->
            lista.filter { it.solicitanteId == solicitanteId }
                .sortedByDescending { it.dataHoraSaida }
        }

    override fun observarViagensPorMotorista(motoristaId: String): Flow<List<Viagem>> =
        viagensFlow.map { lista ->
            lista.filter { it.motoristaId == motoristaId }
                .sortedBy { it.dataHoraSaida }
        }

    // ----- Viagens (writes) -----
    override suspend fun criarViagem(viagem: Viagem): Viagem {
        val agora = LocalDateTime.now()
        val nova = viagem.copy(
            id = viagem.id.ifBlank { "vg-${UUID.randomUUID()}" },
            status = StatusViagem.PENDENTE,
            criadoEm = agora,
            atualizadoEm = agora,
        )
        viagensFlow.update { it + nova }
        return nova
    }

    override suspend fun atualizarViagem(viagem: Viagem) {
        viagensFlow.update { lista ->
            lista.map { if (it.id == viagem.id) viagem.copy(atualizadoEm = LocalDateTime.now()) else it }
        }
    }

    override suspend fun cancelarViagem(viagemId: String) {
        transformar(viagemId) { it.copy(status = StatusViagem.CANCELADA) }
    }

    override suspend fun aceitarViagem(
        viagemId: String,
        motoristaId: String,
        veiculoId: String,
        decididoPor: String,
    ) {
        transformar(viagemId) {
            it.copy(
                status = StatusViagem.ACEITA,
                motoristaId = motoristaId,
                veiculoId = veiculoId,
                decididoPor = decididoPor,
                decididoEm = LocalDateTime.now(),
                motivoRejeicao = null,
            )
        }
    }

    override suspend fun rejeitarViagem(viagemId: String, motivo: String, decididoPor: String) {
        transformar(viagemId) {
            it.copy(
                status = StatusViagem.REJEITADA,
                motivoRejeicao = motivo,
                decididoPor = decididoPor,
                decididoEm = LocalDateTime.now(),
            )
        }
    }

    override suspend fun iniciarViagem(viagemId: String) {
        transformar(viagemId) { it.copy(status = StatusViagem.EM_ANDAMENTO) }
    }

    override suspend fun concluirViagem(viagemId: String) {
        transformar(viagemId) { it.copy(status = StatusViagem.CONCLUIDA) }
    }

    /** Applies [bloco] to the matching trip and stamps `atualizadoEm`. */
    private fun transformar(viagemId: String, bloco: (Viagem) -> Viagem) {
        viagensFlow.update { lista ->
            lista.map { if (it.id == viagemId) bloco(it).copy(atualizadoEm = LocalDateTime.now()) else it }
        }
    }
}
