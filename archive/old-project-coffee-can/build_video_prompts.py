#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder Bước 4b: sinh output/video-prompts.md (hook ~1 phút, Rule 6.x).

Mỗi clip = 1 CÚ CẮT sang ảnh riêng (Rule 6.2) — clip .1 dùng ảnh chính scene và copy
NGUYÊN VĂN image prompt từ prompts.md; clip .k (k>=2) có ảnh phụ [stt]-[k].jpg với
image prompt riêng. Camera motion đổi giữa mọi cặp clip liền kề (Rule 6.7 mục 5).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_prompts import (SETTING, MOOD, STYLE, VSTYLE, main as build_main)  # noqa: E402


def fmt(s):
    return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}"


def img(p1, set_id, extra, shot, mood):
    """Ảnh phụ cho clip hard-cut — vẫn đủ 5 phần như Rule 4.1."""
    p2 = SETTING[set_id] + (f", {extra}" if extra else "") if set_id else extra
    return ", ".join([p1, p2, shot, MOOD[mood], STYLE])


def vid(cam, subj, loc, mood, audio):
    return f"{cam}, {subj}, {loc}, {MOOD[mood]}, {VSTYLE}, Audio: {audio}"


# (stt, k, start, end, ảnh phụ hoặc None cho clip .1, video prompt)
CLIPS = [
(1,1,0,6,None,
 vid("Slow push-in holding the dented tin coffee can centred in frame",
     "the seated lid staying perfectly still while fine dust drifts down through the lamp cone",
     "on a scarred table in a small ranch kitchen","calm","quiet kitchen room tone")),
(1,2,6,12,
 img("a dented tin coffee can standing alone at the middle of a long empty table","dean_kitchen",None,
     "wide shot, 35mm lens","calm"),
 vid("Static camera on a wide kitchen interior",
     "the coffee can holding the centre of the empty table while the hanging lamp sways a little above it",
     "in a small plain ranch kitchen at night","calm","night house settling")),
(2,1,12,18,None,
 vid("Gentle pan right across a desk",
     "Byron in the pressed steel blue dress shirt keeping his pen moving steadily down a court form",
     "at a plain wooden desk under a small lamp","tense","pen scratching on paper")),
(2,2,18,23,
 img("a pen nib pressing a fresh line into a printed county court form",None,"on a plain wooden desk",
     "extreme close-up, 100mm macro lens","tense"),
 vid("Slow tilt down onto the page",
     "a pen nib pressing one continuous line across the form, wet ink darkening behind the tip",
     "on a plain wooden desk under lamplight","tense","pen scratching on paper")),
(3,1,23,30,None,
 vid("Static camera holding a tight portrait",
     "Truman in the threadbare olive brown cardigan slowly lifting his eyes toward the lamp, jaw settling",
     "at a warm lit kitchen table","sad","quiet room tone")),
(3,2,30,36,
 img("Truman sitting small and alone at a long table in a wide dim room","dean_kitchen",None,
     "extreme wide shot, 24mm wide-angle lens","sad"),
 vid("Slow pull-back to a very wide interior",
     "Truman in the olive brown cardigan growing smaller at the table while the dark room opens around him",
     "in a small plain ranch kitchen at night","sad","quiet room tone and distant wind")),
(4,1,36,41,None,
 vid("Slow push-in toward the gate",
     "Rook the black and tan shepherd holding position squared up at the bars, ears forward and tail low",
     "at a metal ranch gate on a gravel drive in cold rain","tense","light rain on gravel")),
(4,2,41,46,
 img("Rook with ears forward and amber brown eyes steady, rain beading across the coat","dean_gate",None,
     "close-up, 85mm portrait lens, full head within frame","tense"),
 vid("Subtle handheld sway close on the dog",
     "Rook the black and tan shepherd keeping his amber brown eyes fixed ahead while rain beads and rolls down the muzzle",
     "at the ranch gate in cold rain","tense","rain and wind across open grassland")),
(5,1,46,52,None,
 vid("Gentle pan left along the doorway",
     "Rook the black and tan shepherd lying half in and half out of the door frame, chest rising and settling, head staying on both paws",
     "at a kitchen doorway with warm light behind","sad","quiet kitchen room tone")),
(5,2,52,58,
 img("an empty pickup standing with the tailgate lowered in a bare gravel yard","dean_porch",None,
     "wide shot, 35mm lens","sad"),
 vid("Slow push-in on an empty pickup",
     "the lowered tailgate standing open and still in a bare gravel yard while the last daylight drains off the grass",
     "in the yard of a ranch house","sad","wind across an empty yard")),
(5,3,58,63,
 img("a plain worn brown leather collar around the neck of a resting dog",None,"in warm doorway light",
     "extreme close-up, 100mm macro lens","sad"),
 vid("Slow tilt up along the collar",
     "a worn brown leather collar rising and settling with the steady breathing of the resting shepherd",
     "in warm doorway light of a ranch kitchen","sad","dog breathing and quiet room tone")),
]


def main():
    rows = build_main()
    prompts = {stt: text for stt, _a, _b, _sc, text in rows}
    hook_end = max(e for _s, _k, _a, e, _i, _v in CLIPS)
    out = ["# Video Prompts — Hook: The Coffee Can (Cherry County, Nebraska)",
           f"Hook window: 00:00:00 → {fmt(hook_end)} | Clips: {len(CLIPS)} | Max clip: 8s", ""]
    for stt, k, a, b, image, video in CLIPS:
        frame = f"ảnh {stt}.jpg" if k == 1 else f"ảnh phụ {stt}-{k}.jpg (CÚ CẮT)"
        out += ["---", f"## Clip {stt}.{k}",
                f"**Scene:** {stt} | **Time:** {fmt(a)} → {fmt(b)} | **Duration:** {b-a}s | **Frame đầu:** {frame}"]
        if k == 1:
            out += ["**Image Prompt (ảnh chính scene):**", prompts[stt]]
        else:
            out += [f"**Image Prompt (ảnh phụ {stt}-{k}.jpg):**", image]
        out += ["**Video Prompt:**", video, ""]
    (ROOT / "output" / "video-prompts.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"WROTE video-prompts.md — {len(CLIPS)} clip, phủ 0 → {hook_end}s")


if __name__ == "__main__":
    main()
