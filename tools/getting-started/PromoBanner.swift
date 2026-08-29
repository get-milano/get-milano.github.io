import MilanoSDK
import SwiftUI

/// One engine for the whole app, created once with the vocabulary the
/// bridge implements; every screen builds its views from it.
enum Milano {
    static let engine: MilanoEngine = {
        do {
            let engine = try MilanoEngine(
                vocabularyJSON: resource("vocabulary"),
                registry: PromoBridge.registry())
            // Refuses to run against a vocabulary the bindings were not generated from.
            PromoVocabulary.assertMatches(engine)
            return engine
        } catch {
            fatalError("Milano setup failed: \(error)")
        }
    }()

    /// The banner: the document from the producer folder, bundled with
    /// the app, plus the context it declared and the handler for its actions.
    static func bannerBuilder() -> MilanoViewBuilder {
        engine.viewBuilder(document: resource("banner"))
            .context(["userName": .string("Ada")])
            .actionHandler(handle(_:))
            .label("banner")
    }

    /// The single funnel for custom actions. The gate proved `url` is a
    /// string; whether it is safe to open is the app's decision.
    @Sendable static func handle(_ action: MilanoAction) async throws -> MilanoValue? {
        switch PromoAction(action) {
        case .openUrl(let url):
            guard let url = URL(string: url), url.scheme == "https" else { return nil }
            await open(url)
        case .unrecognized(let action):
            print("unhandled action \(action.name)")
        }
        return nil
    }

    @MainActor private static func open(_ url: URL) {
        #if canImport(UIKit)
        UIApplication.shared.open(url)
        #else
        print("open \(url)")
        #endif
    }

    private static func resource(_ name: String) -> Data {
        guard let url = Bundle.main.url(forResource: name, withExtension: "json"),
              let data = try? Data(contentsOf: url)
        else { fatalError("\(name).json is not in the app bundle; add it to the target") }
        return data
    }
}

/// Drop it into any screen: the banner renders where this view sits.
struct PromoBannerView: View {
    var body: some View {
        MilanoHost(builder: Milano.bannerBuilder()) {
            ProgressView()
        } failure: { _ in
            EmptyView()   // an optional surface fails to nothing
        }
    }
}
