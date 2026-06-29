package br.gov.sjc.transporte.ui.common

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.matchParentSize
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import br.gov.sjc.transporte.util.DataHora
import java.time.Instant
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset

/**
 * Read-only text field that opens a date picker followed by a time picker, reporting the
 * combined [LocalDateTime] via [onValueChange]. The whole field is tap-able.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DateTimeField(
    label: String,
    value: LocalDateTime,
    onValueChange: (LocalDateTime) -> Unit,
    modifier: Modifier = Modifier,
    isError: Boolean = false,
    supportingText: String? = null,
) {
    var showDate by remember { mutableStateOf(false) }
    var showTime by remember { mutableStateOf(false) }

    Box(modifier = modifier.fillMaxWidth()) {
        OutlinedTextField(
            value = DataHora.formatar(value),
            onValueChange = {},
            readOnly = true,
            label = { Text(label) },
            leadingIcon = { Icon(Icons.Filled.DateRange, contentDescription = null) },
            isError = isError,
            supportingText = supportingText?.let { msg -> { Text(msg) } },
            modifier = Modifier.fillMaxWidth(),
        )
        // Transparent overlay so a tap anywhere on the field opens the picker.
        Box(
            Modifier
                .matchParentSize()
                .clickable { showDate = true },
        )
    }

    if (showDate) {
        val dateState = rememberDatePickerState(
            initialSelectedDateMillis = value.toLocalDate()
                .atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli(),
        )
        DatePickerDialog(
            onDismissRequest = { showDate = false },
            confirmButton = {
                TextButton(onClick = {
                    dateState.selectedDateMillis?.let { millis ->
                        val novaData = Instant.ofEpochMilli(millis)
                            .atZone(ZoneOffset.UTC).toLocalDate()
                        onValueChange(LocalDateTime.of(novaData, value.toLocalTime()))
                    }
                    showDate = false
                    showTime = true
                }) { Text("Próximo") }
            },
            dismissButton = {
                TextButton(onClick = { showDate = false }) { Text("Cancelar") }
            },
        ) {
            DatePicker(state = dateState)
        }
    }

    if (showTime) {
        val timeState = rememberTimePickerState(
            initialHour = value.hour,
            initialMinute = value.minute,
            is24Hour = true,
        )
        AlertDialog(
            onDismissRequest = { showTime = false },
            confirmButton = {
                TextButton(onClick = {
                    onValueChange(
                        LocalDateTime.of(
                            value.toLocalDate(),
                            LocalTime.of(timeState.hour, timeState.minute),
                        ),
                    )
                    showTime = false
                }) { Text("OK") }
            },
            dismissButton = {
                TextButton(onClick = { showTime = false }) { Text("Cancelar") }
            },
            title = { Text("Selecione o horário") },
            text = { TimePicker(state = timeState) },
        )
    }
}
