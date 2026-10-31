# NHS Client Acquisition, Governance, and Legal Compliance Guide

## 1. Executive Overview and Commercial Context

1. **Purpose**:
   - This document establishes the standard operating framework for acquiring,
     contracting, and managing National Health Service (NHS) primary care
     clients as a private technology consultancy (Heath and City Consulting).
   - Specifically addresses the commercial reality of General Practice (GP)
     surgeries, Primary Care Networks (PCNs), and Integrated Care Boards (ICBs).

2. **The Nature of NHS GP Surgeries**:
   - A widespread misconception is that GP practices are state-owned public
     sector departments.
   - In reality, the vast majority of United Kingdom (UK) GP surgeries operate
     as independent, self-employed commercial partnerships (or occasionally
     limited companies) holding a General Medical Services (GMS), Personal
     Medical Services (PMS), or Alternative Provider Medical Services (APMS)
     contract with NHS England.
   - The General Practitioners (GPs) who own the practice ("equity partners")
     bear unlimited personal liability for practice debts and operational
     contracts.

3. **Procurement Tiers and Spending Thresholds**:
   - **Practice Discretionary Spend (Under £10,000 to £25,000)**:
     - GP partners and Practice Managers have direct spending authority to
       procure website development, maintenance, IT consultancy, hardware, and
       local network administration without formal public tender.
     - Speed of acquisition: Days to weeks.
   - **Primary Care Network (PCN) Level (£25,000 to £100,000)**:
     - Shared procurement across 4 to 8 local practices. Coordinated by a
       Clinical Director and PCN Business Manager.
   - **Integrated Care Board (ICB) Level (£100,000+)**:
     - Statutory regional body managing NHS budgets across multiple boroughs.
     - Procures enterprise electronic health records (e.g. EMIS Health,
       SystmOne / TPP) via national procurement frameworks (e.g. Crown
       Commercial Service [CCS] G-Cloud, Spark, or Digital Care Services).

---

## 2. Legal Architecture and Contracting

To onboard a GP practice safely, three legal instruments are required:

### 2.1 Master Services Agreement (MSA)

1. **Parties**:
   - Executed between Heath and City Consulting and the named General Practice
     Partnership (naming all current equity partners jointly and severally)
     trading as the surgery.
2. **Clinical Boundary Disclaimer (Crucial)**:
   - The contract must explicitly state:
     > *"Heath and City Consulting provides technical website hosting,
     > infrastructure maintenance, and software engineering services only. The
     > Consultant does not provide medical triage, clinical advice, diagnostic
     > services, or medical device technology. Clinical accountability for all
     > patient communications, published triage advice, and medical pathways
     > remains entirely with the Practice."*
3. **Limitation of Liability**:
   - Standard commercial cap limited to 100% or 200% of annual contract fees
     (or Professional Indemnity Insurance cover level).
   - Explicit exclusion of indirect, consequential, or clinical negligence
     damages.
4. **Service Level Agreement (SLA)**:
   - Defined core hours aligned with the NHS core contract (08:00 to 18:30,
     Monday to Friday).
   - High-severity incident response: 1 to 2 hours for website downtime.
   - Target availability: 99.9% uptime for static hosting infrastructure.

### 2.2 Data Processing Agreement (DPA)

Under Article 28 of the UK General Data Protection Regulation (UK GDPR), a
formal Data Processing Agreement is legally mandatory whenever an IT supplier
processes data on behalf of a data controller:

1. **Role Definition**:
   - **Data Controller**: The GP Surgery (determines the purpose and legal
     basis for processing patient and staff data).
   - **Data Processor**: Heath and City Consulting (processes technical data,
     logs, or contact form submissions strictly under the Controller's written
     instructions).
2. **Processor Obligations**:
   - Process personal data only on documented instructions from the practice.
   - Ensure all personnel authorised to process personal data have committed
     themselves to strict confidentiality.
   - Implement appropriate technical and organisational security measures
     (encryption at rest, encryption in transit via Transport Layer Security
     [TLS 1.3], multi-factor authentication, and strict access controls).
   - Assist the practice in responding to Data Subject Access Requests (DSARs).
   - Delete or return all personal data upon contract termination.

---

## 3. Data Protection, GDPR, and Caldicott Principles

### 3.1 UK GDPR and Data Protection Act 2018 (DPA 2018)

1. **Lawful Basis for Healthcare Processing**:
   - Practice processing relies on Article 6(1)(e) ("Public task") and
     Article 9(2)(h) ("Health or social care treatment").
   - Commercial IT suppliers processing on their behalf must respect these
     statutory limitations.
2. **Data Minimisation**:
   - For practice websites, avoid storing patient identifiable data (PID) on the
     web server.
   - Route patient enquiries, prescription requests, and appointment forms
     directly into accredited NHSmail addresses or accredited clinical triage
     platforms (e.g. Accurx, eConsult, or Anima) rather than storing medical
     submissions in a local web database.
   - Storing Zero Patient Data on the website server eliminates 95% of data
     breach risk.

### 3.2 The Caldicott Principles

Every NHS organisation adheres to the eight Caldicott Principles governing
confidential patient information:

