# Product Requirements Document — Advanced Manim Bot

## Document Control
| Version | Date | Author | Summary |
|---|---|---|---|
| 0.1 | 2026-06-30 | prd-architect-pro | Initial draft |

## 1. Executive Summary
Bot otomatis 2x/hari untuk Facebook Reels dengan konten **matematika advanced bergaya 3Blue1Brown**. Menggunakan **Manim CE** dengan advance animations (Transform, LaggedStart, 3D camera, characters), Gemini AI untuk generate narasi + scene spec JSON, default Telegram preview.

## 2. Business Objectives
BO-001: 60 video/bulan otomatis | BO-002: Scene dinamis | BO-003: Kualitas 3B1B | BO-004: 100% cron | BO-005: Telegram preview + mode switch | BO-006: Anti-duplikasi | BO-007: Error <5% | BO-008: Zero violation

## 3. Scope
In: Gemini JSON spec, Manim CE render, dynamic scene, advance animations (Transform/LaggedStart/TransformMatchingTex), 3D (ThreeDScene/Sphere/Torus/Surface), camera (reorient/zoom), characters (Pi creature style), LaTeX, BGM, Telegram preview, Facebook posting, mode switch, GHA cron 2x/hari, anti-duplikasi, compliance BLOCK, complexity tier.

## 4. Stakeholders
Admin: Setup + monitor | Audiens: Engage | Sistem (GHA): Run

## 5. User Roles
Admin: secrets + Telegram commands | Bot: generate + render + post + record

## 6. Assumptions
ASM-001 (Critical): ThreeDScene cukup → RISK-001 | ASM-002 (High): Gemini structured JSON → RISK-002 | ASM-003 (High): Render <15m → RISK-003 | ASM-004 (Med): Pi creature port → RISK-004 | ASM-005 (High): Dynamic gen safe → RISK-005

## 7. FR Depth Classification
Core: FR-001 (Gemini Spec), FR-002 (Dynamic Scene), FR-003 (Advance Anim), FR-004 (3D), FR-005 (Camera), FR-007 (LaTeX), FR-008 (Telegram Preview), FR-009 (Facebook Post).
Supporting: FR-006 (Karakter), FR-010 (Mode Switch), FR-011 (Anti-duplikasi), FR-012 (BGM), FR-013 (Compliance), FR-014 (Error Notif), FR-015 (Timeout), FR-016 (Tier).

## 8. Functional Requirements
FR-001: Gemini → narasi + scenes[] JSON. Retry 3x. | FR-002: Parse spec → compose scene dinamis. Max 4 scenes. | FR-003: Transform, LaggedStart, TransformMatchingTex, updaters. | FR-004: ThreeDScene, Sphere, Torus, Surface. Max 1 per video. | FR-005: Camera reorient, zoom, pan. | FR-006: Pi creature VMobject, 2-3 expressions. | FR-007: MathTex, fallback Text. | FR-008: Telegram sendVideo default. <50MB. | FR-009: Facebook Graph API post. | FR-010: /mode command switch. | FR-011: Dedup + 4 topic rotation. | FR-012: FFmpeg BGM volume 0.15. | FR-013: Compliance BLOCK. | FR-014: Telegram error notif. | FR-015: Timeout 10m + cleanup. | FR-016: simple/medium/complex tier.

## 9. NFR
Durasi 20-40s | 1080×1920 | Render: simple<5m, medium<10m, complex<15m | Total <20m | 24 FPS | Error <5% | Zero secrets in code.

## 10. Data
Narasi (transient): judul, deskripsi, rumus, scenes[], complexity.
History: judul, topik, complexity, tanggal, mode, durasi_render.

## 11. Database
JSON `data/history.json`, max 180 items.

## 12. ERD
Gemini → Orchestrator → Scene Factory → FFmpeg → Telegram/Facebook → history.json

## 13. Business Rules
1 video/sesi | Topik unik/hari | No duplicate | Capped 180 | No history if fail | Gemini 3x fail=skip | Render>10m=timeout | Default mode=telegram | Compliance=BLOCK | Auto-downgrade tier.

## 14. Workflows
Main: Load→Pick topic→Pick tier→Gemini→Validate→Caption+Compliance→Render(parse spec→animate)→BGM→Check mode→Send/Post→Save→Cleanup.
Failure: Gemini fail→skip | Render timeout→cleanup+skip | Upload fail→notify+no history.

## 15. APIs
Gemini generateContent | Facebook graph/{id}/videos | Telegram sendVideo + getUpdates

## 16. Integrations
Gemini, Manim CE, FFmpeg, Facebook Graph, Telegram Bot.

## 17. Risk Assessment
RISK-001 (M/H): ThreeDScene not enough → Prototype | RISK-002 (M/H): Gemini spec inconsistent → Validate+template | RISK-003 (M/H): Render >15m → Tier+autodowngrade | RISK-004 (M/M): Pi creature → Simple char | RISK-005 (M/H): Dynamic gen bug → Try/except per scene | RISK-006 (L/M): Bot clash → Different cron.

## 18. Acceptance Criteria (16)
AC-001→FR-001: Valid JSON | AC-002→FR-002: Scene sesuai spec | AC-003→FR-003: Ada advance anim | AC-004→FR-004: ThreeDScene | AC-005→FR-005: Camera move | AC-006→FR-006: Karakter muncul | AC-007→FR-007: LaTeX rapi | AC-008→FR-008: Telegram terkirim | AC-009→FR-009: Post ID | AC-010→FR-010: Mode berubah | AC-011→FR-011: Duplicate detected | AC-012→FR-012: Ada audio | AC-013→FR-013: Blocked | AC-014→FR-014: Notif terkirim | AC-015→FR-015: Cache kosong | AC-016→FR-016: Sesuai tier.

## 19. Traceability Matrix
BO-001: FR-001,002,009,012,016 → AC-001,002,009,012,016 → RISK-002,003
BO-002: FR-001,002 → AC-001,002 → RISK-002,005
BO-003: FR-003,004,005,006,007 → AC-003-007 → RISK-001,004
BO-004: NFR-001,002,004 → AC-008,009 → RISK-006
BO-005: FR-008,010 → AC-008,010
BO-006: FR-011 → AC-011
BO-007: FR-014,015,NFR-006 → AC-014,015 → RISK-003
BO-008: FR-013,NFR-010 → AC-013

## 20. Release Strategy
Phase 1 (D1-2): Foundation | Phase 2 (D2-4): Core advance | Phase 3 (D4-5): Characters+BGM | Phase 4 (D5-6): Delivery | Phase 5 (D6-7): Stabilization

## 21. Tech Recommendations
Python 3.12 | Gemini 3.1 Flash Lite | Manim CE (pip) | ThreeDScene (Cairo) | Pi creature SVG→VMobject | FFmpeg | GHA cron | JSON | Telegram Bot API

## 22. Effort ~7.5 days
Structure+prompt 1d | Dynamic scene 1.5d | Advance anim 1d | 3D+camera 1d | Pi creature 0.5d | Telegram+mode 0.5d | Facebook+compliance 0.5d | GHA+cleanup 0.5d | Testing 1d

## 23. Outstanding Gaps
1. Scene spec JSON schema detail → Phase Architecture
2. 3D prototype GHA → validasi RISK-001
3. Pi creature porting test → Phase Architecture
