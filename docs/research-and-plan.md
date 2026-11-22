# Mark 1 — Research & Product Plan (v1, 2026-11-22)

Mark 1 is the working name for a telehealth / virtual-clinic SaaS for doctors and small clinics: per-doctor dashboard, availability-based booking, video visits, patient records, payments and AI.

Whiteboard: https://claude.ai/artifact/1yoptYkNsFavXjWNERxYEN · Feature sheet: `docs/mark1-features.xlsx`

## Update 2026-11-22: V1 direction (replaces conflicting parts below)

These are the owner's decisions after reviewing v1 of this plan. Where they conflict with sections 1–11 below, this section wins.

**Decisions**
- **Roles:** Admin (us) creates doctor accounts. Doctors use the platform. Patients sign up through a doctor's personal link.
- **Patient model:** a patient joins the doctor whose link they used. If a second doctor shares their link, the existing account is linked to that doctor too, with no new signup. Doctors never see each other, each doctor sees only their own patients' data, and there is no doctor directory.
- **Money:** doctors pay Mark 1 a monthly fee outside the platform. There are no patient payments in V1. If patient payments come later, 100% goes to the doctor. No insurance billing, ever.
- **Video:** Google Meet. The doctor connects their own Google account and Mark 1 creates a Meet link for each booking through the Google Calendar API, free to us. Doctors can paste their own Zoom, Doxy or Teams link instead.
- **Clinics:** individual doctors only in V1 (assumed, to confirm). Clinics with several doctors come in v2.
- **GDPR** is built in from the start. The goal is to sell internationally.
- **Costs:** keep third-party spend minimal. Target about $15–40/month to run.
- **Files:** no file storage in V1. Later, Wasabi or S3.

**Answers to the owner's questions**
- **What HIPAA is:** a US law saying patient health information must be protected. Any company that stores it for a US doctor must protect it and sign a contract with the doctor called a BAA (Business Associate Agreement).
- **"We're not a healthcare company, so no legal rules apply" is not correct.** The rules follow the *data*, not who employs the doctors. Patient names, bookings and doctor notes are health data.
  - US doctors who bill insurance must have a BAA with any software that holds their patients' data.
  - EU patients are covered by GDPR, which treats health data as a "special category" with stricter rules.
  - Purely cash-only US doctors are generally outside HIPAA.
  - The practical cost is small: pick vendors that sign BAAs or DPAs (the GDPR equivalent), follow basic security, and have BAA, DPA and privacy policy templates.
- **Why RDS for row-level security? We don't need it.** Row-level security is built into Postgres itself. RDS is only Amazon running Postgres for you (backups and updates). Any Postgres works, including one on the same small server as the app.
- **"S3 is expensive" isn't true at our size.** S3 costs about $0.023/GB, so 50 GB is about $1.15/month. Wasabi charges a 1 TB minimum (about $6.99/month) and keeps files for at least 90 days, so it's only cheaper above roughly 300 GB. Both sign a BAA (Wasabi through its sales team).
- **What Meet costs us in capability:**
  - Mark 1 can't access the call, so there's no AI transcription of the visit itself.
  - Google has to verify the app before it can create calendar events for the public. Verification is free but takes weeks, so apply early.
  - US doctors who need HIPAA must use paid Google Workspace with Google's BAA. That's the doctor's responsibility, but we must tell them.
- **"Free AI" doesn't really exist for patient data:** free tiers usually let the provider use your data. The low-cost path is:
  1. Dictation after the visit, with speech-to-text running **in the doctor's browser** using open-source Whisper. This costs us $0, and the audio never leaves the doctor's device.
  2. A pay-per-use text AI API with a data agreement, used to structure the dictation into a SOAP note. Expected cost is about $1–5/month at the start.
  3. Doctors on paid Google Workspace can also use Meet's own built-in note-taking.

**Revised V1 scope:** see `mark1-features.xlsx`. In short:
- **Admin:** create doctor accounts, track plan and paid-until date, activate or suspend doctors.
- **Doctor:** availability, personal booking link, calendar, patient list, patient profile and history, intake form, notes with dictation and AI, auto Meet links, email reminders.
- **Patient:** join through a doctor's link, book, reschedule or cancel, fill in the intake form, export or delete their data.
- **For everyone:** consent, audit log, encryption, MFA.

