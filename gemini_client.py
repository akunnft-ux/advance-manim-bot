import json
import os
import time
from google import genai

from config import TOPICS, TOPIC_DESCRIPTIONS


def _build_prompt(topic: str, complexity: str, history: list) -> str:
    topic_label = TOPICS[topic]
    topic_desc = TOPIC_DESCRIPTIONS[topic]
    recent = history[-10:] if history else []

    return f"""Buat konten video matematika advanced bergaya 3Blue1Brown dengan topik {topic_label} ({topic_desc}).

Tingkat kompleksitas: {complexity}

Output JSON dengan struktur berikut:
{{
  "narasi": {{
    "judul": "judul video (max 50 chars)",
    "deskripsi": "penjelasan singkat konsep (max 200 chars, Bahasa Indonesia)",
    "rumus": "LaTeX rumus utama"
  }},
  "scenes": [
    {{
      "type": "intro | visualization | conclusion | transition",
      "duration": 6,
      "elements": ["title", "subtitle", "equation"],
      "animations": ["write", "fade_in"],
      "camera": {{"phi": 0, "theta": -90, "distance": 5, "zoom": 1.0}},
      "3d": false
    }}
  ],
  "character": {{
    "appear": false,
    "expression": "default | explain | happy",
    "position": "bottom_left | bottom_right"
  }},
  "complexity": "{complexity}"
}}

Aturan Scene Spec:
1. scenes[] harus minimal 2, maksimal 4 scene
2. Setiap scene punya: type, duration (4-12 detik), elements[], animations[]
3. Elements dari daftar: title, subtitle, equation, axes, function_graph, surface, sphere, torus, grid, number_line, vector, dot_cloud, label
4. Animations dari daftar: write, fade_in, fade_out, transform, create, lagged_start, grow_from_center, move_along_path, draw_border_then_fill, indicate
5. Jika complexity=complex, minimal 1 scene harus 3d=true dan punya camera field
6. Jika complexity=simple, semua scene 3d=false dan hanya pakai write/fade_in
7. Jika complexity=medium, boleh transform/lagged_start tapi 3d=false
8. Camera field opsional, format: {{"phi": 0-90, "theta": -180-180, "distance": 3-10, "zoom": 0.5-2.0}}
9. Character field opsional. character.appear=true hanya untuk complexity=complex
10. Durasi total semua scene: 20-40 detik
11. judul maksimal 50 karakter
12. deskripsi maksimal 200 karakter, Bahasa Indonesia
13. rumus: LaTeX string tanpa delimiters $$, contoh: "f'(x) = \\\\lim_{{h \\\\to 0}} \\\\frac{{f(x+h) - f(x)}}{{h}}"
14. KONTEN SEBELUMNYA (jangan duplicate): {json.dumps([h.get("judul") for h in recent], ensure_ascii=False)}
15. Jangan pernah menggunakan \\\\text{{}} di dalam \\\\lim atau \\\\sum atau \\\\int — gunakan langsung tanpa \\\\text
16. Pastikan LaTeX valid untuk MathTex Manim (amsmath standar)

Output HANYA JSON, tanpa markdown formatting atau teks lain."""


def generate(topic: str, complexity: str, history: list, max_retry=3) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(topic, complexity, history)

    for attempt in range(1, max_retry + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            result = json.loads(response.text)

            if not _validate_spec(result, complexity):
                continue

            return result

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            if attempt == max_retry:
                raise RuntimeError(f"Gemini failed after {max_retry} attempts: {e}")
            time.sleep(2 * attempt)

    raise RuntimeError(f"Failed to generate valid spec after {max_retry} attempts")


def _validate_spec(spec: dict, complexity: str) -> bool:
    if "narasi" not in spec or "scenes" not in spec:
        return False
    narasi = spec["narasi"]
    if not all(k in narasi for k in ("judul", "deskripsi", "rumus")):
        return False
    if not narasi["judul"] or len(narasi["judul"]) > 50:
        return False
    scenes = spec["scenes"]
    if not isinstance(scenes, list) or len(scenes) < 2 or len(scenes) > 4:
        return False
    total_duration = 0
    has_3d = False
    for scene in scenes:
        if not all(k in scene for k in ("type", "duration", "elements", "animations")):
            return False
        if scene["type"] not in ("intro", "visualization", "conclusion", "transition"):
            return False
        if not isinstance(scene["elements"], list) or not scene["elements"]:
            return False
        if not isinstance(scene["animations"], list) or not scene["animations"]:
            return False
        for anim in scene["animations"]:
            if anim not in ("write", "fade_in", "fade_out", "transform", "create",
                            "lagged_start", "grow_from_center", "move_along_path",
                            "draw_border_then_fill", "indicate"):
                return False
        if scene.get("3d"):
            has_3d = True
        total_duration += scene.get("duration", 0)

    if total_duration < 20 or total_duration > 40:
        return False
    if complexity == "simple" and has_3d:
        return False
    if complexity == "complex":
        complex_has_3d = any(s.get("3d") for s in scenes)
        if not complex_has_3d:
            return False
    if "character" in spec and spec["character"].get("appear"):
        if complexity != "complex":
            return False
        expr = spec["character"].get("expression", "")
        pos = spec["character"].get("position", "")
        if expr not in ("default", "explain", "happy"):
            return False
        if pos not in ("bottom_left", "bottom_right"):
            return False
    return True
