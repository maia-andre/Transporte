plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "br.gov.sjc.transporte"
    compileSdk = 34

    defaultConfig {
        applicationId = "br.gov.sjc.transporte"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"

        // Vector drawables are used for the launcher icon and in-app glyphs.
        vectorDrawables { useSupportLibrary = true }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
    }

    compileOptions {
        // Required for java.time on minSdk 24 (see coreLibraryDesugaring below).
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = libs.versions.composeCompiler.get()
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)

    // Compose BOM keeps all Compose artifacts on a single, compatible version set.
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.navigation.compose)

    implementation(libs.kotlinx.coroutines.android)

    // Enables java.time.* (LocalDateTime/LocalDate) and other Java 8+ APIs on API 24/25.
    coreLibraryDesugaring(libs.desugar.jdk.libs)

    debugImplementation(libs.androidx.ui.tooling)

    // JVM unit tests (run with: ./gradlew test)
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)

    // ---------------------------------------------------------------------------
    // FIREBASE — intentionally disabled for now. The app runs entirely on the
    // in-memory MockTransporteRepository. To go live, see app/README.md
    // ("Firebase switch point"), uncomment the lines below, add google-services.json,
    // and apply the google-services Gradle plugin.
    //
    // implementation(platform(libs.firebase.bom))
    // implementation(libs.firebase.firestore)
    // implementation(libs.firebase.auth)
    // implementation(libs.firebase.messaging)
    // ---------------------------------------------------------------------------
}
