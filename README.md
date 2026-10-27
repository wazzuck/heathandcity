# Hampstead & North West London Private Technology Showcase

Single-page static website with an interactive Web Graphics Processing Unit
(WebGPU) and Three.js Three-Dimensional (3D) visual centrepiece advertising
bespoke systems engineering for senior principals across Hampstead and North
West (NW) London (`NW3`, `NW6`, `NW8`, `NW11`, `N6`).

---

## 1. Quick Start (Step by Step)

1. Start a local static Hypertext Transfer Protocol (HTTP) server from the
   repository root:
   ```bash
   python3 -m http.server 8080
   ```
2. Open `http://localhost:8080` in any modern web browser.
3. Run the automated verification and guard suite before committing:
   ```bash
   python3 scripts/verify_site.py
   ```

---

## 2. Changing the Provisional Brand Name (Step by Step)

The brand name is currently set to a provisional placeholder (`Heath & City
Systems Advisory`) while the final name is To Be Confirmed (TBC).

1. Open `js/config.js` in your editor.
2. Locate the `SITE_CONFIG` object at step 1 of the file.
3. Update `brandName`, `brandMonogram`, `contactEmail`, and
   `contactPhoneDisplay` to your chosen identity.
4. Refresh the page; `js/app.js` binds those tokens into every `[data-brand-*]`
   element across `index.html` automatically.

---

## 3. Hosting on GitHub Pages or Cloudflare Pages

1. Push the `main` branch to GitHub.
2. Open **Settings -> Pages** in the GitHub repository interface.
3. Select **Deploy from a branch**, choose `main` and `/ (root)`, and save.
4. No custom HTTP headers, `SharedArrayBuffer`, Cross-Origin Opener Policy
   (COOP), or Cross-Origin Embedder Policy (COEP) settings are required.
5. The site can be migrated to Cloudflare Pages at any time without code edits.
