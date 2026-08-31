repositories {
    mavenCentral()
}

dependencies {
    implementation("dev.get-milano:engine-compose:2.1.0")
    implementation("io.coil-kt:coil-compose:2.7.0")   // the image loader the bridge below uses
}

// The producer folder's files travel with the app: copied into the assets
// before every build, so an edited document is in the next build.
val copyMilanoDocuments by tasks.registering(Copy::class) {
    from("../milano") { include("vocabulary.json", "documents/banner.json") }
    into("src/main/assets/milano")
}
tasks.named("preBuild") { dependsOn(copyMilanoDocuments) }
