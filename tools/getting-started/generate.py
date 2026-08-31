import html, json, pathlib, re, sys
S = pathlib.Path(__file__).resolve().parent
SITE = pathlib.Path(sys.argv[1])
E = html.escape
NL = "\n"
read = lambda name: (S / name).read_text()
swift_wiring = re.sub(r"        #if canImport\(UIKit\)\n        UIApplication\.shared\.open\(url\)\n        #else\n        print\(\"open \\\(url\)\"\)\n        #endif\n",
                      "        UIApplication.shared.open(url)\n", read("PromoBanner.swift"))
assert "canImport" not in swift_wiring

def hl_json(text):
    out = []
    tokens = re.compile(r'"(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?|true|false|null|[{}\[\]:,]|\s+|.').findall(text)
    for i, tok in enumerate(tokens):
        if tok.startswith('"'):
            is_key = "".join(tokens[i + 1:i + 3]).lstrip().startswith(":")
            if tok == '"$expr"' or (not is_key and i >= 2 and tokens[i - 2] == '"$expr"'):
                out.append(f'<span class="tk-expr">{E(tok)}</span>')
            elif is_key: out.append(f'<span class="tk-key">{E(tok)}</span>')
            else: out.append(f'<span class="tk-str">{E(tok)}</span>')
        elif re.fullmatch(r"-?\d+(?:\.\d+)?", tok): out.append(f'<span class="tk-num">{tok}</span>')
        elif tok in ("true", "false", "null"): out.append(f'<span class="tk-kw">{tok}</span>')
        else: out.append(E(tok))
    return "".join(out)

def code_highlighter(keywords):
    token = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`|[A-Za-z_$][A-Za-z0-9_]*|\d+|\s+|.')
    def hl(text):
        out = []
        for tok in token.findall(text):
            if tok.startswith("//") or tok.startswith("/*"): out.append(f'<span class="tk-cm">{E(tok)}</span>')
            elif tok[0] in '"`': out.append(f'<span class="tk-str">{E(tok)}</span>')
            elif tok in keywords: out.append(f'<span class="tk-kw">{tok}</span>')
            elif re.fullmatch(r"[A-Z][A-Za-z0-9_]*", tok): out.append(f'<span class="tk-type">{tok}</span>')
            elif re.fullmatch(r"\d+", tok): out.append(f'<span class="tk-num">{tok}</span>')
            else: out.append(E(tok))
        return "".join(out)
    return hl

hl_swift = code_highlighter({"import","enum","struct","final","class","func","var","let","static","private","return","switch","case","guard","else","if","in","await","async","throws","try","do","catch","some","self","nil","default"})
hl_kotlin = code_highlighter({"package","import","class","object","fun","val","var","override","when","is","null","return","private","by","lazy","also","if","else","for","in","true","false","suspend","to"})
hl_ts = code_highlighter({"import","export","from","const","let","function","return","async","await","new","if","else","switch","case","null","true","false","type","default"})
hl_gradle = code_highlighter({"val","by","repositories","dependencies","maven","credentials","implementation","tasks","from","into","include","dependsOn"})

def hl_sh(text):
    out, continuing = [], False
    for line in text.rstrip().split("\n"):
        if continuing or re.match(r"^(cd|npx|npm|git|node)\b", line):
            out.append(("" if continuing else '<span class="prompt">$ </span>') + E(line)); continuing = line.endswith("\\")
        elif "SchemaViolation" in line or line.startswith("error:"): out.append(f'<span class="err">{E(line)}</span>')
        else: out.append(f'<span class="out">{E(line)}</span>')
    return "\n".join(out)

HL = {"json": (hl_json, "JSON"), "swift": (hl_swift, "Swift"), "kotlin": (hl_kotlin, "Kotlin"), "gradle": (hl_gradle, "Gradle"), "tsx": (hl_ts, "TypeScript"), "sh": (hl_sh, "Terminal")}
def box(lang, text, path=""):
    hl, label = HL[lang]
    return (f'<figure class="code"><figcaption><span class="lang">{label}</span><span class="path">{E(path)}</span>'
            f'<button type="button" class="copy">Copy</button></figcaption><pre><code>{hl(text.rstrip())}</code></pre></figure>')

