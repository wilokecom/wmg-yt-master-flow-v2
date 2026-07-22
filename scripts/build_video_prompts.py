#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder: sinh output/video-prompts.md (Bước 4, Rule 6.x) cho video hook.

Clip .1 dùng ảnh chính của scene → image prompt được ĐỌC NGUYÊN VĂN từ output/prompts.md
(gate --step4 so khớp từng ký tự). Clip .k (k>=2) là CÚ CẮT sang ảnh phụ `[stt]-[k].jpg`
với image prompt riêng do người viết. Video prompt do người viết.

Project: The Kudzu Place (DLS_31). Hook = scene có start < 60s → scene 1-6, phủ 0→63s.

Chạy: python3 scripts/build_video_prompts.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "output" / "prompts.md"
OUT = ROOT / "output" / "video-prompts.md"

STYLE = ("photorealistic cinematic film still, 35mm film look, natural skin texture, "
         "soft depth of field, clean frame free of watermarks, logos, or AI icons")
VSTYLE = ("photorealistic cinematic footage, 35mm film look, natural motion, "
          "smooth stabilized camera, clean uncluttered frame")

# clip: (stt, k, start, end, image_prompt_phụ hoặc None nếu k==1, video_prompt)
CLIPS = [
 (1, 1, "00:00:00", "00:00:05", None,
  "Slow pull-back from the empty stone steps, the small group of men standing motionless with hands "
  "in their coat pockets while a cold wind moves their collars, thin winter light flattening the "
  "courthouse facade, gray stone county courthouse steps in a small-town square, flat overcast light "
  "holding every figure at a distance, " + VSTYLE + ", Audio: cold wind down an empty street"),

 (1, 2, "00:00:05", "00:00:10",
  "A weathered wooden auction gavel resting on a worn portable lectern, an unmarked folded parcel sheet "
  "beside it, gray stone county courthouse steps behind in soft focus, extreme close-up, 100mm macro lens, "
  "flat overcast light, distant framing, cold detachment, " + STYLE,
  "Static locked-off camera on the resting gavel, the folded paper lifting and settling at one corner in "
  "the wind while nothing else in the frame moves, cold flat daylight on worn wood, " + VSTYLE +
  ", Audio: wind fluttering a single sheet of paper"),

 (2, 1, "00:00:10", "00:00:15", None,
  "Slow push-in on Corinne in the olive-green canvas barn coat as she lifts the auction card chest-high "
  "and holds it there, the men around her staying still, strong directional winter light across her face, "
  "camera holds her centered through the move, " + VSTYLE + ", Audio: a single voice calling a number outdoors"),

 (2, 2, "00:00:15", "00:00:19",
  "Three weathered farmers in work coats and seed caps turning their heads toward the camera left, mouths "
  "closed, gray stone county courthouse steps behind them, medium close-up, 85mm lens, flat overcast light, "
  "distant framing, cold detachment, " + STYLE,
  "Gentle pan right across the row of turning faces, each man moving his head at a slightly different moment, "
  "breath showing faintly in the cold air, overcast light flattening their expressions, " + VSTYLE +
  ", Audio: shuffling boots on stone"),

 (3, 1, "00:00:19", "00:00:24", None,
  "Slow tilt down onto the creased insurance check lying on the dark wooden table, the paper edge curling "
  "slightly as the light shifts across it, muted desaturated tones holding the frame still, " + VSTYLE +
  ", Audio: a room tone so quiet it presses"),

 (4, 1, "00:00:24", "00:00:31", None,
  "Slow lateral tracking move across the smothered hillside, the kudzu surface rippling in one long wave as "
  "wind crosses it, buried fence posts and a barn ridge holding their shapes under the leaves, muted overcast "
  "light, " + VSTYLE + ", Audio: wind moving through a wall of leaves"),

 (4, 2, "00:00:31", "00:00:37",
  "A barn roof ridge and a leaning fence post outlined under a thick blanket of kudzu leaves, the shapes "
  "still readable beneath the growth, hillside smothered in dense kudzu vines, medium shot, 50mm lens, "
  "muted desaturated palette, overcast lighting, empty space, weight of waiting, " + STYLE,
  "Static camera framing the buried barn ridge while the leaf surface breathes in a slow gust, one vine tip "
  "swinging free at the edge of frame, flat gray daylight, " + VSTYLE + ", Audio: dry leaves brushing corrugated metal"),

 (5, 1, "00:00:37", "00:00:43", None,
  "Slow dolly along the roadside guardrail, the green wave sliding past at a steady pace with the same "
  "unbroken shape from end to end, late-winter light muted across the surface, " + VSTYLE +
  ", Audio: tires on asphalt with wind"),

 (5, 2, "00:00:43", "00:00:48",
  "A pale wide pecan trunk standing in the dim green half-light, thick vine curtains hanging across it on "
  "both sides, bark texture catching one shaft of filtered light, dim green cavern beneath kudzu canopy, "
  "close-up, 85mm portrait lens, muted desaturated palette, overcast lighting, empty space, weight of waiting, " + STYLE,
  "Slow push-in through the hanging vines toward the pale trunk, the leaf curtain parting slightly with the "
  "movement of air, filtered green light sliding up the bark, camera holds on the trunk, " + VSTYLE +
  ", Audio: damp leaves and slow dripping"),

 (6, 1, "00:00:48", "00:00:56", None,
  "Subtle handheld sway behind the foreground shoulder, the group of men on the steps breaking into laughter "
  "one after another, shoulders lifting, caps tilting back, flat overcast light keeping the frame cold, "
  + VSTYLE + ", Audio: men laughing in a small crowd"),

 (6, 2, "00:00:56", "00:01:03",
  "Corinne standing alone among the coats with the auction card lowered against her thigh, chin level, eyes "
  "fixed off camera, gray stone county courthouse steps behind her, close-up, 85mm portrait lens, full head "
  "within frame, flat overcast light, distant framing, cold detachment, " + STYLE,
  "Locked-off camera holding on Corinne in the olive-green canvas barn coat, her face steady while the "
  "laughter moves the coats behind her out of focus, one slow blink, cold flat daylight, " + VSTYLE +
  ", Audio: laughter falling away under wind"),
]


