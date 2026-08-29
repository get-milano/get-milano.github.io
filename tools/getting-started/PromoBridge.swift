import MilanoSDK
import SwiftUI

/// The bridge: one renderer per vocabulary type, each mapping a typed node
/// onto a view the app already has. Milano draws nothing itself.
enum PromoBridge {
    static func registry() -> MilanoRegistry {
        var registry = MilanoRegistry()
        registry.register(ColumnRenderer(), for: "Column")
        registry.register(TextRenderer(), for: "Text")
        registry.register(ImageRenderer(), for: "Image")
        registry.register(ButtonRenderer(), for: "Button")
        return registry
    }
}

final class ColumnRenderer: MilanoRenderer {
    func render(_ node: MilanoNode) -> AnyView {
        AnyView(
            VStack(alignment: .leading, spacing: 12) {
                ForEach(node.children) { $0 }
            }
            .padding(16)
        )
    }
}

final class TextRenderer: MilanoRenderer {
    func render(_ node: MilanoNode) -> AnyView {
        let text = PromoTextNode(node)
        switch text.role {
        case .title:
            return AnyView(Text(text.text).font(.title2.bold()))
        case .body:
            return AnyView(Text(text.text).font(.body).foregroundStyle(.secondary))
        }
    }
}

final class ImageRenderer: MilanoRenderer {
    func render(_ node: MilanoNode) -> AnyView {
        let image = PromoImageNode(node)
        return AnyView(
            AsyncImage(url: URL(string: image.url)) { phase in
                if case .success(let loaded) = phase {
                    loaded.resizable().scaledToFill()
                } else {
                    Color.gray.opacity(0.2)
                }
            }
            .frame(height: image.height.map(CGFloat.init))
            .clipShape(RoundedRectangle(cornerRadius: CGFloat(image.cornerRadius ?? 0)))
        )
    }
}

final class ButtonRenderer: MilanoRenderer {
    func render(_ node: MilanoNode) -> AnyView {
        let button = PromoButtonNode(node)
        return AnyView(
            Button(button.label) { button.emitTap() }
                .buttonStyle(.borderedProminent)
                .disabled(!button.enabled)
        )
    }
}
