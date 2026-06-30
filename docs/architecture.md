# Architecture Document — Advanced Manim Bot

## 1. Architecture Overview

Bot Python modular untuk generate video animasi matematika advanced bergaya 3Blue1Brown, render via Manim CE, dan posting ke Facebook Reels (atau preview Telegram). Setiap video memiliki **scene composition dinamis** yang ditentukan oleh Gemini dalam format JSON spec — bukan template fix. Scene Factory pattern mengkonversi spec menjadi scene Manim dengan advance animations, 3D, camera movement, dan karakter.

**Project type:** Headless auto-posting bot (social media growth domain)
**Default Stack:** N/A (bukan web app)
**Stack aktual:** Python 3.12 + Manim CE + Gemini API + FFmpeg + Facebook Graph API + Telegram Bot API + GitHub Actions

```
+------------------------------------------------------------------+
|                     GitHub Actions (Ubuntu)                       |
|  +----------+  +----------+                                       |
|  | Cron 08  |  | Cron 16  |   2x/hari                            |
|  | UTC      |  | UTC      |   (beda dari existing bot 06/10/13)   |
|  +----+-----+  +----+-----+                                       |
|       +----------+----------------+                               |
|                  v                                                 |
|     +-----------------------------+                               |
|     |        main.py              |                               |
|     |  (Orchestrator — 5 phases)  |                               |
|     +--+-------+--------+--------+                               |
|        |       |        |                                         |
|        v       v        v                                         |
|  +---------+ +--------+ +----------------+                        |
|  | Gemini  | | Scene  | | Facebook       |                        |
|  | API     | |Factory | | Graph API      |                        |
|  +---------+ +---+----+ +----------------+                        |
|                  |                                                |
|            +-----+-----+                                          |
|            |  FFmpeg   |                                          |
|            | (BGM mix) |                                          |
|            +-----+-----+                                          |
|                  |                                                |
|            +-----+-----+                                          |
|            |  Telegram  |                                          |
|            | (preview) |                                          |
|            +-----+-----+                                          |
|                  |                                                |
|            data/ | (committed back to repo)                       |
|  +---------+-----+--------+                                      |
|  | mode.json  | history.json |                                    |
|  +---------------------------+                                    |
+------------------------------------------------------------------+
```

---

## 2. Context Diagram

```
+--------------+     +-----------------------------------------+     +--------------+
|   Admin      |     |         GitHub Actions                  |     |   Audiens    |
| (via Telegram)|--->|  +--------------+  +-------------+     |--->| (Facebook)   |
|  /mode cmd   |     |  | Cron 2x/hari |  |  main.py    |     |     |              |
+--------------+     |  +--------------+  +------+------+     |     +--------------+
                     +---------------------------+------------+
                                                   |
         +-----------------------------------------+--------------------------+
         |                    |                    |                         |
         v                    v                    v                         v
+---------------+  +-------------------+  +-------------------+  +------------------+
|  Gemini API   |  |  Manim CE        |  |  FFmpeg           |  | Facebook Graph   |
|  (Google)     |  |  (local render)  |  |  (BGM audio mix)  |  | API (Meta)       |
+---------------+  +-------------------+  +-------------------+  +------------------+
                          |
                   +------+------+
                   |  Telegram   |
                   |  Bot API    |
                   +------+------+
```

---

## 3. Module Architecture

Modular monolith dalam package Python dengan pemisahan modul per tanggung jawab:

```
advance-manim-bot/
├── main.py              # Orchestrator — urutan eksekusi, error handling, cleanup
├── scene_factory.py     # Scene Factory — parse JSON spec → generate scene dinamis
├── scenes.py            # Scene classes: IntroScene, VizScene, ConclusionScene + karakter
├── gemini_client.py     # Gemini API client — prompt engineering + scene spec parsing
├── poster.py            # Facebook + Telegram poster, mode switching
├── composer.py          # FFmpeg BGM compositing
├── history.py           # JSON history management, dedup, topic rotation
├── compliance.py        # Engagement bait check
├── notifier.py          # Telegram error notification
├── config.py            # Config constants, complexity tiers
├── data/
│   ├── history.json     # Post history
│   └── mode.json        # Telegram/Facebook mode state
├── audio/               # BGM MP3 files
├── fonts/               # Font files
└── docs/                # Documentation
```

