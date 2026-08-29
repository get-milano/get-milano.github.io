# The getting-started page, generated

`../../getting-started/index.html` is generated from the files here, so the
code the tutorial shows is code that was checked against the SDK rather
than typed into HTML:

- `vocabulary.json`, `documents/banner.json`: validated with
  `milano validate`; the bindings the page describes come from
  `milano bindings` over this vocabulary (`--swift-prefix Promo`,
  `--kotlin-package com.example.myapp.milano --kotlin-prefix Promo`,
  `--ts-prefix Promo`).
- `PromoBridge.swift`, `PromoBanner.swift`: typechecked with
  `swiftc -typecheck -I sdk/.build/debug/Modules` after `swift build` at the
  SDK root, together with the generated `PromoBindings.swift`.
- `PromoBridge.kt`, `PromoBanner.kt`, `app.build.gradle.kts`: compiled by
  dropping them (package rewritten) into the SDK's Android sample and running
  `:app:compileDebugKotlin`; the Gradle copy task was run in the same sample.
- `bridge.tsx`, `banner.tsx`: typechecked by dropping them into the SDK's
  React Native sample and running its `tsc`.
- `page-template.html`: the page around the steps; `generate.py` fills in
  the steps, highlights the code (JSON, Swift, Kotlin, Gradle, TypeScript,
  terminal), and writes the page.

Regenerate after editing anything here, from the repository root:

```sh
python3 tools/getting-started/generate.py .
```

When the SDK's renderer, host, or builder APIs change, re-verify the
snippets the same way before regenerating. The prose in the template and
the generator holds the no-em-dash rule by hand, like the rest of the site.