**Revised architecture (about $15–40/month):**
- Next.js + TypeScript and Postgres with row-level security per doctor, on one small server.
- **Hosting is still open.** A small AWS server costs about $10–20/month and AWS signs the BAA for free (recommended). A cheap EU VPS costs about €5–10/month and handles GDPR, but its providers usually won't sign a BAA.
- Google Calendar API for Meet links (free) · email reminders with no health details · browser Whisper plus a pay-per-use text AI API.

**Removed from V1:** patient payments and Stripe Connect · built-in video · AI transcription of live calls · file uploads · insurance billing and e-prescribing · the niche-specialty strategy (on hold; still recommended for selling).

Extra sources: https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html · https://docs.wasabi.com/docs/how-does-wasabi-address-health-care-privacy-compliance · https://docs.wasabi.com/docs/how-does-wasabis-monthly-minimum-storage-charge-work · https://gsuite-developers.googleblog.com/2017/12/hangouts-meet-now-available-in-google.html · https://cpaas.8x8.com/en/pricing/jitsi-as-a-service-pricing/

---

## v1 plan (original research)

Prices below come mostly from third-party review sites that often disagree with each other. Treat them as approximate and verify on vendor pages before deciding anything.

---

## 1. What's wrong with the idea as stated

1. **As described, it's a commodity.** Booking, video, records and payments together is what dozens of mature products already sell for $0–$99 per provider per month (see §2). If the pitch is "the same thing, built by one person", doctors have no reason to switch.
2. **Selling to the US and Europe at once means two compliance regimes.** The US has HIPAA. Europe has GDPR plus national health-data rules, such as France's HDS-certified hosting requirement. Each country is its own project. **Recommendation: start with the US only.** It's one law, the largest cash-pay market, English-speaking, and plenty of vendors will sign a BAA (Business Associate Agreement, the HIPAA contract for handling patient data). Add Europe later, one country at a time.
3. **Google Meet is the wrong video choice.** Using Meet under HIPAA requires each doctor to have a paid Google Workspace account with a signed BAA. Free Meet is excluded. Mark 1 also couldn't control the waiting room, branding, recording or AI transcription. Use a video SDK embedded in the product and covered by Mark 1's own BAA (§6).
4. **A full EHR is a trap for a solo builder.** Insurance billing (claims, clearinghouses), e-prescribing (Surescripts, controlled-substance rules), lab integrations and ONC certification each take months. **Target cash-pay practices** and leave insurance billing and e-prescribing out of the MVP.
5. **Selling is the bottleneck, not building.** With no doctor contacts and buyers who are slow and avoid risk, validation and distribution have to start before any code is written (§9).
6. **Compliance costs money every month, starting before the first customer.** On Supabase, for example, HIPAA requires the Team plan at about $599/month plus a HIPAA add-on. Working directly on AWS is cheaper: the BAA is free (signed through AWS Artifact) and RDS, S3, SES and Chime SDK are HIPAA-eligible. That likely starts under $150/month. Customers will also ask Mark 1 to sign a BAA with them and to answer security questionnaires. SOC 2 comes later.

## 2. Competitors