### Module Responsibilities

| Modul | Tanggung Jawab | Dependencies |
|---|---|---|
| **main.py** (Orchestrator) | Urutan 5-phase pipeline: load→generate→render→post→cleanup; error handling; timeout | Semua modul |
| **scenes.py** | Scene classes: IntroScene (animated title), VizScene (core visualization), ConclusionScene (summary); karakter animasi; reusability | Manim CE |
| **scene_factory.py** | Parse Gemini JSON spec → panggil scene classes sesuai spec; dynamic layout; camera setup; animation sequence | scenes.py, Manim CE |
| **gemini_client.py** | Prompt engineering per topic + complexity tier; Gemini API call; JSON parse + validate; retry logic | google-genai |
| **poster.py** | Facebook Graph API upload; Telegram sendVideo; token pre-check; mode switching; compliance re-check | requests |
| **composer.py** | FFmpeg subprocess: audio mixing, codec check | FFmpeg |
| **history.py** | Load/save history.json; dedup check; topic rotation | json |
| **compliance.py** | Pattern-based engagement bait detection | re |
| **notifier.py** | Telegram error notification | requests |
| **config.py** | Constants: topics, hooks, CTAs, hashtags, complexity tier config | — |

### Scene Factory Design Pattern

```
Scene Factory Flow:
  Scene spec JSON (from Gemini)
       |
       v
  Parse spec → validate structure
       |
       v
  For each scene in spec.scenes[]:
       |
       +→ Determine scene class (IntroScene / VizScene / ConclusionScene)
       +→ Map elements[] to Manim mobjects:
       |     "title" → Text
       |     "axes" → Axes
       |     "function_graph" → ParametricFunction
       |     "3d_sphere" → Sphere (if 3d:true)
       |     "surface" → Surface
       |     "equation" → MathTex
       +→ Map animations[] to Manim animations:
       |     "write" → Write
       |     "transform" → Transform
       |     "lagged_start" → LaggedStart
       |     "create" → Create
       |     "grow_from_center" → GrowFromCenter
       |     "move_along_path" → MoveAlongPath
       +→ Apply camera animation if spec.camera exists
       +→ Add character if spec.character exists
       +→ Render scene
       |
       v
  Composite all scenes → raw MP4
```

---

## 4. Layer Architecture

| Layer | Components | Notes |
|---|---|---|
| **Application** | `main.py` (orchestrator) | Pipeline coordinator, no business logic |
| **Domain** | `scene_factory.py`, `scenes.py`, `gemini_client.py`, `history.py`, `compliance.py` | Pure business logic, no IO |
| **Infrastructure** | `poster.py`, `composer.py`, `notifier.py` | External API calls, FFmpeg, Telegram |
| **Config** | `config.py`, `data/*.json` | Configuration + file persistence |

---

## 5. Feature Architecture

### Feature: Dynamic Scene Generation & Render

| Aspek | Detail |
|---|---|
| Purpose | Scene composition determined by Gemini JSON spec — not hardcoded template |
| Inputs | Scene spec JSON (FR-001 output), complexity tier |
| Process | scene_factory.py: parse spec → map elements/animations → call scenes.py classes |
| Outputs | Rendered MP4 (1080×1920, 20-40 detik, 24 FPS) |
| Dependencies | Manim CE, Gemini API |
| Error Handling | Per-scene try/except; unknown element→skip; unknown anim→fallback Write |

### Feature: Advance Animations

| Transform | Morphing dari satu mobject ke mobject lain |
|---|---|
| LaggedStart | Staggered appearance — elements muncul satu per satu |
| TransformMatchingTex | LaTeX morphing — equation berubah menjadi equation lain |
| MoveAlongPath | Objek bergerak mengikuti path |
| Homotopy | Continuous deformation |
| Create | DrawBorderThenFill for geometric shapes |
| GrowFromCenter | Element tumbuh dari pusat |

### Feature: 3D + Camera

