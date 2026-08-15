# get-milano.dev

The landing page for Milano, served by GitHub Pages as the organization site. Static, no build step: `index.html` is the page.

## Serving setup

- **Pages**: Settings → Pages → deploy from branch `main`, root. Being the org site (`get-milano.github.io`), it serves at the domain apex.
- **Custom domain**: `get-milano.dev` (the `CNAME` file in this repo). With the custom domain on this repo, the project sites are also reachable under it: [/specs/](https://get-milano.dev/specs/), [/sdk/](https://get-milano.dev/sdk/), [/playground/](https://get-milano.dev/playground/).
- **DNS**: apex `A` records to GitHub Pages (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) and a `CNAME` record for `www` pointing to `get-milano.github.io`. GitHub then redirects `www.get-milano.dev` to the apex automatically. Enable "Enforce HTTPS" once the certificate is issued.

## License

Apache-2.0, matching the SDK. See the [organization](https://github.com/get-milano).
