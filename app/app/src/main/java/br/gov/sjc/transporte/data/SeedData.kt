package br.gov.sjc.transporte.data

import br.gov.sjc.transporte.domain.model.Combustivel
import br.gov.sjc.transporte.domain.model.Motorista
import br.gov.sjc.transporte.domain.model.Role
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.StatusMotorista
import br.gov.sjc.transporte.domain.model.StatusVeiculo
import br.gov.sjc.transporte.domain.model.StatusViagem
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import java.time.LocalDate
import java.time.LocalDateTime

/**
 * In-memory seed data for the mock build. Trip dates are computed relative to "now" so the
 * lists are always populated with past/today/future trips whenever the app is launched.
 */
object SeedData {

    private val agora: LocalDateTime = LocalDateTime.now()
    private fun hoje(hora: Int, minuto: Int = 0): LocalDateTime =
        agora.toLocalDate().atTime(hora, minuto)

    val secretarias: List<Secretaria> = listOf(
        Secretaria(codigo = 5, nome = "Gabinete do Prefeito", sigla = "GP"),
        Secretaria(codigo = 10, nome = "Secretaria de Governança", sigla = "SG"),
        Secretaria(codigo = 15, nome = "Secretaria de Assuntos Jurídicos", sigla = "SAJ"),
    )

    val usuarios: List<Usuario> = listOf(
        Usuario("u-sol-1", "Ana Lima", "ana.lima@sjc.sp.gov.br", Role.SOLICITANTE, secretariaId = 10),
        Usuario("u-sol-2", "Bruno Alves", "bruno.alves@sjc.sp.gov.br", Role.SOLICITANTE, secretariaId = 5),
        Usuario("u-mot-1", "Carlos Souza", "carlos.souza@sjc.sp.gov.br", Role.MOTORISTA, secretariaId = 10),
        Usuario("u-ctrl-1", "Diana Rocha", "diana.rocha@sjc.sp.gov.br", Role.CONTROLADOR, secretariaId = 5),
    )

    val motoristas: List<Motorista> = listOf(
        Motorista(
            id = "m-1", nome = "Carlos Souza", matricula = "M-1001", cargo = "Motorista I",
            secretariaId = 10, telefone = "(12) 98888-0001", cnhNumero = "12345678901",
            cnhCategoria = "B", cnhValidade = LocalDate.now().plusYears(2),
            usuarioId = "u-mot-1", status = StatusMotorista.ATIVO,
        ),
        Motorista(
            id = "m-2", nome = "Eduardo Pinto", matricula = "M-1002", cargo = "Motorista II",
            secretariaId = 5, telefone = "(12) 98888-0002", cnhNumero = "22345678902",
            cnhCategoria = "D", cnhValidade = LocalDate.now().plusYears(1),
            usuarioId = null, status = StatusMotorista.ATIVO,
        ),
        Motorista(
            id = "m-3", nome = "Fernanda Dias", matricula = "M-1003", cargo = "Motorista I",
            secretariaId = 15, telefone = "(12) 98888-0003", cnhNumero = "32345678903",
            cnhCategoria = "B", cnhValidade = LocalDate.now().plusMonths(8),
            usuarioId = null, status = StatusMotorista.ATIVO,
        ),
    )

    val veiculos: List<Veiculo> = listOf(
        Veiculo("v-1", "GP-01", "ABC1D23", "PAT-001", "VW Gol", 2021, 5, Combustivel.FLEX, 5, StatusVeiculo.DISPONIVEL),
        Veiculo("v-2", "SG-12", "DEF2E34", "PAT-014", "Chevrolet Spin", 2022, 7, Combustivel.FLEX, 10, StatusVeiculo.DISPONIVEL),
        Veiculo("v-3", "SAJ-07", "GHI3F45", "PAT-031", "Toyota Corolla", 2023, 5, Combustivel.FLEX, 15, StatusVeiculo.EM_USO),
        Veiculo("v-4", "SG-20", "JKL4G56", "PAT-040", "Renault Master", 2020, 16, Combustivel.DIESEL, 10, StatusVeiculo.MANUTENCAO),
    )