| ThreeDScene | Scene class untuk 3D visualization |
|---|---|
| Sphere/Torus/Surface | 3D mobjects dengan perspective projection |
| Camera reorient | `self.move_camera(phi, theta, distance)` |
| Camera zoom | `self.camera.frame.animate.scale(zoom_factor)` |
| Auto-rotation | `self.begin_3dillusion_camera_rotation()` |

### Feature: Karakter Animasi

| Karakter | VMobject-based, 2-3 expressions (default, explain, happy) |
|---|---|
| Position | bottom_left / bottom_right |
| Masuk | FadeIn + slide up |
| Ekspresi | Transform antara expression shapes |

### Feature: Telegram Preview + Mode Switch

| Mode | Behavior |
|---|---|
| telegram (default) | `sendVideo` ke Telegram chat admin. State persist di mode.json |
| facebook | `POST /{page_id}/videos` ke Facebook Reels via Graph API |
| Switch | Bot baca `/mode facebook` dan `/mode telegram` via getUpdates |

### Feature: Scene Complexity Tier

| Tier | Animasi | 3D | Karakter | Target Render |
|---|---|---|---|---|
| simple | Write, FadeIn | ❌ | ❌ | <5 menit |
| medium | Transform, LaggedStart | ❌ | Optional | <10 menit |
| complex | All (Transform, LaggedStart, Homotopy, dll) | ✅ | ✅ | <15 menit |

---

## 6. Data Flow

### Main Flow (Posting Cycle)

```
main()
  |
  +- Phase 1: LOAD (2s)
  |     load history.json + mode.json + learning config
  |     pick topic (unique today)
  |     pick complexity tier
  |
  +- Phase 2: GENERATE (15s-30s)
  |     gemini_client.generate(topic, complexity) → narasi + scene spec JSON
  |     validate JSON structure
  |
  +- Phase 3: BUILD (5s)
  |     build caption (judul + deskripsi + CTA + hashtags)
  |     compliance check → BLOCK jika fail
  |
  +- Phase 4: RENDER (5m-15m — tergantung tier)
  |     scene_factory.render(spec, complexity, topic) → raw MP4
  |       for each scene in spec.scenes:
  |         map elements to Manim mobjects
  |         map animations to Manim animation types
  |         apply camera if spec.camera
  |         add character if spec.character
  |       composite scenes → raw MP4
  |     composer.add_bgm(raw_mp4) → final MP4
  |
  +- Phase 5: PUBLISH (30s-60s)
  |     check mode (mode.json)
  |     if mode == "telegram":
  |       poster.send_telegram(video, caption)
  |     if mode == "facebook":
  |       poster.post_facebook(video, caption)
  |         (includes token pre-check + compliance re-check)
  |
  +- Phase 6: RECORD (1s)
  |     history.save({judul, topik, complexity, tanggal, mode, durasi_render})
  |
  +- Phase 7: CLEANUP (2s)
  |     delete temp files
  |     flush Manim cache
```

### Failure Flow

```
Phase 2 (Gemini 3x fail)
  → notifier.send("Gemini failed")
  → skip sesi (exit 0 — jangan exit 1 agar cron next tetap jalan)

Phase 4 (Render timeout > tier_bound)
  → cleanup temp + Manim cache
  → notifier.send("Render timeout")
  → skip sesi

Phase 5 (Post/send fail)
  → notifier.send("Upload failed: {detail}")
  → JANGAN simpan history
  → skip sesi
```

### Mode Switch Flow

```
Pre-execution (setiap cron):
  poster.check_mode() → getUpdates
    jika ada /mode facebook → mode.json {mode: "facebook"}
    jika ada /mode telegram → mode.json {mode: "telegram"}  (default)
```

---

## 7. Integration Design

### Manim Community Edition (Local)

| Aspek | Detail |
|---|---|
| Package | `pip install manim>=0.19.0` |
| Config | `config.pixel_width=1080, pixel_height=1920`; `quality=medium_quality`; `disable_caching=True` |
| Rendering | In-process via `tempconfig()` context manager |
| 3D | ThreeDScene via Cairo perspective projection |
| Timeout | 600s (complex), 400s (medium), 200s (simple) |
| System Deps | FFmpeg (apt), LaTeX minimal (texlive-latex-base) |