| Product | Focus | Approx. price | Notes |
|---|---|---|---|
| doxy.me | Telehealth video only | Free tier (with BAA); Pro ~$35/provider | Sets the price floor for "just video" |
| SimplePractice | Therapy and wellness practice management | ~$49–$99/mo; per-claim fees | Owned by Vista Equity since 2024; complaints about price rises and support |
| Practice Better | Nutrition, coaching, wellness | $25–$155/mo | Telehealth included |
| Jane App | Allied health clinics | $59 / $79 / $99 + $15 AI scribe add-on | Strong booking; AI sold as an extra |
| Healthie | Virtual-first and nutrition, plus an API | $18–$135+/mo | Also sells infrastructure to startups |
| Cliniko | Allied health (AU, UK, EU) | ~$45/mo for 1 practitioner | Regional data residency |
| Semble | UK private clinics | From ~£119/mo | ISO 27001, NHS DSPT |
| Doctolib | France and Germany booking and teleconsultation | ~€139–149/mo | Dominant in Europe; HDS hosting |
| Tebra | US independent practices with insurance | ~$150/mo+ | Full EHR and billing |
| Elation | Primary care and direct primary care | ~$349/mo | Clinical depth |
| CharmHealth | General EHR | Free low-volume tier | Price pressure |
| AI scribes (Freed, Heidi, Abridge) | Notes only | $39–$149/mo (Abridge enterprise) | A separate bill on top of the practice software |

**Gap Mark 1 could fill:** a cash-pay specialty clinic today pays for practice software (~$50–$100) *plus* a scribe (~$40–$150) *plus* juggles a separate payments setup. One product that covers one specialty's workflow, with the AI scribe included in the price, gives a concrete reason to switch.

## 3. Positioning (recommendation, to validate)

- **One niche, one workflow.** Don't build a generic clinic product. Candidates to validate with interviews:
  - Psychiatric NPs, ketamine and TMS clinics
  - Weight-loss / GLP-1 telehealth clinics
  - Functional and integrative medicine
  - Dermatology and aesthetics follow-ups
  - Men's or women's health and sleep clinics
  - *Avoid general therapy and mental health: it's saturated.*
- **AI-native bundle:** scheduling, video, AI-drafted notes and payments for one price.
- **Fast setup:** a booking link, intake form and video room working within 10 minutes, with no sales call.

## 4. Feature scope

See `mark1-features.xlsx` for the full list with priority, phase and effort.

**MVP:** multi-tenant clinic workspace and roles (with MFA) · doctor availability (hours, exceptions, buffers, visit types, prices) · public booking page · patient portal (intake forms, consents, documents) · embedded video with a waiting room · patient chart (demographics, allergies, medications, problems, SOAP notes, files) · AI scribe drafting notes for the doctor to sign · Stripe Connect payments at booking plus no-show fees · reminders with no patient health data in the message · audit log, encryption, data export · BAA template for customers · SaaS subscription billing.

**v2:** Google/Outlook calendar sync · secure messaging · AI intake summary · AI-drafted message replies · packages and memberships · superbills (receipts patients submit to their insurer themselves) · multi-provider and small-hospital admin · analytics.

**Later:** e-prescribing through a partner · labs · insurance billing · EU expansion · mobile apps · white-label for hospitals.

## 5. AI features, ranked by value for the effort

1. **Ambient scribe:** transcribes the visit (with consent) and drafts a SOAP note that the doctor edits and signs. Highest value; it's what competitors charge $39–$149/mo for.
2. **Pre-visit summary:** turns intake answers and history into a one-screen brief.
3. **Message reply drafts** for patient messages.
4. **After-visit summary** in plain language, with translation.
5. Later: no-show prediction, scheduling suggestions, billing-code suggestions.

Guardrails: the doctor always reviews and signs · AI never sends clinical content on its own · every AI use is logged · the speech-to-text and LLM vendors must sign a BAA and must not retain data.

## 6. Architecture (suited to a solo developer, HIPAA-eligible)

- **Frontend:** Next.js + TypeScript. Three surfaces: the doctor dashboard, the patient portal and public booking pages.
- **Backend:** Node/TypeScript API; PostgreSQL on AWS RDS (encrypted); every row carries a `clinic_id` and Postgres row-level security keeps each clinic's data separate.
- **Files:** S3, encrypted, accessed through signed URLs.
- **Email:** AWS SES. **SMS:** a provider that signs a BAA; reminder messages contain no patient health data.
- **Video:** AWS Chime SDK (about $0.0017 per attendee-minute, covered by the AWS BAA), so a 30-minute two-person visit costs about $0.10. Alternatives: Daily or 100ms (healthcare add-ons around $500/mo) or the Zoom Video SDK.
- **Auth:** AWS Cognito, or another auth provider that signs a BAA. MFA is required for clinic staff.
- **AI:** speech-to-text and LLM APIs from vendors that sign a BAA.
- **Ops:** no patient health data in logs · append-only audit log · backups · infrastructure as code.
- **Build vs buy:** Medplum is an open-source FHIR backend (FHIR is the standard format for health records) that we could self-host on AWS. Oystehr is usage-based EHR infrastructure (about $0.25 per monthly active user). Default to plain Postgres for speed, and shape the records like FHIR so integrations are easier later.

