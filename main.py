import os
import shutil
import sys
import tempfile
import time
import traceback
from datetime import datetime, date

from config import DEFAULT_COMPLEXITY
from history import load_history, save_history, pick_topic, is_duplicate
from notifier import notify_telegram
from gemini_client import generate
from scene_factory import render_with_timeout, RenderTimeoutError
from composer import composite_bgm
from compliance import compliance_check
from poster import check_mode, check_fb_token, post_to_facebook, send_telegram
from config import TOPICS, CTA_POOL, HASHTAG_POOL, get_env


def build_caption(judul: str, deskripsi: str, topic: str) -> str:
    import random
    topic_label = TOPICS.get(topic, topic)
    cta = random.choice(CTA_POOL)
    tags = " ".join(random.sample(HASHTAG_POOL, k=min(5, len(HASHTAG_POOL))))
    return f"{judul}\n\n{deskripsi}\n\n{topic_label}\n\n{cta}\n\n{tags}"


def main():
    print(f"[START] Advanced Manim Bot — {datetime.now().isoformat()}")
    start_time = time.time()
    tmpdir = tempfile.mkdtemp()
    final_video = None

    try:
        mode = check_mode()
        print(f"[INFO] Mode: {mode}")

        print("[STEP 1/7] Load history")
        history = load_history()

        topic = pick_topic(history)
        complexity = os.environ.get("COMPLEXITY", DEFAULT_COMPLEXITY)
        if complexity not in ("simple", "medium", "complex"):
            complexity = DEFAULT_COMPLEXITY
        print(f"[STEP 2/7] Pick topic: {topic}, complexity: {complexity}")

        print("[STEP 3/7] Generate content via Gemini")
        spec = generate(topic, complexity, history)
        judul = spec["narasi"]["judul"]
        print(f"  Judul: {judul}")

        if is_duplicate(judul, history):
            print("[WARN] Duplicate judul detected, regenerating...")
            spec = generate(topic, complexity, history)
            judul = spec["narasi"]["judul"]

        print("[STEP 4/7] Build caption & compliance check")
        caption = build_caption(judul, spec["narasi"]["deskripsi"], topic)
        compliance_check(caption)
        print(f"  Caption OK ({len(caption)} chars)")

        print("[STEP 5/7] Render Manim scene")
        raw_video = os.path.join(tmpdir, "raw_scene.mp4")
        render_start = time.time()
        try:
            result = render_with_timeout(spec, topic, complexity, raw_video)
            render_time = time.time() - render_start
            print(f"  Render took {render_time:.1f}s")
        except RenderTimeoutError:
            raise TimeoutError(f"Render timed out after {complexity} tier limit")
        except Exception as e:
            raise RuntimeError(f"Render failed: {e}")

        print("[STEP 6/7] Composite BGM")
        bgm_video = os.path.join(tmpdir, "bgm_scene.mp4")
        final_video = composite_bgm(raw_video, bgm_video)

        print("[STEP 7/7] Publish")
        if mode == "facebook":
            token_ok, _ = check_fb_token()
            if not token_ok:
                raise PermissionError("FB token invalid — fallback to skip")
            post_to_facebook(final_video, caption)
        else:
            send_telegram(final_video, caption)

        print("[RECORD] Save history")
        entry = {
            "judul": judul,
            "topik": topic,
            "complexity": complexity,
            "tanggal": date.today().isoformat(),
            "mode": mode,
            "durasi_render": round(time.time() - render_start, 1),
            "timestamp": datetime.now().isoformat(),
        }
        history.append(entry)
        save_history(history)
        print(f"  History: {len(history)} entries")

        elapsed = time.time() - start_time
        print(f"\n[DONE] Completed in {elapsed:.1f}s")
        sys.exit(0)

    except PermissionError as e:
        print(f"[BLOCKED] {e}")
        notify_telegram(f"[BLOCKED] {e}")
        sys.exit(0)

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] {datetime.now().isoformat()} — {e}")
        traceback.print_exc()
        notify_telegram(f"[ERROR] {e} (elapsed: {elapsed:.1f}s)")
        sys.exit(0)

    finally:
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)
        cleanup_cache()





def cleanup_cache():
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


if __name__ == "__main__":
    main()