def load_scene_prompts():
    md = PROMPTS.read_text(encoding="utf-8")
    out = {}
    blocks = re.split(r"^##\s+(\d+)\s*$", md, flags=re.M)
    for i in range(1, len(blocks) - 1, 2):
        m = re.search(r"\*\*Prompt:\*\*[^\n]*\n+(.*?)(?=\n---|\n##|\Z)", blocks[i + 1], re.S)
        if m:
            out[int(blocks[i])] = " ".join(m.group(1).split())
    return out


def sec(ts):
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def main():
    if not PROMPTS.exists():
        sys.exit("LỖI: chưa có output/prompts.md — chạy phần image prompt trước.")
    scene_prompts = load_scene_prompts()
    missing = [stt for stt, k, *_ in CLIPS if k == 1 and stt not in scene_prompts]
    if missing:
        sys.exit(f"LỖI: prompts.md thiếu scene {missing} (clip .1 phải copy nguyên văn).")

    hook_end = CLIPS[-1][3]
    lines = [f"# Video Prompts — Hook: The Kudzu Place (DLS_31)",
             f"Hook window: 00:00:00 → {hook_end} | Clips: {len(CLIPS)} | Max clip: 8s", ""]
    prev_end = 0
    for stt, k, t1, t2, img, vid in CLIPS:
        assert sec(t1) == prev_end, f"Clip {stt}.{k} không nối tiếp"
        prev_end = sec(t2)
        d = sec(t2) - sec(t1)
        assert 2 <= d <= 8, f"Clip {stt}.{k}: {d}s ngoài 2-8s"
        frame = f"ảnh {stt}.jpg" if k == 1 else f"ảnh phụ {stt}-{k}.jpg (CÚ CẮT)"
        lines += ["---", f"## Clip {stt}.{k}",
                  f"**Scene:** {stt} | **Time:** {t1} → {t2} | **Duration:** {d}s | **Frame đầu:** {frame}"]
        body = scene_prompts[stt] if k == 1 else " ".join(img.split())
        label = "**Image Prompt (ảnh scene — copy nguyên văn prompts.md):**" if k == 1 else \
                f"**Image Prompt (ảnh phụ {stt}-{k}.jpg — CHỈ dùng cho hook, không vào metadata):**"
        lines += [label, body, "**Video Prompt:**", " ".join(vid.split()), ""]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ Đã ghi {OUT.name} — {len(CLIPS)} clip, phủ 00:00:00 → {hook_end}")


if __name__ == "__main__":
    main()