## 7. Monetization & payments

- **Subscription per provider** (Stripe Billing), to be validated:
  - Starter, about $49: booking, video, chart, payments
  - Pro, about $99: Starter plus the AI scribe and AI features
  - Clinic: custom pricing for multiple providers, admin and a BAA
  - 14-day trial
- **Payment revenue:** patients pay the clinic through Stripe Connect, with an optional platform fee of about 1%.
- **Stripe does not sign a BAA.** Payment processing is exempt from HIPAA, but only as long as no patient health data goes to Stripe. Never send the visit reason, diagnosis or clinical notes in descriptions, metadata or receipts; link payments to records with internal IDs only.
- **Unit economics to model:** video about $0.10 per visit · AI scribe cost per visit · fixed hosting cost · Stripe fees.

## 8. Third-party services

The list with BAA status and costs is in the spreadsheet's "Third parties" sheet.

## 9. Go-to-market (no contacts yet)

**Phase 0, before writing code:**
1. Shortlist two niches.
2. Interview 15–20 practitioners. Find them through LinkedIn, specialty Facebook groups, Reddit, and cold email to cash-pay clinics found in online directories.
3. Put up a landing page with a waitlist.
4. Sign three design-partner clinics (early clinics that use the product for free or cheap in exchange for feedback) before building the full MVP.

A separate session will go deep on sales and marketing.

## 10. Risks

- **Regulatory missteps.** Doctors are responsible for being licensed in the patient's state, but the platform should support that, for example by capturing the patient's location.
- **Breach liability.** Needs BAAs, cyber insurance and security discipline.
- **Long sales cycles.** Doctors are slow, risk-averse buyers.
- **Solo part-time burnout.** One person building in spare time is a real limit.
- **AI note errors.** The doctor must always review and sign.

## 11. Open decisions

US only first? (recommended) · which niche · price points · video vendor (Chime or Daily) · build vs Medplum · product name.

## Sources

- https://softwarefinder.com/resources/best-ehr-emr-for-telehealth
- https://www.supanote.ai/blog/ehr-software-for-small-practices
- https://doxy.me/pricing
- https://www.capterra.com/p/158461/Doxy-me/pricing/
- https://prospyrmed.com/compare/janeapp-pricing
- https://ranksvs.com/compare/jane-app-vs-tebra/
- https://ranksvs.com/compare/elation-health-vs-tebra/
- https://www.choosingtherapy.com/simplepractice-alternatives/
- https://www.g2.com/products/SimplePractice/reviews
- https://schedulingkit.com/pricing-guides/cliniko-pricing
- https://bookedsolid.health/blog/cliniko-vs-semble
- https://www.capterra.com/p/184480/Doctolib/
- https://connect.doctolib.com/assets/downloads/Privacy-policy-EN.pdf
- https://support.google.com/a/answer/3407054
- https://www.hipaajournal.com/is-google-meet-hipaa-compliant/
- https://www.commure.com/blog-scribe/scribe-pricing
- https://www.deepcura.com/resources/compare/best-ai-medical-scribes
- https://www.forasoft.com/blog/article/hipaa-compliant-video-platform
- https://www.videosdk.live/blog/hipaa-compliant-video-conferencing-api
- https://medplum.com/pricing
- https://oystehr.com/custom-emr
- https://supabase.com/pricing
- https://supabase.com/legal/customer-resources/business-associate-agreement
- https://www.hipaajournal.com/is-stripe-hipaa-compliant/
- https://help.doxy.me/en/articles/1228780-collecting-payment-from-patients-and-hipaa-compliance
