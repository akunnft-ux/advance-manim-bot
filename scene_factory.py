import os
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Optional

from manim import config, tempconfig

from config import RENDER_TIMEOUT


def _concat_scenes(scene_paths: list, output_path: str) -> str:
    valid = [p for p in scene_paths if os.path.exists(p) and os.path.getsize(p) > 0]
    if not valid:
        raise RuntimeError("No valid scene files to concatenate")
    if len(valid) == 1:
        if valid[0] != output_path:
            shutil.move(valid[0], output_path)
        return output_path

    tmpdir = tempfile.mkdtemp()
    try:
        filelist = os.path.join(tmpdir, "filelist.txt")
        with open(filelist, "w") as f:
            for p in valid:
                f.write(f"file '{p}'\n")

        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", filelist, "-c", "copy", output_path],
            check=True, capture_output=True, text=True, timeout=120,
        )
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        raise RuntimeError("FFmpeg concat produced empty output")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"FFmpeg concat failed: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def render_scene(spec: dict, topic: str, complexity: str, output_path: str):
    narasi = spec["narasi"]
    scenes_spec = spec["scenes"]
    character = spec.get("character", None)

    base_config = {
        "quality": "medium_quality",
        "disable_caching": True,
        "preview": False,
        "pixel_width": 1080,
        "pixel_height": 1920,
        "frame_rate": 24,
    }

    tmpdir = tempfile.mkdtemp()
    scene_paths = []

    try:
        for i, scene_spec in enumerate(scenes_spec):
            scene_type = scene_spec["type"]
            is_3d = scene_spec.get("3d", False)

            scene_data = {
                "judul": narasi["judul"],
                "topic": topic,
                "complexity": complexity,
                "elements": scene_spec["elements"],
                "animations": scene_spec["animations"],
                "duration": scene_spec.get("duration", 6),
                "camera": scene_spec.get("camera", None),
                "3d": is_3d,
                "character": character,
            }

            if scene_type == "intro":
                from scenes import IntroScene
                scene_class = IntroScene
            elif scene_type == "visualization":
                from scenes import VizScene, VizScene2D
                scene_class = VizScene if is_3d else VizScene2D
            elif scene_type == "conclusion":
                from scenes import ConclusionScene
                scene_class = ConclusionScene
            else:
                from scenes import VizScene2D
                scene_class = VizScene2D

            with tempconfig({**base_config, "output_file": f"scene_{i}"}):
                instance = scene_class()
                instance.data = scene_data
                instance.render()

            rendered = instance.renderer.file_writer.movie_file_path
            if os.path.exists(rendered) and os.path.getsize(rendered) > 0:
                scene_paths.append(rendered)
            else:
                print(f"[WARN] Scene {i} rendered no output, skipping")

        if not scene_paths:
            raise RuntimeError("No scenes rendered successfully")

        return _concat_scenes(scene_paths, output_path)

    except Exception as e:
        raise RuntimeError(f"Manim render failed: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        _cleanup_cache()


def _cleanup_cache():
    cache_dirs = [
        os.path.expanduser("~/.ManimCache"),
        os.path.expanduser("~/.cache/manim"),
    ]
    for d in cache_dirs:
        if os.path.exists(d):
            try:
                shutil.rmtree(d, ignore_errors=True)
            except Exception:
                pass


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
