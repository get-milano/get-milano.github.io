import { createMilanoRegistry } from "@get-milano/react";
import type { MilanoReactRegistry, MilanoRenderer } from "@get-milano/react";
import { Image, Pressable, Text, View } from "react-native";

import { PromoButtonNode, PromoImageNode, PromoTextNode } from "./bindings.ts";

/**
 * The bridge: one renderer per vocabulary type, each mapping a typed node
 * onto a component the app already has. Milano draws nothing itself.
 */

const ColumnRenderer: MilanoRenderer = ({ node }) => (
  <View style={{ gap: 12, padding: 16 }}>{node.children}</View>
);

const TextRenderer: MilanoRenderer = ({ node }) => {
  const text = new PromoTextNode(node);
  if (text.role === "title") return <Text style={{ fontSize: 22, fontWeight: "700" }}>{text.text}</Text>;
  return <Text style={{ fontSize: 15, color: "#6b6b6b" }}>{text.text}</Text>;
};

const ImageRenderer: MilanoRenderer = ({ node }) => {
  const image = new PromoImageNode(node);
  return (
    <Image
      source={{ uri: image.url }}
      resizeMode="cover"
      style={{
        width: "100%",
        height: image.height === null ? 160 : Number(image.height),
        borderRadius: Number(image.cornerRadius ?? 0),
      }}
    />
  );
};

const ButtonRenderer: MilanoRenderer = ({ node }) => {
  const button = new PromoButtonNode(node);
  return (
    <Pressable
      accessibilityRole="button"
      disabled={!button.enabled}
      onPress={() => button.emitTap()}
      style={{
        alignSelf: "flex-start",
        backgroundColor: "#d12360",
        borderRadius: 999,
        paddingHorizontal: 18,
        paddingVertical: 10,
        opacity: button.enabled ? 1 : 0.5,
      }}
    >
      <Text style={{ color: "#fff", fontWeight: "600" }}>{button.label}</Text>
    </Pressable>
  );
};

export function promoRegistry(): MilanoReactRegistry {
  const registry = createMilanoRegistry();
  registry.register("Column", ColumnRenderer);
  registry.register("Text", TextRenderer);
  registry.register("Image", ImageRenderer);
  registry.register("Button", ButtonRenderer);
  return registry;
}