1. **Principle 1**: Justify the purpose(s) for using confidential information.
2. **Principle 2**: Do not use personal confidential data unless absolutely
   necessary.
3. **Principle 3**: Use the minimum necessary personal confidential data.
4. **Principle 4**: Access to personal confidential data should be on a strict
   need-to-know basis.
5. **Principle 5**: Everyone with access to personal confidential data must be
   aware of their responsibilities.
6. **Principle 6**: Comply with the law.
7. **Principle 7**: The duty to share information for individual care is as
   important as the duty to protect patient confidentiality.
8. **Principle 8**: Inform patients about how their information was used.

### 3.3 Data Protection Officer (DPO) and DPIA

- Every GP surgery is legally required to appoint an independent Data Protection
  Officer (DPO). The DPO is frequently provided centrally by the local
  Integrated Care Board (ICB) or a regional primary care federation.
- Any new IT system that handles patient submissions requires a Data Protection
  Impact Assessment (DPIA). Heath and City Consulting provides pre-completed
  technical security sections of the DPIA to accelerate practice approval.

---

## 4. NHS Technical Compliance Frameworks

### 4.1 Data Security and Protection Toolkit (DSPT)

1. **What It Is**:
   - An annual online self-assessment managed by NHS England that sets the
     benchmark for data security and information governance across health and
     social care.
2. **Supplier Relevance**:
   - Any external supplier holding an NHS standard contract or accessing NHS
     systems (such as NHSmail, the Health and Social Care Network [HSCN], or
     clinical databases) must publish an annual DSPT assessment meeting
     "Standards Met".
   - For an independent IT consultancy, completing an "IT Services and
     Commercial Third Party" DSPT submission is the ultimate badge of
     institutional credibility.

### 4.2 Digital Technology Assessment Criteria (DTAC)

1. **Overview**:
   - The national baseline standard created by the NHS Transformation
     Directorate to evaluate digital health technologies across five sections:
     - **Section C1: Clinical Safety**: Compliance with DCB0129 (manufacturer)
       and DCB0160 (deployer). Requires a designated Clinical Safety Officer
       (CSO) if the software impacts clinical decision-making.
     - **Section C2: Data Protection**: Full UK GDPR, DPIA, and DPO compliance.
     - **Section C3: Technical Security**: Cyber Essentials certification,
       annual penetration testing (OWASP Top 10), and secure cloud hosting.
     - **Section C4: Interoperability**: Alignment with NHS standards (OpenAPI,
       Fast Healthcare Interoperability Resources [FHIR]).
     - **Section C5: Usability and Accessibility**: Conformance with Web
       Content Accessibility Guidelines (WCAG) 2.1 level AA.
2. **Application to Static Practice Websites**:
   - A public practice information website is **not** a clinical diagnostic
     device and therefore does not require DCB0129 clinical safety clearance
     provided it explicitly disclaims medical advice and points emergencies to
     NHS 111 and 999.
   - However, achieving WCAG 2.1 AA accessibility and Cyber Essentials provides
     a near-insurmountable competitive advantage over legacy providers.

---

## 5. Professional Indemnity and Cyber Insurance

An IT consultancy serving NHS medical practices must maintain:

1. **Professional Indemnity (PI) Insurance**:
   - Minimum £1,000,000 to £2,000,000 cover for breach of professional duty or
     technical failure.
2. **Cyber and Data Liability Insurance**:
   - Minimum £1,000,000 cover covering costs associated with security incidents,
     ransomware, forensic investigation, and Information Commissioner's Office
     (ICO) notification defense.
3. **Public Liability**:
   - Minimum £1,000,000 to £2,000,000 for on-premises client site visits.

---

## 6. End-to-End Client Acquisition Procedure

```text
+--------------------------------------------------------------------------+
|                  Phase 1: Opportunity Identification                     |
|  - Identify distressed practice (e.g. Silicon Practice administration)   |
|  - Review Care Quality Commission (CQC) report & practice leadership     |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|                  Phase 2: Risk-Free Proof of Value                       |
|  - Construct faithful working mock-up of website & clinic hours          |
|  - Host on private staging endpoint on dedicated port (e.g. 8085)        |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|                  Phase 3: Decision-Maker Engagement                      |
|  - Contact Practice Manager (Operational Buyer) between 11:30 and 13:30  |
|  - Demonstrate instant solution to phone congestion                      |
|  - Deliver preview link & executive brief to Senior GP Partner           |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|                  Phase 4: Governance & Contracting                       |
|  - Execute Master Services Agreement (MSA) with Partnership              |
|  - Execute Article 28 UK GDPR Data Processing Agreement (DPA)            |
|  - Submit DPIA documentation to practice Data Protection Officer (DPO)   |
+--------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|                  Phase 5: Technical Cutover & Onboarding                 |
|  - Coordinate Domain Name System (DNS) re-pointing with practice/ICB     |
|  - Verify SSL/TLS certificates and emergency NHS 111 routing             |
|  - Onboard practice to monthly proactive monitoring retainer             |
+--------------------------------------------------------------------------+
```
