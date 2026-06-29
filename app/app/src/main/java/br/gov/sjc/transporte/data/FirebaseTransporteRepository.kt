package br.gov.sjc.transporte.data

import br.gov.sjc.transporte.domain.model.Motorista
import br.gov.sjc.transporte.domain.model.Role
import br.gov.sjc.transporte.domain.model.Secretaria
import br.gov.sjc.transporte.domain.model.Usuario
import br.gov.sjc.transporte.domain.model.Veiculo
import br.gov.sjc.transporte.domain.model.Viagem
import kotlinx.coroutines.flow.Flow

/**
 * SKELETON — Firestore-backed implementation. NOT wired up yet (the app uses
 * [MockTransporteRepository] via [RepositoryProvider]). Every method below documents the
 * intended Firestore operation so the migration is mechanical.
 *
 * To enable:
 *  1. Uncomment the Firebase dependencies in `app/build.gradle.kts` and the version-catalog
 *     entries, and add the `com.google.gms.google-services` plugin + `google-services.json`.
 *  2. Implement the bodies below (replace each `TODO`). Collection names mirror the contract:
 *     `secretarias` (id = codigo), `usuarios` (id = uid), `motoristas`, `veiculos`, `viagens`.
 *  3. Convert dates at this boundary: Firestore `Timestamp` (UTC) <-> `LocalDateTime`.
 *  4. Flip the single switch in [RepositoryProvider].
 *
 * Reactive reads should be built with `callbackFlow { ... addSnapshotListener ... }`; writes
 * with `collection.document(id).set/update(...).await()` (kotlinx-coroutines-play-services).
 */
class FirebaseTransporteRepository : TransporteRepository {

    // Example wiring once Firebase is added:
    // private val db = com.google.firebase.firestore.ktx.firestore (Firebase.firestore)
    // private val viagens get() = db.collection("viagens")

    override fun observarSecretarias(): Flow<List<Secretaria>> {
        // TODO: Firestore — callbackFlow over db.collection("secretarias").addSnapshotListener
        TODO("Firestore: observe collection 'secretarias'")
    }

    override suspend fun getSecretarias(): List<Secretaria> {
        // TODO: Firestore — db.collection("secretarias").get().await().toObjects(...)
        TODO("Firestore: get 'secretarias'")
    }

    override suspend fun getUsuarios(): List<Usuario> {
        // TODO: Firestore — db.collection("usuarios").get().await()
        TODO("Firestore: get 'usuarios'")
    }

    override suspend fun getUsuarioPorEmail(email: String): Usuario? {
        // TODO: Firestore — usuarios.whereEqualTo("email", email).limit(1).get().await()
        // NOTE: real auth is Firebase Auth (email/senha, @sjc.sp.gov.br); this is the profile doc.
        TODO("Firestore: query 'usuarios' by email")
    }

    override suspend fun getUsuariosPorRole(role: Role): List<Usuario> {
        // TODO: Firestore — usuarios.whereEqualTo("role", role.name).get().await()
        TODO("Firestore: query 'usuarios' by role")
    }

    override fun observarMotoristas(): Flow<List<Motorista>> {
        // TODO: Firestore — callbackFlow over collection("motoristas")
        TODO("Firestore: observe 'motoristas'")
    }

    override suspend fun getMotoristas(secretariaId: Int?): List<Motorista> {
        // TODO: Firestore — optionally whereEqualTo("secretariaId", secretariaId)
        TODO("Firestore: get 'motoristas'")
    }

    override suspend fun getMotoristaPorUsuario(usuarioId: String): Motorista? {
        // TODO: Firestore — motoristas.whereEqualTo("usuarioId", usuarioId).limit(1).get().await()
        TODO("Firestore: query 'motoristas' by usuarioId")
    }

    override fun observarVeiculos(): Flow<List<Veiculo>> {
        // TODO: Firestore — callbackFlow over collection("veiculos")
        TODO("Firestore: observe 'veiculos'")
    }

    override suspend fun getVeiculos(secretariaId: Int?): List<Veiculo> {
        // TODO: Firestore — optionally whereEqualTo("secretariaId", secretariaId)
        TODO("Firestore: get 'veiculos'")
    }

    override fun observarViagens(): Flow<List<Viagem>> {
        // TODO: Firestore — callbackFlow over collection("viagens").orderBy("dataHoraSaida")
        TODO("Firestore: observe 'viagens'")
    }

    override fun observarViagensPorSolicitante(solicitanteId: String): Flow<List<Viagem>> {
        // TODO: Firestore — viagens.whereEqualTo("solicitanteId", solicitanteId)
        //                          .orderBy("criadoEm", DESCENDING) (see firestore.indexes.json)
        TODO("Firestore: observe 'viagens' by solicitanteId")
    }

    override fun observarViagensPorMotorista(motoristaId: String): Flow<List<Viagem>> {
        // TODO: Firestore — viagens.whereEqualTo("motoristaId", motoristaId)
        //                          .orderBy("dataHoraSaida")
        TODO("Firestore: observe 'viagens' by motoristaId")
    }

    override suspend fun criarViagem(viagem: Viagem): Viagem {
        // TODO: Firestore — val ref = viagens.document(); ref.set(viagem.copy(id = ref.id)).await()
        TODO("Firestore: create 'viagens' doc")
    }

    override suspend fun atualizarViagem(viagem: Viagem) {
        // TODO: Firestore — viagens.document(viagem.id).set(viagem).await()
        TODO("Firestore: set 'viagens' doc")
    }

    override suspend fun cancelarViagem(viagemId: String) {
        // TODO: Firestore — viagens.document(viagemId).update("status", "CANCELADA", ...).await()
        TODO("Firestore: cancel viagem")
    }

    override suspend fun aceitarViagem(
        viagemId: String,
        motoristaId: String,
        veiculoId: String,
        decididoPor: String,
    ) {
        // TODO: Firestore — update status=ACEITA + motoristaId + veiculoId + decididoPor/Em.
        // The double-booking conflict check is server-trusted (web/domain); the app only requests.
        TODO("Firestore: accept viagem")
    }

    override suspend fun rejeitarViagem(viagemId: String, motivo: String, decididoPor: String) {
        // TODO: Firestore — update status=REJEITADA + motivoRejeicao + decididoPor/Em.
        TODO("Firestore: reject viagem")
    }

    override suspend fun iniciarViagem(viagemId: String) {
        // TODO: Firestore — update status=EM_ANDAMENTO (rules: motoristaId == self).
        TODO("Firestore: start viagem")
    }

    override suspend fun concluirViagem(viagemId: String) {
        // TODO: Firestore — update status=CONCLUIDA (rules: motoristaId == self).
        TODO("Firestore: finish viagem")
    }
}