PLATFORMS = [("swiftui", "SwiftUI"), ("compose", "Compose"), ("react", "React Native")]
def switcher():
    buttons = "".join(f'<button type="button" role="tab" data-platform="{key}" aria-selected="{"true" if key == "swiftui" else "false"}">{label}</button>' for key, label in PLATFORMS)
    return f'<div class="platform-switch" role="tablist" aria-label="Your app">{buttons}</div>'
def tabs(**content):
    return NL.join(f'<div class="tab" data-platform="{key}"{"" if key == "swiftui" else " hidden"}>{content[key]}</div>' for key, _ in PLATFORMS)
def step(n, title, body):
    return f'<section class="step" id="step-{n}">{NL}            <div class="step-head"><span class="badge">{n}</span><h2>{title}</h2></div>{NL}{body}{NL}          </section>'

SH_INIT = "cd MyApp" + NL + "npx @get-milano/cli init milano --name promo" + NL + "cd milano && npm install && npm run check"
SH_CHECK = "npm run check" + NL + "documents/banner.json: valid" + NL + "documents/welcome.json: valid"
SH_BROKEN = "npm run check" + NL + "documents/banner.json: SchemaViolation: schema violation (property-type) at root/children[1]: expected enum, found string"
SH_DIFF = "npx milano diff vocabulary-1.0.0.json vocabulary.json" + NL + "ADDITIVE  Text property maxLines added" + NL + "verdict: ok (0 breaking, 1 additive)"
BIND = {
 "swiftui": "npx milano bindings vocabulary.json \\" + NL + "    --swift-prefix Promo \\" + NL + "    --swift-out ../MyApp/Milano/PromoBindings.swift",
 "compose": "npx milano bindings vocabulary.json \\" + NL + "    --kotlin-package com.example.myapp.milano --kotlin-prefix Promo \\" + NL + "    --kotlin-out ../app/src/main/kotlin/com/example/myapp/milano/PromoBindings.kt",
 "react": "npx milano bindings vocabulary.json \\" + NL + "    --ts-prefix Promo \\" + NL + "    --ts-out ../src/milano/bindings.ts",
}
GRADLE = read("app.build.gradle.kts")
SPM = "dependencies: [" + NL + '    .package(url: "https://github.com/get-milano/sdk.git", from: "2.1.0")' + NL + "]"

def validated():
    """Every document here, through the reference gate, against this
    vocabulary. The page teaches what the gate accepts or it teaches
    nothing; the specs' checker is the same one the suite runs."""
    import os
    specs = pathlib.Path(os.environ.get("MILANO_SPECS_DIR", S.parents[2] / "specs"))
    checker = specs / "tools" / "reference_check.py"
    if not checker.is_file():
        print(f"note: no specs checkout at {specs}; documents not validated")
        return
    sys.path.insert(0, str(specs / "tools"))
    import reference_check as rc
    vocabulary = json.loads(read("vocabulary.json"))
    for path in sorted((S / "documents").glob("*.json")):
        document = json.loads(path.read_text())
        gate = rc.ReferenceGate(vocabulary, "fail")
        # No app here, so a declared function answers with the zero value of
        # its return type, as `milano validate` does for a producer.
        gate.function_results = None
        gate.build({"name": path.name, "document": document,
                    "context": rc.synthesized_values(document.get("context", {})),
                    "state": rc.synthesized_values(document.get("state", {}))})
    print("validated", len(list((S / "documents").glob("*.json"))), "documents")


validated()

FUNCTION_DECLARATION = ("{" + NL +
 '  "functions": {' + NL +
 '    "formatMoney": { "arguments": ["int", "string"], "returns": "string" }' + NL +
 "  }" + NL + "}")

FUNCTIONS = {
 "swiftui": read("PromoFunctions.swift"),
 "compose": read("PromoFunctions.kt"),
 "react": read("functions.tsx"),
}
FUNCTION_TABS = tabs(swiftui=box("swift", FUNCTIONS["swiftui"]),
                     compose=box("kotlin", FUNCTIONS["compose"]),
                     react=box("tsx", FUNCTIONS["react"]))

