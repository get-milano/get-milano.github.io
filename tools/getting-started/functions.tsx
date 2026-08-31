// The engine takes one function handler; it answers every function the
// vocabulary declares, for every view built from this engine.
const engine = new MilanoEngine({
  vocabularyJson: vocabulary,
  registry: promoRegistry(),
  functionHandler: (call) => {
    if (call.name !== "formatMoney") return null;
    const [cents, currency] = call.arguments;
    return MilanoValue.string(
      new Intl.NumberFormat(undefined, {
        style: "currency",
        currency: currency.stringValue ?? "EUR",
      }).format(Number(cents.intValue ?? 0n) / 100),
    );
  },
});
