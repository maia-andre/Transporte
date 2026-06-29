package br.gov.sjc.transporte

import android.app.Application

/**
 * Application entry point. Currently a no-op (the app runs on the in-memory mock repository).
 *
 * When Firebase is enabled, initialise it here:
 *   `com.google.firebase.FirebaseApp.initializeApp(this)`
 * (the `google-services` Gradle plugin also auto-initialises via a ContentProvider).
 */
class TransporteApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // TODO (Firebase): FirebaseApp.initializeApp(this)
    }
}