steps = [
("Start the producer folder", f'''
            <p>Inside the app's repository, next to the project, let the CLI scaffold a folder for the documents:</p>
            {box("sh", SH_INIT)}
            <p><code>milano init</code> writes a working producer setup and <code>npm run check</code> proves it: the schema for your editor is regenerated and every document is validated with the gate the engines run. The folder contains:</p>
            <table>
              <tr><th>File</th><th>What it is</th></tr>
              <tr><td><code>vocabulary.json</code></td><td>The contract between producer and app: component types, their properties and events, the custom actions.</td></tr>
              <tr><td><code>documents/welcome.json</code></td><td>A first document using the starter vocabulary. The banner goes next to it.</td></tr>
              <tr><td><code>documents.schema.json</code>, <code>.vscode/settings.json</code></td><td>The document schema specialized to your vocabulary, and the editor settings pointing at it, so typos get red squiggles as you type.</td></tr>
              <tr><td><code>package.json</code></td><td><code>validate</code>, <code>schema</code>, and <code>check</code> scripts running the CLI.</td></tr>
              <tr><td><code>AGENTS.md</code>, <code>CLAUDE.md</code>, <code>.claude/skills/</code></td><td>The authoring rules for an AI agent working in the folder, and the instruction to run the check after every change.</td></tr>
            </table>
            <p>These files are what the app will bundle in step 5: the vocabulary it registers renderers for, and the documents it renders. They stay in <code>milano/</code>, and the app reads them from there.</p>'''),
("Declare the vocabulary", f'''
            <p>The vocabulary names what documents may use. The banner needs a column, text, an image, and a button, plus one action for the button to request. Replace <code>vocabulary.json</code> with:</p>
            {box("json", read("vocabulary.json"), "milano/vocabulary.json")}
            <p>Each property has a type: <code>"int?"</code> is an optional integer, the <code>enum</code> is a closed set of values, and <code>"tap": null</code> declares an event with no payload. The action takes one parameter. Run <code>npm run check</code> again: the schema follows the new vocabulary, and <code>welcome.json</code> still validates, since everything it used is still declared.</p>'''),
("Write the banner", f'''
            {box("json", read("documents/banner.json"), "milano/documents/banner.json")}
            <p>Three things to notice. The title is an <strong>expression</strong>: the <code>$expr</code> wrapper reads <code>context.userName</code>, a value the app injects, and the document declares that it needs it under <code>context</code>. The button's <code>on.tap</code> binds the event to the <code>openUrl</code> action with its parameter. And <code>vocabulary.min</code> says which vocabulary the document was written for, so an app holding an older one fails the build with a typed error instead of rendering the wrong thing.</p>
            {box("sh", SH_CHECK)}
            <div class="callout">
              <div class="title">Try it</div>
              <p>Change the title's <code>role</code> to <code>"headline"</code> and run the check. The gate answers with the rule it applied, the node (by path, since that node has no <code>id</code>), and what it expected:</p>
              {box("sh", SH_BROKEN)}
              <p>That is the same message the app would report, which is the point of running it here first. Put the <code>role</code> back.</p>
            </div>
            <p>Everything so far is the producer's side, and it is the same whatever the app is built with. The next four steps are the app's side, in the platform picked at the top of the page.</p>'''),
("Generate the bindings", f'''
            <p>The vocabulary is machine-readable, so the app does not have to read properties by string. One command turns it into typed code, written straight into the app's source tree:</p>
            {tabs(
swiftui=f"""{box("sh", BIND["swiftui"])}
            <p>The file holds one wrapper per component (<code>PromoTextNode</code> with <code>text</code> and <code>role</code>, <code>PromoImageNode</code>, <code>PromoButtonNode</code> with <code>emitTap()</code>), a Swift enum per declared enum (<code>PromoTextRole</code>), an exhaustive <code>PromoAction</code> with an <code>unrecognized</code> case, and <code>PromoVocabulary.assertMatches</code>.</p>""",
compose=f"""{box("sh", BIND["compose"])}
            <p>The file holds one wrapper per component (<code>PromoTextNode</code> with <code>text</code> and <code>role</code>, <code>PromoImageNode</code>, <code>PromoButtonNode</code> with <code>emitTap()</code>), an enum class per declared enum (<code>PromoTextRole</code>), a sealed <code>PromoAction</code> with <code>OpenUrl</code> and <code>Unrecognized</code> and a <code>from(action)</code> decoder, and <code>PromoVocabulary.assertMatches</code>.</p>""",
react=f"""{box("sh", BIND["react"])}
            <p>The file holds one wrapper per component (<code>PromoTextNode</code> with <code>text</code> and <code>role</code>, <code>PromoImageNode</code>, <code>PromoButtonNode</code> with <code>emitTap()</code>), a string-literal union per declared enum (<code>PromoTextRole</code>), a discriminated <code>PromoAction</code> union with a <code>promoAction(action)</code> decoder, and <code>PromoVocabulary.assertMatches</code>. It imports only <code>@get-milano/core</code>.</p>""")}
            <p>A property the vocabulary declares non-optional is a non-optional property in the generated code: the gate guarantees it is there. Commit the file, and regenerate it whenever the vocabulary changes; the compiler then lists every place in the app the change touches.</p>'''),
("Add the SDK and the producer files to the app", tabs(
swiftui=f"""<p>In Xcode, File, Add Package Dependencies, and enter the repository URL; choose "Up to Next Major" from <code>2.1.0</code> and add the <code>MilanoSDK</code> product to the app target. In a <code>Package.swift</code> it is:</p>
            {box("swift", SPM, "Package.swift")}
            <p>A tagged release resolves to a prebuilt, signed <code>MilanoSDK.xcframework</code>. Then add <code>milano/vocabulary.json</code> and <code>milano/documents/banner.json</code> to the app target: drag them into the project navigator, tick the target, and leave "Copy items if needed" unchecked, so the project references the files where the CLI wrote them. Xcode copies them into the bundle at build time, and an edited document is in the next build.</p>""",
compose=f"""<p>The engine is on Maven Central, so nothing but <code>mavenCentral()</code> is needed. In the app module's <code>build.gradle.kts</code>, the dependencies and a copy task that carries the producer folder's files into the assets before every build:</p>
            {box("gradle", GRADLE, "app/build.gradle.kts")}
            <p>Two other ways in, if you need them: every release also goes to GitHub Packages (whose Maven registry wants a token with <code>read:packages</code> even for public artifacts), and carries <code>engine-compose-android-2.1.0.aar</code> on the release page to drop into <code>libs/</code>. A checkout of the SDK can be consumed from source with <code>includeBuild</code>. The copy task keeps the app's <code>assets/milano/</code> equal to the two files in <code>milano/</code>, so an edited document is in the next build and nothing is duplicated by hand.</p>""",
react=f"""{box("sh", "npm install @get-milano/core @get-milano/react")}
            <p>Two packages and nothing native: no autolinking, no pod install, because Milano draws nothing. The same two serve React on the web; only the components in the bridge change. The app imports the vocabulary and the banner straight from <code>milano/</code> as JSON modules (<code>resolveJsonModule</code>), which is fine for this document since all its numbers are integers.</p>
            <div class="callout note">
              <div class="title">Doubles in documents</div>
              <p>Milano distinguishes <code>int</code> from <code>double</code>, and <code>JSON.parse</code> does not: an imported <code>2.0</code> becomes <code>2</code>. Once a document carries doubles, bundle it as <strong>text</strong> (the React Native sample's <code>scripts/bundle-documents.mjs</code> shows how) and hand the string to the engine.</p>
            </div>""")),
("Bridge your views", f'''
            <p>A renderer is one function: node in, view out. Each one reads the typed node and returns a view the app already has, or the platform's plain components, as here. Milano never draws anything; this file is where your design system meets the document.</p>
            {tabs(
swiftui=box("swift", read("PromoBridge.swift"), "MyApp/Milano/PromoBridge.swift"),
compose=box("kotlin", read("PromoBridge.kt"), "app/src/main/kotlin/com/example/myapp/milano/PromoBridge.kt"),
react=box("tsx", read("bridge.tsx"), "src/milano/bridge.tsx"))}
            <p><code>node.children</code> are the column's materialized children, already renderable: the container only places them. The button's <code>emitTap()</code> puts the event into Milano's dispatch, which runs the actions the document bound to it.</p>'''),
("Create the engine and show the banner", f'''
            <p>One engine per app, created once with the vocabulary and the registry, then a builder per surface: the document, the context the document declared, and the handler for the actions it may request. Both files come from the producer folder the app bundled in step 5.</p>
            {tabs(
swiftui=f"""{box("swift", swift_wiring, "MyApp/Milano/PromoBanner.swift")}
            <p>Put <code>PromoBannerView()</code> wherever the banner belongs, a home screen, a list header, a sheet.</p>""",
compose=f"""{box("kotlin", read("PromoBanner.kt"), "app/src/main/kotlin/com/example/myapp/milano/PromoBanner.kt")}
            <p>Create one <code>Milano(applicationContext)</code> for the app (in your <code>Application</code> or your dependency graph) and put <code>PromoBanner(milano)</code> wherever the banner belongs, a home screen, a list header, a bottom sheet. Events and view updates run on the main thread by default.</p>""",
react=f"""{box("tsx", read("banner.tsx"), "src/milano/banner.tsx")}
            <p>Put <code>&lt;PromoBanner /&gt;</code> wherever the banner belongs. The builder is memoized because a new builder means a new build; <code>MilanoHost</code> subscribes to the view and tears it down when it unmounts.</p>""")}
            <p>Build and run: the image loads, the title reads "Summer sale, Ada", the button opens the offer. The handler is the last capability check: the gate proved <code>url</code> is a string, the app decides that only <code>https</code> leaves it. The failure content is where a rejected document lands; for an optional surface, nothing is the right thing to show.</p>'''),
("Everything else the contract gives you", f'''
            <p>The banner uses a fraction of what a document can do. Everything below is the same contract, needs no new app code beyond what a feature explicitly asks for, and is documented in full in the <a href="/sdk/">SDK guides</a>.</p>
            <p>This document is a small basket. It repeats a list with a stable identity per row, edits that list in place, keeps a derived count in step, reacts to being shown, and formats money through a function the app computes:</p>
            {box("json", read("documents/features.json"), "milano/documents/features.json")}
            <table>
              <tr><th>What it uses</th><th>What it is</th></tr>
              <tr><td><code>$repeat</code> with <code>key</code></td><td>One template per element of an array. The <code>key</code> makes a row's identity follow the element, so removing the first row does not renumber the rest. Without it, rows are identified by position.</td></tr>
              <tr><td><code>$append</code>, <code>$remove</code>, <code>$update</code></td><td>Change one element of a list in state: add, drop, or set one field. Inside the template, <code>item_index</code> is the row's position at the moment of the tap, so a row edits itself.</td></tr>
              <tr><td><code>watch</code></td><td>Action lists that run when a state key changes, as part of the change. Here it keeps <code>count</code> in step with the list. A watch never triggers another watch, so there is no cascade to reason about.</td></tr>
              <tr><td><code>on</code></td><td>Lifecycle bindings: <code>appear</code> when the host says the view is on screen, <code>disappear</code> when it leaves. The host container delivers both; Milano infers nothing.</td></tr>
              <tr><td><code>formatMoney(...)</code></td><td>A function your app computes, declared in the vocabulary and called by its bare name. The contract's own functions carry a <code>$</code> (<code>$concat</code>, <code>$str</code>, <code>$length</code>), so yours can be named anything, <code>round</code> included, without either shadowing the other.</td></tr>
            </table>
            <h3 class="plain">Declaring and using your own functions</h3>
            <p>Formatting is the usual reason: money, dates, plurals, units. The document should not carry locale rules, and Milano should not guess them, so the app computes them. Declare the function in the vocabulary, with its argument types and what it returns:</p>
            {box("json", FUNCTION_DECLARATION, "milano/vocabulary.json")}
            <p>Then give the engine one function handler. It answers every function the vocabulary declares, for every view that engine builds:</p>
            {switcher()}
            {FUNCTION_TABS}
            <p>Documents then call it like any other function: <code>formatMoney(item.cents, 'EUR')</code>. The gate checks the call against the declaration, so a wrong argument count or type fails the build rather than the screen. A function must be <strong>pure over its arguments</strong>: the same arguments always give the same value. That is why the locale is passed in from context rather than read inside the handler, and it is what lets the engine call it whenever a dependency changes.</p>
            <div class="callout note">
              <div class="title">While you are still writing documents</div>
              <p><code>npm run check</code> has no app to ask, so it answers every declared function with the zero value of its return type: an empty string here. The document is still fully type-checked; only the formatting is missing. The <a href="/playground/">playground</a> answers a small library of functions if you want to see values.</p>
            </div>
            <h3 class="plain">The rest, in one place</h3>
            <table>
              <tr><th>Feature</th><th>What it is for</th><th>Guide</th></tr>
              <tr><td>Typed results and failures</td><td>An action's handler answers with a value the document reads as <code>result</code>, or fails with a reason it reads as <code>failure</code>, so error copy lives in the document.</td><td><a href="/sdk/documents#failure-payloads">Writing documents</a></td></tr>
              <tr><td>Dispatch identity</td><td>Every dispatched action carries a process-unique <code>dispatchId</code>: the idempotency key for the request your handler makes.</td><td><a href="/sdk/bridge#the-action-funnel">Creating a bridge</a></td></tr>
              <tr><td>Document replacement</td><td><code>view.replace(document)</code> swaps a live view's document, keeping the state whose declaration is unchanged: hot reload, or a refreshed document, without losing what the user typed.</td><td><a href="/sdk/bridge#replacing-a-document">Creating a bridge</a></td></tr>
              <tr><td>Capability grants</td><td>A surface can narrow the actions a document may dispatch, or declare extra ones for itself, so a banner cannot reach what a settings screen can.</td><td><a href="/sdk/bridge#granting-capabilities-per-surface">Creating a bridge</a></td></tr>
              <tr><td>Context that changes</td><td>A context handle pushes new values into every live view: sign-in, feature flags, locale.</td><td><a href="/sdk/guidelines">Guidelines</a></td></tr>
              <tr><td>Analytics</td><td>Impressions, taps, dispatches, and outcomes arrive as structured records, with no document or renderer involvement.</td><td><a href="/sdk/analytics">Analytics</a></td></tr>
              <tr><td>Guardrails</td><td>Every rejection rule, every runtime occurrence, the limits, and the unknown-type policies.</td><td><a href="/sdk/guardrails">Guardrails</a></td></tr>
            </table>'''),
("Change the banner", f'''
            <p>Edit <code>milano/documents/banner.json</code>: new copy, a different image, a second line of text. Run <code>npm run check</code>, rebuild the app, and the change is on screen. No app code moved, because the app bundles the producer folder's files: from here on, changing what the banner says is a change in <code>milano/</code>, checked by the CLI, and the app is rebuilt with it.</p>
            <p>When the vocabulary itself changes (a new component, a new property), bump its version and let the CLI say whether the bump is right before the app team depends on it:</p>
            {box("sh", SH_DIFF)}
            <p>Additive changes need a minor bump, breaking ones a major, and documents declare the minimum they need, so an older app and a newer document never meet by accident. Regenerate the bindings, add the renderer for anything new, and the compiler walks you through the rest.</p>
            <div class="callout note">
              <div class="title">The same document, everywhere</div>
              <p>Switch the platform above and read steps 4 to 7 again: the vocabulary, the banner, and the check never changed. That is the contract: one document, validated once, rendered by whatever the app is built with.</p>
            </div>'''),
]
nav = NL.join(f'              <li><a href="#step-{i + 1}">{E(t)}</a></li>' for i, (t, _) in enumerate(steps))
body = (NL + NL + "          ").join(step(i + 1, E(t), b) for i, (t, b) in enumerate(steps))
template = read("page-template.html")
page = template.replace("@@nav@@", nav).replace("@@body@@", body)
assert "@@" not in page
(SITE / "getting-started/index.html").write_text(page)
print("written", len(page.splitlines()), "lines; em dashes:", page.count("—"), "; http mentions:", len(re.findall(r"fetch|URLSession|server", page)))
from html.parser import HTMLParser
class Check(HTMLParser):
    VOID = {"meta", "link", "img", "br", "hr", "input"}
    def __init__(self): super().__init__(); self.stack = []; self.errors = []
    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack or self.stack[-1] != tag: self.errors.append(f"{tag} at line {self.getpos()[0]}")
        else: self.stack.pop()
c = Check(); c.feed(page); print("unbalanced:", c.errors[:3], "still open:", c.stack)
