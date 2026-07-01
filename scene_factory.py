import os
import shutil
import subprocess
import tempfile
import threading
from manim import tempconfig

from config import RENDER_TIMEOUT
from templates import TEMPLATE_REGISTRY


def render_scene(spec: dict, topic: str, complexity: str, output_path: str):
    narasi = spec["narasi"]
    template_name = spec.get("template", "derivative")
    user_params = spec.get("params", {})

    template_class = TEMPLATE_REGISTRY.get(template_name)
    if not template_class:
        raise RuntimeError(f"Unknown template: {template_name}")

    base_config = {
        "quality": "medium_quality",
        "disable_caching": True,
        "preview": False,
        "pixel_width": 1080,
        "pixel_height": 1920,
        "frame_width": 4.5,
        "frame_height": 8,
        "frame_rate": 24,
    }

    params = {
        "rumus": narasi.get("rumus", ""),
        "judul": narasi.get("judul", ""),
        "deskripsi": narasi.get("deskripsi", ""),
        "topic_label": topic.replace("-", " ").title(),
        "complexity": complexity,
        **user_params,
    }

    with tempconfig({**base_config, "output_file": "template_scene"}):
        instance = template_class()
        instance.params = params
        instance.topic = topic
        instance.render()

    rendered = instance.renderer.file_writer.movie_file_path
    if os.path.exists(rendered) and os.path.getsize(rendered) > 0:
        if rendered != output_path:
            shutil.move(rendered, output_path)
        return output_path

    raise RuntimeError(f"Template {template_name} produced no output")


class RenderTimeoutError(Exception):
    pass


def render_with_timeout(spec, topic, complexity, output_path):
    timeout = RENDER_TIMEOUT.get(complexity, 600)
    result = {"path": None, "error": None}

    def _run():
        try:
            result["path"] = render_scene(spec, topic, complexity, output_path)
        except Exception as e:
            result["error"] = str(e)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise RenderTimeoutError(f"Render timed out after {timeout}s")
    if result["error"]:
        raise RuntimeError(result["error"])
    return result["path"]
