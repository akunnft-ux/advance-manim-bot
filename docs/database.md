# Database Design — Advanced Manim Bot

## 1. Database Overview

**No database server.** Persistent storage via JSON files. Architecture ini dipilih karena:
- Single writer (sequential cron, no concurrency)
- Max 180 records (<50KB)
- Git-tracked untuk history dan rollback
- Tidak perlu query language (linear scan cukup)

---

## 2. Entity List

### 2.1 History Entry
Menyimpan record setiap post/send yang sukses.

### 2.2 Mode State
Menyimpan mode saat ini (telegram/facebook) dan update_id terakhir untuk getUpdates polling.

### 2.3 Learning Config (future)
Menyimpan konfigurasi yang dioptimasi oleh self-learning loop.

---

## 3. Entity Definitions

### history_entry

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| judul | String | Yes | — | Title konten (used for dedup) |
| topik | String | Yes | — | Enum: kalkulus, aljabar-linear, geometri-3d, probstat |
| complexity | String | Yes | — | Enum: simple, medium, complex |
| tanggal | String | Yes | — | YYYY-MM-DD |
| mode | String | Yes | — | Enum: telegram, facebook |
| durasi_render | Number | Yes | 0 | Render time in seconds |
| timestamp | String | Yes | ISO8601 | Waktu eksekusi |

### mode_state

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| mode | String | Yes | "telegram" | Enum: telegram, facebook |
| last_update_id | Number | Yes | 0 | Telegram update_id terakhir yang diproses |

---

## 4. Relationship Map

```
Gemini API → [main.py] → history.json (append-only)
Telegram → [main.py] → mode.json (single object overwrite)
```

No relationships between entities. Two independent files.

---

## 5. ERD (Text)

```
[history.json]
┌──────────────────────────────────────────────┐
│ [                                              │
│   { judul, topik, complexity, tanggal, mode,  │
│     durasi_render, timestamp },              │
│   ...                                        │
│ ]                                             │
└──────────────────────────────────────────────┘

[mode.json]
┌──────────────────────────────┐
│ { mode, last_update_id }    │
└──────────────────────────────┘
```

---

## 6. Table Definitions

### history.json — Structure
```json
[
  {
    "judul": "Visualisasi Turunan Fungsi",
    "topik": "kalkulus",
    "complexity": "medium",
    "tanggal": "2026-06-30",
    "mode": "telegram",
    "durasi_render": 342.5,
    "timestamp": "2026-06-30T08:00:00Z"
  }
]
```

### mode.json — Structure
```json
{
  "mode": "telegram",
  "last_update_id": 123456789
}
```

---

## 7. Constraints

| Entity | Constraint |
|---|---|
| history.json | Max 180 array items |
| history.json | judul unique dalam file (by exact match) |
| history.json | topik from enum: [kalkulus, aljabar-linear, geometri-3d, probstat] |
| history.json | complexity from enum: [simple, medium, complex] |
| history.json | mode from enum: [telegram, facebook] |
| mode.json | mode from enum: [telegram, facebook] |
| mode.json | last_update_id integer monotonik |

---

## 8. Index Strategy

No indexes. Linear scan untuk:
- Dedup check: `any(h["judul"] == new_judul for h in history)` — O(n), n ≤ 180
- Topic check: `set(h["topik"] for h in history if h["tanggal"] == today)` — O(n)

---

## 9. Unique Constraints

- `judul` unique secara semantik (exact string match) dalam history file

---

## 10. Audit Strategy

| Audit | Implementation |
|---|---|
| Post record | history.json entry |
| File mutation | Git commit per sesi (commit message: "auto: update history YYYY-MM-DD") |
| Rollback | `git revert` atau `git checkout` previous history.json |

---

## 11. RLS Matrix

N/A — Tidak ada database server, tidak ada multi-user.

---

## 12. Reporting Strategy

| Report | Method |
|---|---|
| Post count by topic | count di history.json |
| Render time trend | plot durasi_render dari history |
| Mode usage | count mode dari history |
| Daily activity | filter by tanggal |

---

## 13. Migration Strategy

| Version | Change |
|---|---|
| v1 (initial) | history.json with {judul, topik, complexity, tanggal, mode, durasi_render, timestamp} |
| v2+ (future) | TBD — backward compatible via optional fields |

---

## 14. Backup Strategy

| Frequency | Method |
|---|---|
| Per session | Git commit (auto-push) |
| Recovery | git revert atau restore from commit history |

---

## 15. Retention Strategy

| Entity | Retention | Deletion |
|---|---|---|
| history.json | 180 items (~60 hari) | Auto-purge oldest saat nambah baru |
| mode.json | Indefinite | N/A |

---

## 16. Security Design

| Concern | Implementation |
|---|---|
| Data exposure | Hanya judul konten (tidak ada PII) |
| File integrity | Git-tracked — every change is versioned |
| Write protection | Hanya bot yang write via git commit |
| Corrupt recovery | Try/except on JSON parse; backup corrupt file as .corrupt |

---

## 17. Risks

| Risk | L | I | Mitigation |
|---|---|---|---|
| Concurrent git push conflict (2 cron overlap) | Low | Med | Sequential cron, non-overlapping. GHA job concurrency: cancel-in-progress |
| File corrupt (disk error) | Low | High | Backup .corrupt + start fresh |
| History.json grows beyond 180 | Low | Low | Auto-purge di save_history() |

---

## 18. Recommendations

1. Gunakan `uv` atau `pip` untuk dependency management
2. Simpan `data/` di git — jangan .gitignore history.json
3. Gunakan `concurrency` di GHA workflow untuk prevent concurrent runs:
```yaml
concurrency:
  group: advance-manim-bot
  cancel-in-progress: true
```
4. Monitor file size — history.json tidak boleh >1MB