### Gemini API

| Aspek | Detail |
|---|---|
| Model | `gemini-3.1-flash-lite` |
| Mode | JSON mode (`response_mime_type: "application/json"`) |
| Retry | 3 attempts, backoff 2s, 5s, 10s |
| Timeout | 30 detik per attempt |

### Facebook Graph API

| Aspek | Detail |
|---|---|
| Endpoint | `POST https://graph.facebook.com/v22.0/{PAGE_ID}/videos` |
| Token check | Pre-emptive via `GET /{page_id}?fields=id,name` sebelum upload |
| Error matrix (per social-media-growth-engine §4.2) | |
| — Token expired (401) | Halt, alert, no retry |
| — Rate limited (429) | Backoff 3x, then defer |
| — Content rejected | Log, human review |
| — Duplicate/spam flag | Halt, no auto-retry |

### FFmpeg (Audio Compositing)

| Aspek | Detail |
|---|---|
| Command | `ffmpeg -i video.mp4 -i bgm.mp3 -filter_complex "[1:a]volume=0.15[a1];[0:a][a1]amix=inputs=2:duration=first" -c:v copy -shortest output.mp4` |
| Fallback | Jika gagal → video tanpa audio |

### Telegram Bot API

| Aspek | Detail |
|---|---|
| sendVideo | `POST https://api.telegram.org/bot{TOKEN}/sendVideo` |
| getUpdates | `GET https://api.telegram.org/bot{TOKEN}/getUpdates` (mode switch polling) |
| Error | Fire-and-forget, log warning |

---

## 8. Authorization Design

| Resource | Authentication | Authorization |
|---|---|---|
| Gemini API | GEMINI_API_KEY (env var) | N/A (single key) |
| Facebook Page | FB_ACCESS_TOKEN (env var) | Scope: pages_manage_posts |
| Telegram | TELEGRAM_BOT_TOKEN (env var) | Chat ID filtered |
| history.json | File system | Git-tracked, no auth |
| mode.json | File system | Git-tracked |

### Token/credential handling (social-media-growth-engine §4.1)
- Pre-emptive expiry check sebelum setiap posting batch
- Pada expiry: log `BLOCKED_TOKEN_EXPIRED`, notify admin, jangan simpan history
- Refresh path: manual via GitHub secrets update

---

## 9. Audit Design

| Action | Data Captured | Storage |
|---|---|---|
| Post success | {judul, topik, complexity, tanggal, mode, durasi_render} | history.json |
| Gemini fail | Timestamp + error + attempt count | GHA log + Telegram |
| Render timeout | Timestamp + tier + duration | GHA log |
| Token expiry | Timestamp + platform + error detail | GHA log + Telegram |
| Mode switch | Timestamp + old_mode + new_mode | GHA log + mode.json |

---

## 10. Observability Design

| Aspect | Implementation |
|---|---|
| App logs | `print()` timestamped per phase — visible di GHA |
| Manim logs | Captured in tempconfig (verbosity WARNING) |
| Render perf | Waktu render per scene + total — stdout |
| Error logs | Telegram + stdout |
| Execution status | GHA workflow run status + duration |

---

## 11. Security Design

| Concern | Implementation |
|---|---|
| Secret Management | GitHub Actions encrypted secrets (5 vars) |
| .env file | .gitignore, .env.example tanpa nilai real |
| Facebook Token | Long-lived; pre-emptive expiry check |
| No PII | Hanya judul konten, topik, timestamp |
| LaTeX injection | Validate LaTeX constuctor — reject dangerous commands |
| File cleanup | Temp files deleted after render/post |

---

## 12. Performance Strategy

| Operation | Target | Strategy |
|---|---|---|
| Gemini API | <15s | 30s timeout, retry 3x |
| Simple render | <5m | Write/FadeIn only, no 3D |
| Medium render | <10m | Transform/LaggedStart, 2D only |
| Complex render | <15m | All features + 3D |
| FFmpeg mix | <30s | Copy video codec, mix audio only |
| Facebook upload | <30s | File <50MB |
| Total simple | <8m | — |
| Total medium | <13m | — |
| Total complex | <20m | — |

