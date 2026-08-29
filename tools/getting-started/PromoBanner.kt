package com.example.myapp.milano

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import dev.getmilano.MilanoAction
import dev.getmilano.MilanoEngine
import dev.getmilano.MilanoHost
import dev.getmilano.MilanoValue
import dev.getmilano.MilanoViewBuilder
import dev.getmilano.viewBuilder

/**
 * One engine for the whole app, created once with the vocabulary the
 * bridge implements; every screen builds its views from it.
 */
class Milano(private val context: Context) {
    private val engine: MilanoEngine by lazy {
        MilanoEngine(
            vocabularyJson = asset("milano/vocabulary.json"),
            registry = promoRegistry(),
        ).also { PromoVocabulary.assertMatches(it) }
        // Refuses to run against a vocabulary the bindings were not generated from.
    }

    /**
     * The banner: the document from the producer folder, copied into the
     * assets at build time, plus the context it declared and the handler
     * for its actions.
     */
    fun bannerBuilder(): MilanoViewBuilder =
        engine
            .viewBuilder(asset("milano/documents/banner.json"))
            .context(mapOf("userName" to MilanoValue.StringValue("Ada")))
            .actionHandler { action -> handle(action) }
            .label("banner")

    /**
     * The single funnel for custom actions. The gate proved `url` is a
     * string; whether it is safe to open is the app's decision.
     */
    private fun handle(action: MilanoAction): MilanoValue? {
        when (val decoded = PromoAction.from(action)) {
            is PromoAction.OpenUrl -> {
                val uri = Uri.parse(decoded.url)
                if (uri.scheme == "https") {
                    context.startActivity(Intent(Intent.ACTION_VIEW, uri).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                }
            }
            is PromoAction.Unrecognized -> println("unhandled action ${decoded.action.name}")
        }
        return null
    }

    private fun asset(name: String): String = context.assets.open(name).bufferedReader().use { it.readText() }
}

/** Drop it into any screen: the banner renders where this composable sits. */
@Composable
fun PromoBanner(milano: Milano) {
    val builder = remember { milano.bannerBuilder() }
    MilanoHost(
        builder = builder,
        loading = { CircularProgressIndicator() },
        failure = { /* an optional surface fails to nothing */ },
    )
}
