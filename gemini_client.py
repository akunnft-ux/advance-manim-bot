import json
import os
import random
import time
from google import genai

from config import TOPICS, TOPIC_DESCRIPTIONS
from templates import TEMPLATE_TOPIC_MAP


def _build_prompt(topic: str, history: list) -> str:
    topic_label = TOPICS[topic]
    topic_desc = TOPIC_DESCRIPTIONS[topic]
    templates = TEMPLATE_TOPIC_MAP.get(topic, ["derivative"])
    templates_str = ", ".join(templates)
    recent = history[-10:] if history else []

    return f"""Buat konten video matematika bergaya 3Blue1Brown dengan topik {topic_label} ({topic_desc}).

Tugasmu:
1. Pilih template scene dari daftar yang tersedia: [{templates_str}]
2. Tulis judul, deskripsi, dan rumus LaTeX yang sesuai
3. Isi parameter opsional untuk template

Output JSON dengan struktur berikut:
{{
  "template": "nama_template",
  "narasi": {{
    "judul": "judul video (max 50 chars)",
    "deskripsi": "penjelasan singkat (max 200 chars, Bahasa Indonesia)",
    "rumus": "LaTeX rumus utama"
  }},
  "params": {{
  }}
}}

Aturan:
- judul maksimal 50 karakter, Bahasa Indonesia
- deskripsi maksimal 200 karakter, Bahasa Indonesia
- rumus: LaTeX string valid untuk MathTex Manim, tanpa delimiters $$, contoh: "f'(x) = \\\\lim_{{h \\\\to 0}} \\\\frac{{f(x+h) - f(x)}}{{h}}"
- Jangan pernah menggunakan \\\\text{{}} di dalam \\\\lim atau \\\\sum atau \\\\int
- Pastikan LaTeX valid (amsmath standar)
- KONTEN SEBELUMNYA (jangan duplicate): {json.dumps([h.get("judul") for h in recent], ensure_ascii=False)}
- Pilih template yang paling cocok dengan konten yang dibuat

Untuk template "derivative": isi params opsional seperti "topik_khusus"
Untuk template "integral": isi params opsional seperti "topik_khusus"
Untuk template "vector": isi params opsional seperti "topik_khusus"
Untuk template "transform": isi params opsional seperti "topik_khusus"
Untuk template "sphere": isi params opsional seperti "topik_khusus"
Untuk template "cross_section": isi params opsional seperti "topik_khusus"
Untuk template "distribusi": isi params opsional seperti "topik_khusus"
Untuk template "bayes": isi params opsional seperti "topik_khusus"

Output HANYA JSON, tanpa markdown formatting atau teks lain."""


def generate(topic: str, complexity: str, history: list, max_retry=3) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    templates = TEMPLATE_TOPIC_MAP.get(topic, ["derivative"])
    template_name = random.choice(templates)

    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(topic, history)

    for attempt in range(1, max_retry + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            result = json.loads(response.text)

            if not _validate(result):
                continue

            return result

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            if attempt == max_retry:
                break
            time.sleep(2 * attempt)

    # Fallback: use random template with minimal content
    return {
        "template": template_name,
        "narasi": {
            "judul": _fallback_judul(topic, template_name),
            "deskripsi": f"Visualisasi {TOPICS[topic].lower()} menggunakan animasi matematika.",
            "rumus": _fallback_rumus(template_name),
        },
        "params": {},
    }


def _validate(result: dict) -> bool:
    if "template" not in result or "narasi" not in result:
        return False
    narasi = result["narasi"]
    if not all(k in narasi for k in ("judul", "deskripsi", "rumus")):
        return False
    if not narasi["judul"] or len(narasi["judul"]) > 50:
        return False
    if not isinstance(result.get("params"), dict):
        result["params"] = {}
    return True


def _fallback_judul(topic, template):
    titles = {
        "kalkulus": {"derivative": "Turunan Fungsi", "integral": "Integral Tentu"},
        "aljabar-linear": {"vector": "Penjumlahan Vektor", "transform": "Transformasi Linear"},
        "geometri-3d": {"sphere": "Geometri Bola", "cross_section": "Irisan Bidang"},
        "probstat": {"distribusi": "Distribusi Normal", "bayes": "Teorema Bayes"},
    }
    return titles.get(topic, {}).get(template, "Visualisasi Matematika")


def _fallback_rumus(template):
    rumus = {
        "derivative": "f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}",
        "integral": "\\int_{a}^{b} f(x) \\, dx",
        "vector": "\\vec{a} + \\vec{b}",
        "transform": "\\begin{pmatrix}1 & 2\\\\3 & 1\\end{pmatrix}",
        "sphere": "x^2 + y^2 + z^2 = r^2",
        "cross_section": "z = x^2 + y^2",
        "distribusi": "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}",
        "bayes": "P(A|B) = \\frac{P(B|A)P(A)}{P(B)}",
    }
    return rumus.get(template, "f(x)")
