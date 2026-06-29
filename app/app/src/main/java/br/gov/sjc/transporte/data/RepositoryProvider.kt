package br.gov.sjc.transporte.data

/**
 * Tiny DI-lite service locator. Single source of the app's [TransporteRepository].
 *
 * ┌──────────────────────────────────────────────────────────────────────────────┐
 * │  FIREBASE SWITCH POINT                                                          │
 * │  Today the whole app runs on the in-memory mock. To go live with Firestore:    │
 * │    1) finish FirebaseTransporteRepository,                                      │
 * │    2) enable the Firebase deps in app/build.gradle.kts (+ google-services),     │
 * │    3) change the single line below to:                                          │
 * │         MockTransporteRepository()  ->  FirebaseTransporteRepository()          │
 * │  Nothing else in the app needs to change — everything depends on the interface. │
 * └──────────────────────────────────────────────────────────────────────────────┘
 */
object RepositoryProvider {

    @Volatile
    private var instance: TransporteRepository? = null

    /** The active repository, lazily created and cached. */
    fun repository(): TransporteRepository =
        instance ?: synchronized(this) {
            instance ?: createDefault().also { instance = it }
        }

    // <<< THE ONE LINE TO CHANGE FOR FIREBASE >>>
    private fun createDefault(): TransporteRepository = MockTransporteRepository()
    // private fun createDefault(): TransporteRepository = FirebaseTransporteRepository()

    /** Test/override hook (e.g. inject a fake in instrumentation tests). */
    fun override(repository: TransporteRepository) {
        instance = repository
    }
}
