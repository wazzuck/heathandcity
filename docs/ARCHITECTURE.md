# Architecture: Hampstead & North West London Private Practice Website

## 1. Purpose and Scope

1. This document defines the technical architecture of the static website
   for the Hampstead and North West (NW) London private technology practice.
2. The website targets time-poor, non-technical principals across NW3,
   NW6, NW8, NW11, and N6: barristers and King's Counsel (KC), insurance and
   stock brokers, composers and music publishers, and surgeons and senior
   consultants.
3. Copy is plain English. Technical detail sits in a collapsed panel that the
   reader can skip. The page has no animated graphics.

---

## 2. Hosting and Deployment Constraints

1. The site is engineered for static hosting on GitHub Pages (free tier) and
   remains portable to Cloudflare Pages or any Content Delivery Network (CDN)
   without code modifications.
2. No server-side execution, database, or custom Hypertext Transfer Protocol
   (HTTP) response headers are required.
3. The application explicitly avoids `SharedArrayBuffer`, Cross-Origin Opener
   Policy (COOP), and Cross-Origin Embedder Policy (COEP) headers.
4. No build step, bundler, or third-party JavaScript library is used.

---

## 3. Page Structure

The single page (`index.html`) runs top to bottom in this order:

1. **Hero**: headline, three quick facts, and two calls to action.
2. **Three promises**: no disruption, privacy, and continuity.
3. **About the founder**: background of Neville Bryce, 17+ years in
   institutional financial systems, and verified credentials.
4. **Demo**: a sample "typical morning" summary, with one tab per practice
   type. All names and figures are invented and labelled illustrative.
5. **Services**: one card per practice type, with three short benefits each.
6. **Ways to work together**: four options, plus a collapsed technical panel
   describing the build.
7. **Pricing**: three fixed-fee steps and an interactive return estimator.
8. **Questions and answers**: eight short, self-contained answers, also
   published as `FAQPage` structured data.
9. **Contact**: local details and a short enquiry form. The form opens the
   reader's own email application, and sends no data to a web server.
10. **Footer**: brand, locations, and the professional-services disclaimer.

---

## 4. Module Inventory

| Path                     | Responsibility                                   |
| ------------------------ | ------------------------------------------------ |
| `index.html`             | Semantic single-page structure and content.      |
| `img/neville-bryce.jpg`   | Founder portrait image for About and JSON-LD.    |
| `css/styles.css`         | Typography, colour, responsive layout, motion.   |
| `js/config.js`           | Brand settings, demo data, roles, and pricing.   |
| `js/app.js`              | UI state, demo tabs, estimator, and enquiry form.|
| `robots.txt`             | Lets every crawler, including AI assistants, in. |
| `sitemap.xml`            | Lists the pages for search engines.              |
| `llms.txt`               | Plain summary of the business for AI assistants. |
| `package.json`           | Manifest and verification command. No runtime    |
|                          | dependencies.                                    |
| `scripts/verify_site.py` | Automated structure, hosting, and 80-column      |
|                          | guard.                                           |

---

## 5. Search and AI-Assistant Discoverability

1. **No-JavaScript rule**: many crawlers do not run scripts. Every fact a
   reader needs (prices, the four ways to work, postcodes, the first demo
   panel, the questions and answers) is written into `index.html`.
   `js/app.js` renders the same data again from `js/config.js`.
2. **Two copies, one guard**: because the data now exists in `js/config.js`
   and in `index.html`, change both together. `scripts/verify_site.py`
   fails if a price, role title, postcode name or FAQ text in the config is
   missing from the raw HTML.
3. **Structured data**: one JSON-LD block in the head holds a
   `ProfessionalService` entry and a `FAQPage` entry. Every fact in it must
   also be visible on the page. No reviews or ratings are marked up.
4. **Head tags**: canonical link, Open Graph and Twitter card tags. There
   is no social preview image yet.
5. **Crawler files**: `robots.txt` allows all crawlers and names the
   sitemap. Do not block AI crawlers; that removes the site from their
   answers.

---

## 6. Legal, Licence, and Patent Record

1. **Typography**: Google Fonts (`Plus Jakarta Sans`, `JetBrains Mono`) are
   licensed under the Open Font License (OFL) with system font stacks as
   instant fallbacks.
2. **Standards**: HTML5 and Cascading Style Sheets (CSS) are royalty-free
   World Wide Web Consortium (W3C) standards.
3. **Original Code**: All copy, user interface components, and scripts in this
   repository are original works free of third-party patent claims or
   proprietary data dependencies.
4. **Practice-Type Copy (legal and regulatory check, November 2026)**:
   - The site provides technology and administrative services only. The
     footer states that it gives no legal, medical, investment or insurance
     advice. Broker copy says the firm does not give regulated advice.
   - Record-keeping wording refers to "the period your regulator requires"
     rather than naming a fixed retention period.
   - Collection-society names (for example, PRS for Music) are used only to
     describe the statements the system reads. The site makes no claim of
     affiliation, endorsement, or integration with any society.
   - All client, patient and royalty figures in the demonstration panel are
     invented and labelled as illustrative.
   - No risk requiring a stop-and-decide was identified.
   - Fee-estimator hourly rates and leakage factors in `js/app.js` are
     assumptions, shown to the reader as conservative estimates.
5. **Removed 3D Engine (November 2026)**: The Three.js visual, its WebGPU and
   WebGL shader code, and the `three` dependency were removed. No third-party
   code remains in the repository.
