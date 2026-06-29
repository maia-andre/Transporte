package br.gov.sjc.transporte.util

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

/** Centralised pt-BR date/time formatting helpers (display only). */
object DataHora {
    private val ptBr = Locale("pt", "BR")
    private val dataHora = DateTimeFormatter.ofPattern("dd/MM/yyyy 'às' HH:mm", ptBr)
    private val dataHoraCurto = DateTimeFormatter.ofPattern("dd/MM HH:mm", ptBr)
    private val data = DateTimeFormatter.ofPattern("dd/MM/yyyy", ptBr)
    private val hora = DateTimeFormatter.ofPattern("HH:mm", ptBr)

    fun formatar(dt: LocalDateTime): String = dt.format(dataHora)
    fun formatarCurto(dt: LocalDateTime): String = dt.format(dataHoraCurto)
    fun formatarData(d: LocalDate): String = d.format(data)
    fun formatarHora(dt: LocalDateTime): String = dt.format(hora)
}
