# The Southgate Surgery: Rapid Client Website Restoration Mock-Up

## 1. Executive Summary and Client Context

1. **Client Name**: The Southgate Surgery (Enfield Unity Primary Care Network
   [PCN], North London).
2. **Practice Address**: 270 Chase Side, Southgate, London, N14 4PR.
3. **Telephone Contact**: 020 8440 9301.
4. **Clinical Partners**: Dr Brian Geffin, Dr Selva Nithiyananthan, Dr Sugi
   Sutharsan, and Dr Yasser Salim. Permanent Locum: Dr Osipero Opaneye.
5. **Incident Context**:
   - The primary National Health Service (NHS) website and online triage
     vendor for the practice ("Silicon Practice") entered administration,
     triggering nationwide service disruptions across hundreds of General
     Practice (GP) surgeries throughout the United Kingdom (UK).
   - The public-facing practice domain
     (`http://www.thesouthgatesurgerynorthlondon.nhs.uk/`) went offline,
     leaving patients unable to review opening hours, clinical staff rosters,
     appointment procedures, or prescription guidance online.
6. **Commercial Opportunity**:
   - This directory contains a fully functional, self-contained restoration
     mock-up of the practice website, prepared by Heath and City Consulting
     for pre-sales client acquisition and cold outreach.
   - Demonstrates immediate capability to restore practice accessibility within
     hours, eliminating single-vendor fragility without long procurement
     delays.

---

## 2. Technical Architecture of the Mock-Up

1. **Self-Contained Static Hosting**:
   - Engineered to run completely offline or on low-cost static infrastructure
     such as Cloudflare Pages or GitHub Pages.
   - Zero dependency on database backends, legacy content management systems,
     or vulnerable third-party portal plugins.
2. **Design Standards and Accessibility**:
   - Built on the official National Health Service (NHS) Digital Frontend
     Design System (`nhsuk-frontend`).
   - Uses British English conventions throughout patient-facing guidance.
   - Retains responsive mobile-first layouts, accessible colour contrast, and
     standard Frutiger typography fallbacks.
3. **Asset Decoupling and Sanitisation**:
   - All Cascading Style Sheets (CSS), Font Awesome icon fonts, JavaScript
     libraries (jQuery and NHS frontend modules), and official NHS logos are
     mirrored locally in `wp-content/` and `wp-includes/`.
   - All historical web archive wrappers, third-party analytics trackers, and
     broken vendor endpoints have been excised.
   - Relative Uniform Resource Locator (URL) hierarchy ensures pages can be
     opened directly via file protocols or any local development server.

---

## 3. Directory Layout

| Relative Path                     | Purpose                          |
| --------------------------------- | -------------------------------- |
| `index.html`                      | Surgery homepage.                |
| `appointments/index.html`         | Appointment booking guidance.    |
| `prescriptions/index.html`        | Repeat prescription guidance.    |
| `surgery-information/index.html`  | Practice overview.               |
| `.../opening-times/index.html`    | Weekly clinic hours.             |
| `.../staff/index.html`            | Team directory.                  |
| `.../staff/doctors/index.html`    | Partner and locum roster.        |
| `services/index.html`             | Primary care services directory. |
| `services/new-patients/index.html`| Patient registration protocol.   |
| `contact-us/index.html`           | Practice address and telephones. |
| `wp-content/`                     | Mirrored styling, fonts, assets. |
| `wp-includes/`                    | Mirrored core JavaScript files.  |

---

## 4. Local and Remote Demonstration Instructions

To inspect and demonstrate this mock-up during a client acquisition call:

1. Launch the server listening remotely across network interfaces on port 8085:
   ```bash
   python3 scripts/serve_southgate.py
   ```
2. For local review on the host machine:
   - Open `http://localhost:8085/`
3. For remote review across the local network / Wi-Fi or forwarded gateway:
   - Open `http://192.168.0.13:8085/`
4. Alternatively, double-click `index.html` to inspect directly via the local
   file system.

---

## 5. Proposed Next Steps for Client Onboarding

1. **Domain Name System (DNS) Re-Pointing**:
   - Assist the practice manager and Integrated Care Board (ICB) in re-pointing
     the apex domain `thesouthgatesurgerynorthlondon.nhs.uk` to the resilient
     static hosting tier.
2. **Modern Triage Integration**:
   - Replace legacy Silicon Practice web forms with accredited NHS digital
     consultation tools such as Accurx, eConsult, or Anima.
3. **Ongoing Maintenance and Support**:
   - Enrol the surgery into a monthly proactive monitoring and compliance
     retainer with Heath and City Consulting.
