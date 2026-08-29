import { MilanoEngine, MilanoValue } from "@get-milano/core";
import type { MilanoAction } from "@get-milano/core";
import { MilanoHost } from "@get-milano/react";
import type { MilanoReactBuilder } from "@get-milano/react";
import { useMemo } from "react";
import type { ReactNode } from "react";
import { ActivityIndicator, Linking } from "react-native";

import { PromoVocabulary, promoAction } from "./bindings.ts";
import { promoRegistry } from "./bridge.tsx";
import banner from "../../milano/documents/banner.json";
import vocabulary from "../../milano/vocabulary.json";

/**
 * One engine for the whole app, created once with the vocabulary the
 * bridge implements; every screen builds its views from it.
 */
const engine = new MilanoEngine({ vocabularyJson: JSON.stringify(vocabulary), registry: promoRegistry() });
// Refuses to run against a vocabulary the bindings were not generated from.
PromoVocabulary.assertMatches(engine);

/**
 * The single funnel for custom actions. The gate proved `url` is a
 * string; whether it is safe to open is the app's decision.
 */
async function handle(action: MilanoAction): Promise<MilanoValue | null> {
  const decoded = promoAction(action);
  switch (decoded.kind) {
    case "openUrl":
      if (decoded.url.startsWith("https://")) await Linking.openURL(decoded.url);
      return null;
    case "unrecognized":
      console.log(`unhandled action ${decoded.action.name}`);
      return null;
  }
}

/**
 * The banner: the document from the producer folder, imported in place,
 * plus the context it declared and the handler for its actions.
 */
export function bannerBuilder(): MilanoReactBuilder {
  return engine
    .viewBuilder(JSON.stringify(banner))
    .context({ userName: MilanoValue.string("Ada") })
    .actionHandler(handle)
    .label("banner");
}

/** Drop it into any screen: the banner renders where this component sits. */
export function PromoBanner(): ReactNode {
  const builder = useMemo(() => bannerBuilder(), []);
  return <MilanoHost builder={builder} loading={<ActivityIndicator />} failure={() => null} />;
}
