// The engine takes one function handler; it answers every function the
// vocabulary declares, for every view built from this engine.
val engine =
    MilanoEngine(
        vocabularyJson = vocabulary,
        registry = promoRegistry(),
        functionHandler =
            MilanoFunctionHandler { call ->
                when (call.name) {
                    "formatMoney" -> {
                        val cents = call.arguments[0].intOrNull ?: 0L
                        val currency = call.arguments[1].stringOrNull ?: "EUR"
                        val format = NumberFormat.getCurrencyInstance()
                        format.currency = Currency.getInstance(currency)
                        MilanoValue.StringValue(format.format(cents / 100.0))
                    }
                    else -> null
                }
            },
    )