### Optimization Strategies
1. `quality=medium_quality` — cukup untuk Facebook Reels (compress lagi by FB)
2. `disable_caching=True` — no partial movie files
3. `frame_rate=24` — FPS rendah cukup
4. Scene complexity tier — pilih complexity berdasarkan render time history
5. Auto-downgrade — jika render time >threshold, turunkan tier

---

## 13. Scalability Strategy

| Aspect | Current | Growth (12mo) |
|---|---|---|
| Posts/day | 2 | 2-3 |
| History items | 180 | 180 |
| Temp storage | ~50MB/run | ~50MB (deleted per session) |
| History storage | ~50KB | ~50KB |

No scalability concerns. Single-threaded, sequential execution.

---

## 14. Deployment Architecture

```
+--------------------------------------------------------+
|              GitHub Repository                          |
|  advance-manim-bot/                                     |
|  +- main.py                    (orchestrator)           |
|  +- scene_factory.py           (dynamic scene gen)      |
|  +- scenes.py                  (scene classes)          |
|  +- gemini_client.py           (Gemini API wrapper)     |
|  +- poster.py                  (FB + Telegram)          |
|  +- composer.py                (FFmpeg BGM)             |
|  +- history.py                 (JSON persistence)       |
|  +- compliance.py              (engagement bait check)  |
|  +- notifier.py                (Telegram error)         |
|  +- config.py                  (constants + config)     |
|  +- requirements.txt           (dependencies)           |
|  +- .env.example                                        |
|  +- data/ (history.json, mode.json)                     |
|  +- audio/*.mp3                                         |
|  +- docs/                                               |
|  +- .github/workflows/advance-manim.yml                 |
+----------------------------+---------------------------+
                              | push
                              v
+--------------------------------------------------------+
|              GitHub Actions (ubuntu-latest)              |
|  +- Checkout repo                                       |
|  +- Setup Python 3.12                                   |
|  +- apt: ffmpeg, texlive-latex-base, texlive-latex-extra|
|  +- pip install manim google-genai requests              |
|  +- python main.py                                      |
|  +- git add + git commit + git push (history.json)      |
+--------------------------------------------------------+
```

### Environment Variables (GitHub Secrets)

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `FB_PAGE_ID` | Facebook Page ID |
| `FB_ACCESS_TOKEN` | Long-lived Facebook Page Access Token |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Chat ID admin |

### GitHub Actions Workflow

```yaml
name: Advance Manim Bot
on:
  schedule:
    - cron: '0 8 * * *'   # 08:00 UTC = 15:00 WIB
    - cron: '0 16 * * *'  # 16:00 UTC = 23:00 WIB
  workflow_dispatch:

jobs:
  generate-post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg texlive-latex-base texlive-latex-extra
      - name: Install Python dependencies
        run: pip install manim google-genai requests
      - name: Run bot
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          FB_PAGE_ID: ${{ secrets.FB_PAGE_ID }}
          FB_ACCESS_TOKEN: ${{ secrets.FB_ACCESS_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python main.py
      - name: Commit history
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add data/
          git diff --staged --quiet || git commit -m "auto: update history $(date +%Y-%m-%d)"
          git push
```

---

## 15. Architecture Decision Records

### ADR-001: Manim CE over ManimGL

| Aspek | Detail |
|---|---|
| Decision | Gunakan Manim Community Edition |
| Reason | CE stable, headless Cairo renderer, dokumentasi lengkap. ManimGL butuh OpenGL yang sulit di GHA headless |
| Alternatives | ManimGL (3b1b), MoviePy+Pillow (duplicate existing) |
| Tradeoff | ThreeDScene via Cairo bukan true OpenGL 3D |
| Chosen | Manim CE |

### ADR-002: Scene Factory Pattern over Hardcoded Templates

| Aspek | Detail |
|---|---|
| Decision | Dynamic scene composition dari Gemini JSON spec via Scene Factory |
| Reason | Setiap video punya struktur scene unik (BO-002). Tidak mungkin dengan template fix |
| Alternatives | 3 template scenes seperti existing project |
| Tradeoff | Lebih complex, rawan bug jika spec invalid |
| Chosen | Scene Factory with per-scene try/except |

