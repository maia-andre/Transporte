package br.gov.sjc.transporte.data

import br.gov.sjc.transporte.domain.model.Role
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.time.LocalDateTime

/**
 * Unit tests (JVM) for the in-memory repository — the app's data layer behavior and the
 * trip state-machine transitions. Run with `./gradlew test`.
 */
class MockTransporteRepositoryTest {

    private lateinit var repo: MockTransporteRepository

    @Before
    fun setUp() {
        repo = MockTransporteRepository()
    }

    private suspend fun viagem(id: String): Viagem =
        repo.observarViagens().first().first { it.id == id }

    @Test
    fun criarViagem_geraId_eEntraComoPendente() = runTest {
        val base = LocalDateTime.now()
        val nova = repo.criarViagem(
            Viagem(
                id = "", solicitanteId = "u-sol-1", solicitanteNome = "Ana Lima",
                secretariaId = 10, origem = "A", destino = "B",
                dataHoraSaida = base.plusHours(1), dataHoraRetorno = base.plusHours(3),
                numPassageiros = 2, finalidade = "teste",
                criadoEm = base, atualizadoEm = base,
            )
        )
        assertTrue(nova.id.startsWith("vg-"))
        assertEquals(StatusViagem.PENDENTE, nova.status)
        assertNotNull(nova.criadoEm)
        // persistida e observável
        assertEquals(StatusViagem.PENDENTE, viagem(nova.id).status)
    }

    @Test
    fun aceitarViagem_defineEscalaEStatus() = runTest {
        repo.aceitarViagem("vg-2", motoristaId = "m-1", veiculoId = "v-2", decididoPor = "u-ctrl-1")
        val v = viagem("vg-2")
        assertEquals(StatusViagem.ACEITA, v.status)
        assertEquals("m-1", v.motoristaId)
        assertEquals("v-2", v.veiculoId)
        assertEquals("u-ctrl-1", v.decididoPor)
        assertNull(v.motivoRejeicao)
    }

    @Test
    fun rejeitarViagem_gravaMotivo() = runTest {
        repo.rejeitarViagem("vg-1", motivo = "Sem frota", decididoPor = "u-ctrl-1")
        val v = viagem("vg-1")
        assertEquals(StatusViagem.REJEITADA, v.status)
        assertEquals("Sem frota", v.motivoRejeicao)
    }

    @Test
    fun fluxoMotorista_iniciaEConclui() = runTest {
        repo.iniciarViagem("vg-3")        // ACEITA -> EM_ANDAMENTO
        assertEquals(StatusViagem.EM_ANDAMENTO, viagem("vg-3").status)
        repo.concluirViagem("vg-4")       // EM_ANDAMENTO -> CONCLUIDA
        assertEquals(StatusViagem.CONCLUIDA, viagem("vg-4").status)
    }

    @Test
    fun cancelarViagem_mudaParaCancelada() = runTest {
        repo.cancelarViagem("vg-1")
        assertEquals(StatusViagem.CANCELADA, viagem("vg-1").status)
    }

    @Test
    fun getUsuarioPorEmail_eCaseInsensitive() = runTest {
        val u = repo.getUsuarioPorEmail("ANA.LIMA@SJC.SP.GOV.BR")
        assertNotNull(u)
        assertEquals("u-sol-1", u!!.uid)
        assertEquals(Role.SOLICITANTE, u.role)
    }

    @Test
    fun observarViagensPorMotorista_filtraDoCondutor() = runTest {
        val ids = repo.observarViagensPorMotorista("m-1").first().map { it.id }.toSet()
        assertTrue(ids.containsAll(setOf("vg-3", "vg-4", "vg-6")))
        assertTrue(ids.none { it == "vg-5" })   // vg-5 é do m-2
    }
}
