// app/build.gradle.kts
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("androidx.navigation.safeargs.kotlin") // Ensure this is present
    id("com.google.gms.google-services")
    // Ensure 'kotlin-parcelize' is applied in your project-level build.gradle.kts
}

android {
    namespace = "com.nutrivision.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.nutrivision.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.core:core-splashscreen:1.0.1")
    implementation("androidx.appcompat:appcompat:1.7.1")
    implementation("com.google.android.material:material:1.13.0")
    implementation("androidx.constraintlayout:constraintlayout:2.2.1")

    // Firebase BoM (use the latest stable version)
    implementation(platform("com.google.firebase:firebase-bom:34.12.0"))

    // Firebase Auth & Firestore
    implementation("com.google.firebase:firebase-auth:24.0.1")
    implementation("com.google.firebase:firebase-firestore:26.2.0")

    // Firebase Generative AI (Gemini)
    implementation("com.google.firebase:firebase-ai:17.11.0")

    // Navigation component
    val nav_version = "2.9.7"
    implementation("androidx.navigation:navigation-fragment-ktx:$nav_version")
    implementation("androidx.navigation:navigation-ui-ktx:$nav_version")

    // Retrofit & OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Guava for ListenableFuture used by CameraX ProcessCameraProvider
    implementation("com.google.guava:guava:33.2.1-android")

    // CameraX
    val camerax_version = "1.3.1"
    implementation("androidx.camera:camera-core:${camerax_version}")
    implementation("androidx.camera:camera-camera2:${camerax_version}")
    implementation("androidx.camera:camera-lifecycle:${camerax_version}")
    implementation("androidx.camera:camera-view:${camerax_version}")

    // Image Loading
    implementation("io.coil-kt:coil:2.7.0")

    // Lottie for animations
    implementation("com.airbnb.android:lottie:6.7.1")

    // ML Kit for OCR
    implementation("com.google.mlkit:text-recognition:16.0.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-play-services:1.7.3")

    // Google Sign-In
    implementation("com.google.android.gms:play-services-auth:21.5.1")

    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}

// Ensure 'kotlin-parcelize' plugin is applied in your project-level build.gradle.kts:
// plugins {
//     id("com.android.application")
//     id("org.jetbrains.kotlin.android")
//     id("androidx.navigation.safeargs.kotlin")
//     id("com.google.gms.google-services")
//     id("kotlin-parcelize") // This line is crucial
// }