### ADR-003: In-process Manim via tempconfig

| Aspek | Detail |
|---|---|
| Decision | Render in-process via Python `tempconfig()` context manager |
| Reason | Kontrol timeout, error handling, tidak perlu CLI parsing |
| Alternatives | CLI subprocess `manim -ql scene.py` |
| Chosen | `tempconfig()` in-process |

### ADR-004: Modular Single Package (not single file)

| Aspek | Detail |
|---|---|
| Decision | Multi-file Python package (9 modul) bukan single main.py |
| Reason | Scene Factory + scene classes cukup besar; pemisahan memudahkan testing dan maintenance |
| Alternatives | Single main.py + scenes.py seperti existing project |
| Chosen | 9 module files |

### ADR-005: JSON File Persistence over Database

| Aspek | Detail |
|---|---|
| Decision | `data/history.json` + `data/mode.json` |
| Reason | Max 180 records, single writer, git-tracked |
| Alternatives | SQLite, Supabase |
| Chosen | JSON files |

### ADR-006: ThreeDScene Cairo over OpenGL

| Aspek | Detail |
|---|---|
| Decision | Gunakan ThreeDScene dengan Cairo perspective projection untuk efek 3D |
| Reason | Tidak butuh display/GPU. Manim CE OpenGL renderer butuh Xvfb di GHA |
| Alternatives | Manim CE OpenGL renderer + Xvfb; ManimGL + Xvfb |
| Tradeoff | Cahaya dan shading terbatas, tapi cukup untuk visualization |
| Chosen | ThreeDScene Cairo. Fallback: OpenGL renderer + xvfb-run jika diperlukan |

### ADR-007: GitHub Actions over VPS

| Aspek | Detail |
|---|---|
| Decision | GitHub Actions cron 2x/hari sebagai scheduler + runner |
| Reason | Gratis, built-in secrets, auto commit/push. Same infra as existing bot |
| Alternatives | VPS cron, AWS Lambda, Railway |
| Chosen | GitHub Actions |

---

## 16. Risks

| Risk | L | I | Mitigation |
|---|---|---|---|
| Manim CE ThreeDScene tidak cukup 3D | Med | High | Prototype rendering di GHA early; fallback ke OpenGL renderer + xvfb-run |
| Gemini scene spec tidak konsisten | Med | High | Validasi JSON ketat + template fallback per scene |
| Scene Factory rawan runtime error | Med | High | Per-scene try/except — satu scene gagal, lainnya tetap jalan |
| Render > tier timeout | Med | High | Auto-downgrade tier berdasarkan render time history |
| Pi creature port gagal | Med | Med | Jalankan tanpa karakter (masih engaging dengan advance animations) |
| 2 bot clash posting ke Page sama | Low | Med | Jadwal cron berbeda (existing 06/10/13 UTC, baru 08/16 UTC) |
| FB token expiry | Med | Med | Pre-emptive check; long-lived System User token |
| LaTeX install >500MB di GHA | Med | Low | texlive-latex-base minimal; fallback Text untuk rumus sederhana |

---

## 17. Recommendations

1. **Prototype 3D dulu** — render satu scene ThreeDScene di GHA runner untuk ukur waktu dan validasi visual quality sebelum implementasi penuh
2. **Scene Factory trial** — test dengan 3 scene spec varian (simple/medium/complex) untuk validasi pipeline parsing
3. **Pi creature port trial** — port 1 karakter sederhana dari 3b1b SVG ke Manim CE VMobject
4. **Auto-downgrade** — catat render time per tier; jika >threshold 3x berturut-turut, turunkan tier otomatis
5. **Jadwal cron berbeda** — bot baru: 08:00 UTC dan 16:00 UTC (existing bot: 06:00, 10:00, 13:00 UTC)
6. **Token monitoring** — pre-emptive check setiap sesi; kirim reminder 7 hari sebelum expiry
7. **Gradual complexity ramp** — mulai dari medium tier, naik ke complex setelah render time stabil
