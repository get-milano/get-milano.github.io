package com.example.myapp.milano

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import dev.getmilano.MilanoNode
import dev.getmilano.MilanoRegistry
import dev.getmilano.MilanoRenderer

/**
 * The bridge: one renderer per vocabulary type, each mapping a typed node
 * onto a composable the app already has. Milano draws nothing itself.
 */
fun promoRegistry(): MilanoRegistry {
    val registry = MilanoRegistry()
    registry.register("Column", ColumnRenderer)
    registry.register("Text", TextRenderer)
    registry.register("Image", ImageRenderer)
    registry.register("Button", ButtonRenderer)
    return registry
}

object ColumnRenderer : MilanoRenderer {
    @Composable
    override fun Render(node: MilanoNode) {
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier.padding(16.dp),
        ) {
            for (child in node.children) {
                key(child.key) { child.Render() }
            }
        }
    }
}

object TextRenderer : MilanoRenderer {
    @Composable
    override fun Render(node: MilanoNode) {
        val text = PromoTextNode(node)
        when (text.role) {
            PromoTextRole.Title -> Text(text.text, style = MaterialTheme.typography.titleLarge)
            PromoTextRole.Body ->
                Text(
                    text.text,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
        }
    }
}

object ImageRenderer : MilanoRenderer {
    @Composable
    override fun Render(node: MilanoNode) {
        val image = PromoImageNode(node)
        var modifier: Modifier = Modifier.fillMaxWidth()
        image.height?.let { modifier = modifier.height(it.toInt().dp) }
        image.cornerRadius?.let { modifier = modifier.clip(RoundedCornerShape(it.toInt().dp)) }
        AsyncImage(
            model = image.url,
            contentDescription = null,
            contentScale = ContentScale.Crop,
            modifier = modifier,
        )
    }
}

object ButtonRenderer : MilanoRenderer {
    @Composable
    override fun Render(node: MilanoNode) {
        val button = PromoButtonNode(node)
        Button(onClick = { button.emitTap() }, enabled = button.enabled) {
            Text(button.label)
        }
    }
}
