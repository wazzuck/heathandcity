# Architecture: Hampstead & North West London Consulting Showcase

## 1. Purpose and Scope

1. This document defines the technical architecture of the static showcase
   website for the Hampstead and North West (NW) London private technology
   consulting practice.
2. The website targets senior, non-technical principals across NW3, NW6, NW8,
   NW11, and N6, including boutique insurance brokers, senior medical
   consultants, King's Counsel (KC), boutique law partners, family offices,
   and multi-Special Purpose Vehicle (SPV) property principals.
3. The system combines an institutional-grade editorial layout with a
   high-impact, interactive Three-Dimensional (3D) visual centrepiece powered
   by Web Graphics Processing Unit (WebGPU), Three.js, and Web Graphics
   Library (WebGL) shaders.

---

## 2. Hosting and Deployment Constraints

1. The site is engineered for static hosting on GitHub Pages (free tier) and
   remains portable to Cloudflare Pages or any Content Delivery Network (CDN)
   without code modifications.
2. No server-side execution, database, or custom Hypertext Transfer Protocol
   (HTTP) response headers are required.
3. The application explicitly avoids `SharedArrayBuffer`, Cross-Origin Opener
   Policy (COOP), and Cross-Origin Embedder Policy (COEP) headers.
4. All visual physics, particle transformations, and shader effects run on
   single-page client graphics pipelines without multi-threaded WebAssembly
   (WASM) compute dependencies.

---

## 3. Multi-Tier Graphics Architecture

To guarantee both visual impact on modern hardware and 100% reliability on
older or locked-down client machines, the rendering engine (`js/gpu-scene.js`)
implements a four-tier graceful degradation pipeline:

```text
+--------------------------------------------------------------------------+
|                     Browser Hardware Capability Probe                    |
+--------------------------------------------------------------------------+
         |
         +--> [Tier 1: WebGPU Adapter + Device Available]
         |    Initialises navigator.gpu device, compiles WebGPU Shading
         |    Language (WGSL) verification kernel, and pairs with the
         |    Three.js / WebGL2 3D hardware shader pipeline.
         |
         +--> [Tier 2: Three.js WebGL2 Custom Shader Pipeline]
         |    Renders 12,000+ GPU-animated particles, 3D architectural
         |    lattice geometries, and interactive cursor raycasting.
         |
         +--> [Tier 3: Zero-Dependency 2D Canvas Projection Engine]
         |    If external CDN modules are blocked or WebGL is unavailable,
         |    projects 3D particle and lattice coordinates onto an HTML5
         |    Two-Dimensional (2D) Canvas at 60 Frames Per Second (FPS).
         |
         +--> [Tier 4: Accessible Static Architectural Fallback]
              Activated when prefers-reduced-motion is requested or all
              canvas contexts are disabled.
```

---

## 4. Interactive Visual Centrepiece Modes

The user can switch live between three interactive 3D GPU scenes:

1. **Scene 1: Order from Chaos (Autonomous Inbox & Document Lattice)**
   - Models unsorted email threads, 2,000-page PDF bundles, and insurer
     remittances entering a central normalisation ring and snapping into an
     ordered emerald-and-brass architectural ledger.
   - Controlled via the live "Entropy to Order" slider, cursor movement, and
     scroll position.
2. **Scene 2: The Sovereign Vault (Private Two-Tower Neural Retrieval)**
   - Models an on-premises Hampstead Linux and GPU vault surrounded by
     concentric rings of 20-year precedent archives.
   - Cursor proximity fires synaptic retrieval beams across the vector space
     while an outer shield deflects external public-cloud egress.
3. **Scene 3: City-to-Heath Precision (Financial & Property Telemetry)**
   - Models ultra-low-latency City of London market data pipelines merged with
     Hampstead topographical contours, reconciling multi-bank PDF statements
     and 90/60/30-day property compliance horizons.

---

## 5. Module Inventory

| Path                     | Responsibility                                   |
| ------------------------ | ------------------------------------------------ |
| `index.html`             | Semantic single-page structure and content.      |
| `css/styles.css`         | Bespoke styling, themes, and responsive layout.  |
| `js/config.js`           | Centralised brand settings and vertical data.    |
| `js/gpu-scene.js`        | WebGPU, Three.js, WebGL, and Canvas 3D engine.   |
| `js/app.js`              | User Interface (UI) state, demos, and controls.  |
| `package.json`           | Dependency manifest and verification commands.   |
| `scripts/verify_site.py` | Automated quality, constraint, and column guard. |

---

## 6. Legal, Licence, and Patent Record

1. **Three.js (`0.170.0`)**: Consumed under the permissive Massachusetts
   Institute of Technology (MIT) Licence.
2. **Typography**: Google Fonts (`Cormorant Garamond`, `Plus Jakarta Sans`,
   `JetBrains Mono`) are licensed under the Open Font License (OFL) with
   system font stacks as instant fallbacks.
3. **Standards**: WebGPU, WebGL, HTML5, and Cascading Style Sheets (CSS) are
   royalty-free World Wide Web Consortium (W3C) and Khronos Group standards.
4. **Original Code**: All shader algorithms, 3D geometries, copy, and user
   interface components in this repository are original works free of third-
   party patent claims or proprietary data dependencies.