    val viagens: List<Viagem> = listOf(
        // PENDENTE — future (Ana / SG)
        Viagem(
            id = "vg-1", solicitanteId = "u-sol-1", solicitanteNome = "Ana Lima", secretariaId = 10,
            origem = "Paço Municipal", destino = "Aeroporto de Guarulhos",
            dataHoraSaida = agora.plusDays(1).withHour(8).withMinute(0).withSecond(0).withNano(0),
            dataHoraRetorno = agora.plusDays(1).withHour(14).withMinute(0).withSecond(0).withNano(0),
            numPassageiros = 3, finalidade = "Recepção de comitiva",
            status = StatusViagem.PENDENTE,
            criadoEm = agora.minusDays(1), atualizadoEm = agora.minusDays(1),
        ),
        // PENDENTE — today (Ana / SG)
        Viagem(
            id = "vg-2", solicitanteId = "u-sol-1", solicitanteNome = "Ana Lima", secretariaId = 10,
            origem = "Sede da Secretaria", destino = "Câmara Municipal",
            dataHoraSaida = hoje(15, 0), dataHoraRetorno = hoje(18, 0),
            numPassageiros = 2, finalidade = "Reunião de orçamento",
            status = StatusViagem.PENDENTE,
            criadoEm = agora.minusHours(5), atualizadoEm = agora.minusHours(5),
        ),
        // ACEITA — today, assigned to Carlos (m-1) + Spin (v-2)
        Viagem(
            id = "vg-3", solicitanteId = "u-sol-1", solicitanteNome = "Ana Lima", secretariaId = 10,
            origem = "Paço Municipal", destino = "Centro de Eventos",
            dataHoraSaida = hoje(16, 30), dataHoraRetorno = hoje(20, 0),
            numPassageiros = 4, finalidade = "Cerimônia de premiação",
            status = StatusViagem.ACEITA, motoristaId = "m-1", veiculoId = "v-2",
            decididoPor = "u-ctrl-1", decididoEm = agora.minusHours(3),
            criadoEm = agora.minusDays(1), atualizadoEm = agora.minusHours(3),
        ),
        // EM_ANDAMENTO — happening now, Carlos (m-1) + Gol (v-1)
        Viagem(
            id = "vg-4", solicitanteId = "u-sol-2", solicitanteNome = "Bruno Alves", secretariaId = 5,
            origem = "Gabinete do Prefeito", destino = "Distrito de Eugênio de Melo",
            dataHoraSaida = agora.minusHours(2).withSecond(0).withNano(0),
            dataHoraRetorno = agora.plusHours(3).withSecond(0).withNano(0),
            numPassageiros = 2, finalidade = "Vistoria de obra",
            status = StatusViagem.EM_ANDAMENTO, motoristaId = "m-1", veiculoId = "v-1",
            decididoPor = "u-ctrl-1", decididoEm = agora.minusDays(1),
            criadoEm = agora.minusDays(2), atualizadoEm = agora.minusHours(2),
        ),
        // CONCLUIDA — past, Eduardo (m-2) + Gol (v-1)
        Viagem(
            id = "vg-5", solicitanteId = "u-sol-2", solicitanteNome = "Bruno Alves", secretariaId = 5,
            origem = "Paço Municipal", destino = "Fórum da Comarca",
            dataHoraSaida = agora.minusDays(2).withHour(9).withMinute(0).withSecond(0).withNano(0),
            dataHoraRetorno = agora.minusDays(2).withHour(12).withMinute(0).withSecond(0).withNano(0),
            numPassageiros = 1, finalidade = "Protocolo de documentos",
            status = StatusViagem.CONCLUIDA, motoristaId = "m-2", veiculoId = "v-1",
            decididoPor = "u-ctrl-1", decididoEm = agora.minusDays(3),
            criadoEm = agora.minusDays(4), atualizadoEm = agora.minusDays(2),
        ),
        // ACEITA — future, assigned to Carlos (m-1) + Spin (v-2)
        Viagem(
            id = "vg-6", solicitanteId = "u-sol-2", solicitanteNome = "Bruno Alves", secretariaId = 5,
            origem = "Gabinete do Prefeito", destino = "Universidade Federal",
            dataHoraSaida = agora.plusDays(2).withHour(7).withMinute(30).withSecond(0).withNano(0),
            dataHoraRetorno = agora.plusDays(2).withHour(13).withMinute(0).withSecond(0).withNano(0),
            numPassageiros = 5, finalidade = "Visita técnica acadêmica",
            status = StatusViagem.ACEITA, motoristaId = "m-1", veiculoId = "v-2",
            decididoPor = "u-ctrl-1", decididoEm = agora.minusHours(20),
            criadoEm = agora.minusDays(3), atualizadoEm = agora.minusHours(20),
        ),
        // REJEITADA — future (Ana / SG)
        Viagem(
            id = "vg-7", solicitanteId = "u-sol-1", solicitanteNome = "Ana Lima", secretariaId = 10,
            origem = "Sede da Secretaria", destino = "São Paulo - Capital",
            dataHoraSaida = agora.plusDays(3).withHour(6).withMinute(0).withSecond(0).withNano(0),
            dataHoraRetorno = agora.plusDays(3).withHour(22).withMinute(0).withSecond(0).withNano(0),
            numPassageiros = 8, finalidade = "Congresso estadual",
            status = StatusViagem.REJEITADA,
            motivoRejeicao = "Sem veículo de 8 lugares disponível na data solicitada.",
            decididoPor = "u-ctrl-1", decididoEm = agora.minusHours(8),
            criadoEm = agora.minusDays(2), atualizadoEm = agora.minusHours(8),
        ),
        // CANCELADA — future (Bruno / GP)
        Viagem(
            id = "vg-8", solicitanteId = "u-sol-2", solicitanteNome = "Bruno Alves", secretariaId = 5,
            origem = "Gabinete do Prefeito", destino = "Aeroporto de São José dos Campos",
            dataHoraSaida = agora.plusDays(4).withHour(10).withMinute(0).withSecond(0).withNano(0),
            dataHoraRetorno = agora.plusDays(4).withHour(16).withMinute(0).withSecond(0).withNano(0),
            numPassageiros = 2, finalidade = "Translado de autoridade (cancelado)",
            status = StatusViagem.CANCELADA,
            criadoEm = agora.minusDays(2), atualizadoEm = agora.minusHours(30),
        ),
    )
}
