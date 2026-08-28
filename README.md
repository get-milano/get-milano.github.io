# get-milano.dev

The landing page for Milano, served by GitHub Pages as the organization site. Static, no build step: `index.html` is the page, `styles.css` its stylesheet.

## Serving setup

- **Pages**: Settings → Pages → deploy from branch `main`, root. Being the org site (`get-milano.github.io`), it serves at the domain apex.
- **Custom domain**: `get-milano.dev` (the `CNAME` file in this repo). With the custom domain on this repo, the project sites are also reachable under it: [/specs/](https://get-milano.dev/specs/), [/sdk/](https://get-milano.dev/sdk/), [/playground/](https://get-milano.dev/playground/).
- **DNS**: apex `A` records to GitHub Pages (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) and a `CNAME` record for `www` pointing to `get-milano.github.io`. GitHub then redirects `www.get-milano.dev` to the apex automatically. Enable "Enforce HTTPS" once the certificate is issued.

## Files

- `index.html`: the page itself, no build step.
- `styles.css`: the one stylesheet, shared with `404.html` so the two pages cannot drift apart.
- `404.html`: branded not-found page, served by Pages for unmatched paths under the apex.
- `robots.txt`, `sitemap.xml`: crawl directives; the sitemap lists the apex plus `/sdk/`, `/specs/`, and `/playground/`. Update `lastmod` when the page changes materially.
- `site.webmanifest`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `favicon.ico`: icons and install metadata.
- `og-cover.png`: 1200×630 link preview used by `og:image` and `twitter:image`.
- Structured data (`Organization`, `WebSite`, `SoftwareApplication`, `FAQPage`) is a single JSON-LD block in `index.html`. Its questions and answers mirror the on-page "Questions" section; change both together, or the markup and the schema drift. It carries no `softwareVersion` on purpose: there is no build step to stamp one, so it would only ever be stale; the `releaseNotes` link points at the SDK changelog, which is always current.

## Style

Prose on this site never uses the em dash character, the rule the specs and SDK repositories check in CI; this repository has no CI, so it is a rule to keep by hand.

## License

Apache-2.0, matching the SDK. See the [organization](https://github.com/get-milano).
