// The engine takes one function handler; it answers every function the
// vocabulary declares, for every view built from this engine.
let engine = try MilanoEngine(
    vocabularyJson: vocabulary,
    registry: PromoBridge.registry(),
    functionHandler: MilanoClosureFunctionHandler { call in
        switch call.name {
        case "formatMoney":
            let cents = call.arguments[0].intValue ?? 0
            let currency = call.arguments[1].stringValue ?? "EUR"
            let formatter = NumberFormatter()
            formatter.numberStyle = .currency
            formatter.currencyCode = currency
            let amount = NSNumber(value: Double(cents) / 100)
            return .string(formatter.string(from: amount) ?? "")
        default:
            return .null
        }
    }
)
