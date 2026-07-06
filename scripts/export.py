#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bước 4 — Export metadata.json (tự động, không cần AI viết tay).

Nguồn dữ liệu (ưu tiên JSON, fallback parse Markdown):
  1. output/scene-breakdown.json  (nếu có)  else parse output/scene-breakdown.md
  2. output/prompts.json          (nếu có)  else parse output/prompts.md
  3. input/config.json

Output: output/metadata.json + báo cáo validate (rules 5.1 → 5.8) in ra stdout.

Cách chạy (từ thư mục gốc project):
    python3 scripts/export.py            # export + validate (bước 4)
    python3 scripts/export.py --validate # chỉ validate metadata.json hiện có
    python3 scripts/export.py --step2    # GATE bước 2: scene-breakdown.md đạt chuẩn chưa
    python3 scripts/export.py --step3    # GATE bước 3: prompts.md đạt chuẩn chưa
    python3 scripts/export.py --prompts-list  # xuất output/prompts-list.txt (prompt đánh số, để copy chạy hàng loạt)
    python3 scripts/export.py --unix-export   # xuất output/unix-batch-NN.txt (cú pháp Uni-X Studio, nhóm 100 ảnh/file)

QUY TẮC: bước 2/3 CHƯA XONG chừng nào gate tương ứng chưa PASS.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "input"
OUTPUT = ROOT / "output"

BEAT_TYPES = {"establishing", "dialogue", "emotional_peak", "tension", "reflection", "resolution"}
TS_RE = re.compile(r"^\d{2}:\d{2}:\d{2}$")


def ts_to_sec(ts: str) -> int:
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def norm_chars(cell: str):
    cell = cell.strip()
    if cell in ("", "—", "-", "–", "none"):
        return []
    return [c.strip() for c in cell.split(",") if c.strip()]


# ---------------------------------------------------------------- parsers

def load_scenes():
    """Trả về (title, scenes[]) — mỗi scene: stt, start, end, beat_type, mood, characters, description."""
    j = OUTPUT / "scene-breakdown.json"
    if j.exists():
        d = json.loads(j.read_text(encoding="utf-8"))
        return d.get("title", ""), d["scenes"]

    src = OUTPUT / "scene-breakdown.md"
    if not src.exists():
        sys.exit("CHƯA CÓ output/scene-breakdown.md — bước 2 chưa chạy.")
    md = src.read_text(encoding="utf-8")
    title_m = re.search(r"^#\s*Scene Breakdown:\s*(.+)$", md, re.M)
    title = title_m.group(1).strip() if title_m else ""
    scenes = []
    for line in md.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 9 or not cells[0].isdigit():
            continue  # bỏ header / separator
        scenes.append({
            "stt": int(cells[0]),
            "start": cells[1],
            "end": cells[2],
            "beat_type": cells[4],
            "mood": cells[5],
            "characters": norm_chars(cells[6]),
            "description": cells[7],
        })
    return title, scenes


def load_prompts():
    """Trả về dict {stt: prompt_text}."""
    j = OUTPUT / "prompts.json"
    if j.exists():
        d = json.loads(j.read_text(encoding="utf-8"))
        return {int(p["stt"]): p["prompt"].strip() for p in d["prompts"]}

    src = OUTPUT / "prompts.md"
    if not src.exists():
        sys.exit("CHƯA CÓ output/prompts.md — bước 3 chưa chạy.")
    md = src.read_text(encoding="utf-8")
    prompts = {}
    blocks = re.split(r"^##\s+(\d+)\s*$", md, flags=re.M)
    # blocks: [preamble, stt1, body1, stt2, body2, ...]
    for i in range(1, len(blocks) - 1, 2):
        stt = int(blocks[i])
        body = blocks[i + 1]
        m = re.search(r"\*\*Prompt:\*\*[^\n]*\n+(.*?)(?=\n---|\n##|\Z)", body, re.S)
        if m:
            text = " ".join(m.group(1).split())
            prompts[stt] = text
    return prompts


# ---------------------------------------------------------------- validate

def validate(meta, srt_total=None):
    """Trả về (errors[], warnings[]) theo rules 5.1 → 5.8."""
    errs, warns = [], []
    scenes = meta["scenes"]
    char_ids = {c["id"] for c in meta["characters"]}

    for i, sc in enumerate(scenes):
        p = f"Scene {sc.get('stt', '?')}"
        # 5.7 required fields
        for f in ("stt", "start", "end", "duration_s", "beat_type", "mood",
                  "description", "characters", "prompt", "image_file"):
            if f not in sc or sc[f] in (None, ""):
                if f == "characters" and sc.get(f) == []:
                    continue
                errs.append(f"{p}: thiếu field `{f}` (5.7)")
        # 5.6 timestamp format
        for f in ("start", "end"):
            if not TS_RE.match(str(sc.get(f, ""))):
                errs.append(f"{p}: timestamp `{f}` sai format HH:MM:SS (5.6)")
        # 5.2 sequential stt
        if sc.get("stt") != i + 1:
            errs.append(f"{p}: stt không liên tục, kỳ vọng {i + 1} (5.2)")
        # 5.4 file naming
        if sc.get("image_file") != f"{sc.get('stt')}.jpg":
            errs.append(f"{p}: image_file `{sc.get('image_file')}` không khớp stt (5.4)")
        # 5.5 duration
        if TS_RE.match(str(sc.get("start", ""))) and TS_RE.match(str(sc.get("end", ""))):
            real = ts_to_sec(sc["end"]) - ts_to_sec(sc["start"])
            if sc.get("duration_s") != real:
                errs.append(f"{p}: duration_s={sc.get('duration_s')} nhưng tính từ timestamp là {real} (5.5)")
            if real <= 0:
                errs.append(f"{p}: end <= start")
        # 5.3 character ids
        for cid in sc.get("characters", []):
            if cid not in char_ids:
                errs.append(f"{p}: character `{cid}` chưa define trong config (5.3)")
        # beat type hợp lệ
        if sc.get("beat_type") not in BEAT_TYPES:
            warns.append(f"{p}: beat_type `{sc.get('beat_type')}` không thuộc 6 loại chuẩn")
        # 5.1 gap/overlap
        if i > 0:
            prev = scenes[i - 1]
            if prev.get("end") != sc.get("start"):
                errs.append(f"{p}: start={sc.get('start')} != end scene trước ({prev.get('end')}) — gap/overlap (5.1)")

    # 5.1 tổng thời lượng
    total = sum(sc.get("duration_s", 0) for sc in scenes)
    if meta["project"].get("total_duration") != total:
        errs.append(f"project.total_duration={meta['project'].get('total_duration')} != tổng duration_s={total} (5.1)")
    if srt_total is not None and abs(total - srt_total) > 1:
        warns.append(f"Tổng duration ({total}s) lệch với SRT ({srt_total}s)")

    if meta["project"].get("total_scenes") != len(scenes):
        errs.append(f"project.total_scenes={meta['project'].get('total_scenes')} != số scene thực ({len(scenes)})")

    return errs, warns


def srt_total_seconds():
    srt = INPUT / "subtitle.srt"
    if not srt.exists():
        return None
    text = srt.read_text(encoding="utf-8", errors="replace")
    ends = re.findall(r"-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})", text)
    if not ends:
        return None
    h, m, s, ms = ends[-1]
    return int(h) * 3600 + int(m) * 60 + int(s) + (1 if int(ms) >= 500 else 0)


# ---------------------------------------------------------------- gates

BEAT_BOUNDS = {  # rule 3.1: min, max (giây)
    "establishing": (10, 18), "dialogue": (6, 12), "emotional_peak": (10, 18),
    "tension": (5, 10), "reflection": (10, 18), "resolution": (12, 25),
}


def gate_step2():
    """GATE bước 2 — kiểm tra scene-breakdown.md. Trả về (errors, warnings)."""
    errs, warns = [], []
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    char_ids = {c["id"] for c in config.get("characters", [])}
    moods = set(config.get("mood_map", {}).keys())
    _, scenes = load_scenes()
    srt_end = srt_total_seconds()

    if not scenes:
        return ["scene-breakdown.md không có dòng scene nào"], []

    # Coverage — lỗi nghiêm trọng nhất (dấu hiệu tràn context)
    if scenes[0]["start"] != "00:00:00":
        errs.append(f"Scene 1 bắt đầu {scenes[0]['start']}, phải là 00:00:00")
    if srt_end is not None:
        last_end = ts_to_sec(scenes[-1]["end"])
        if abs(last_end - srt_end) > 1:
            miss = srt_end - last_end
            errs.append(
                f"COVERAGE FAIL: bảng dừng ở {scenes[-1]['end']} nhưng SRT dài {srt_end}s "
                f"— THIẾU {miss}s ({miss/60:.1f} phút). Bước 2 CHƯA XONG."
            )

    prev = None
    streak, streak_beat = 0, None
    for s in scenes:
        p = f"Scene {s['stt']}"
        dur = ts_to_sec(s["end"]) - ts_to_sec(s["start"])
        if dur <= 0:
            errs.append(f"{p}: Dur={dur}s — phải gộp vào scene liền kề")
        if prev and prev["end"] != s["start"]:
            errs.append(f"{p}: gap/overlap với scene trước (end {prev['end']} vs start {s['start']})")
        if s["beat_type"] not in BEAT_TYPES:
            errs.append(f"{p}: beat_type `{s['beat_type']}` không hợp lệ")
        else:
            lo, hi = BEAT_BOUNDS[s["beat_type"]]
            if dur > 0 and not (lo <= dur <= hi):
                warns.append(f"{p}: {s['beat_type']} {dur}s ngoài khoảng {lo}-{hi}s (rule 3.1)")
        if s["mood"] not in moods:
            warns.append(f"{p}: mood `{s['mood']}` không có trong mood_map")
        for cid in s["characters"]:
            if cid not in char_ids:
                errs.append(f"{p}: character `{cid}` chưa define trong config")
        # 4+ liên tiếp cùng beat
        if s["beat_type"] == streak_beat:
            streak += 1
            if streak == 4:
                warns.append(f"{p}: 4+ scene liên tiếp cùng beat `{streak_beat}` (rule 3.2)")
        else:
            streak, streak_beat = 1, s["beat_type"]
        prev = s
    return errs, warns


# Rule 2.1a — style không được trộn 2 medium
PHOTO_TOKENS = {"photorealistic", "photograph", "photo", "film still", "35mm", "dslr"}
ILLUS_TOKENS = {"illustration", "painting", "painterly", "drawn", "cartoon", "anime", "watercolor"}
# Rule 4.6 — từ hàm ý cốt truyện / phủ định / âm thanh (model vẽ sai hoặc không vẽ được)
NARRATIVE_WORDS = r"\b(secret|hidden|mysterious|forbidden|unknown|invisible|unseen|memories|remembering)\b"
NEGATION_WORDS = r"\b(no|not|without|never)\b"
AUDIO_WORDS = r"\b(sound|noise|music|loud|humming|droning|echoing|silence|whisper(?:ing)?)\b"


def gate_step3():
    """GATE bước 3 — kiểm tra prompts.md khớp scene-breakdown + rules 4.x."""
    errs, warns = [], []
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    style = config.get("style", "").strip()
    _, scenes = load_scenes()
    prompts = load_prompts()

    # Rule 2.1a — medium dứt khoát
    s = style.lower()
    has_photo = any(tok in s for tok in PHOTO_TOKENS)
    has_illus = any(tok in s for tok in ILLUS_TOKENS)
    if has_photo and has_illus:
        errs.append("Style string trộn 2 medium (photo + illustration) — vi phạm Rule 2.1a, gây ảnh lúc thật lúc vẽ")
    if not has_photo and not has_illus:
        warns.append("Style string chưa tuyên bố medium rõ ràng (photograph hay illustration?) — Rule 2.1a")

    scene_stts = {s["stt"] for s in scenes}
    missing = sorted(scene_stts - set(prompts))
    extra = sorted(set(prompts) - scene_stts)
    if missing:
        errs.append(f"THIẾU prompt cho {len(missing)} scene: {missing[:15]}{'...' if len(missing) > 15 else ''}")
    if extra:
        errs.append(f"Prompt thừa (không có scene): {extra[:15]}")

    # Rule 1.1a — nano_name KHÔNG được dính liền sở hữu cách ('s) — phá vỡ tham chiếu ảnh ingredient
    nano_names = [c["nano_name"] for c in config.get("characters", []) if c.get("nano_name")]

    for stt in sorted(set(prompts) & scene_stts):
        text = prompts[stt]
        n = len(text.split())
        if n < 20 or n > 75:
            (errs if n < 15 or n > 90 else warns).append(f"Prompt {stt}: {n} từ (chuẩn 20-75, rule 4.4)")
        if style and style not in text:
            errs.append(f"Prompt {stt}: thiếu style anchor nguyên văn (rule 2.1)")
        if style and text.count(style) > 1:
            errs.append(f"Prompt {stt}: style anchor bị lặp {text.count(style)} lần")
        # Rule 4.6 — phần mô tả (bỏ style anchor) không chứa từ cấm
        body = text.replace(style, "").lower()
        for pat, label in ((NARRATIVE_WORDS, "từ hàm ý cốt truyện"),
                           (NEGATION_WORDS, "từ phủ định (positive framing)"),
                           (AUDIO_WORDS, "từ âm thanh")):
            hits = sorted(set(re.findall(pat, body)))
            if hits:
                warns.append(f"Prompt {stt}: {label}: {', '.join(hits)} (rule 4.6)")
        # Rule 4.8 — shot type phải kèm lens
        if re.search(r"\b(shot|close-up)\b", body) and "lens" not in body:
            warns.append(f"Prompt {stt}: shot type chưa kèm lens (rule 4.8)")
        # Rule 1.1a — nano_name dính liền sở hữu cách 's — LỖI cứng, phá vỡ tham chiếu ảnh ingredient
        for nn in nano_names:
            if re.search(r"\b" + re.escape(nn) + r"'s\b", text):
                errs.append(f"Prompt {stt}: `{nn}'s` — nano_name dính liền sở hữu cách, phá vỡ tham chiếu ảnh ingredient (Rule 1.1a)")
        # Rule 2.5 — Era Lock: vật thể ngoài niên đại là LỖI
        forbidden = config.get("era", {}).get("forbidden", [])
        for w in forbidden:
            if re.search(r"\b" + re.escape(w.lower()) + r"\b", body):
                errs.append(f"Prompt {stt}: chứa `{w}` — ngoài niên đại era (Rule 2.5)")

    # Rule 6.x — Video Hook
    vh = config.get("video_hook", {})
    if vh.get("enabled"):
        e2, w2 = check_video_hook(vh, scenes, prompts, config)
        errs += e2
        warns += w2
    return errs, warns


CAMERA_WORDS = r"(push[- ]in|pull[- ]back|pan|dolly|tracking|static camera|zoom|tilt|sway|crane|handheld|locked[- ]off|camera holds)"
# Rule 6.6 — từ gây đứt gãy thời gian → subject vanishing
DISCONTINUITY_WORDS = r"\b(suddenly|appears?|disappears?|vanish(?:es)?|reveal(?:s|ing)?|transforms?|morphs?|materializes?|teleports?|cut to)\b"


def check_video_hook(vh, scenes, prompts, config=None):
    """Rule 6.1→6.6 — kiểm video-prompts.md."""
    errs, warns = [], []
    config = config or {}
    nano = {c["id"]: c.get("nano_name", "") for c in config.get("characters", [])}
    scene_chars = {s["stt"]: s["characters"] for s in scenes}
    f = OUTPUT / "video-prompts.md"
    if not f.exists():
        return [f"video_hook bật nhưng thiếu {f.name} (Rule 6.4)"], []
    md = f.read_text(encoding="utf-8")
    dur_s, max_clip = vh.get("duration_s", 120), vh.get("max_clip_s", 8)

    hook_scenes = [s for s in scenes if ts_to_sec(s["start"]) < dur_s]
    if not hook_scenes:
        return ["video_hook: không scene nào trong cửa sổ duration_s"], []
    hook_end = ts_to_sec(hook_scenes[-1]["end"])

    blocks = re.findall(
        r"^## Clip (\d+)\.(\d+)\s*\n\*\*Scene:\*\* (\d+) \| \*\*Time:\*\* (\d{2}:\d{2}:\d{2}) → (\d{2}:\d{2}:\d{2}) \| \*\*Duration:\*\* (\d+)s",
        md, re.M)
    if not blocks:
        return ["video-prompts.md không parse được block Clip nào (sai format Rule 6.4)"], []

    prev_end = 0
    for stt, k, stt2, t1, t2, d in blocks:
        cid = f"Clip {stt}.{k}"
        a, b = ts_to_sec(t1), ts_to_sec(t2)
        if int(d) != b - a:
            errs.append(f"{cid}: Duration {d}s != {b - a}s tính từ Time")
        if b - a > max_clip:
            errs.append(f"{cid}: {b - a}s vượt max_clip_s={max_clip}")
        if b - a < 2:
            warns.append(f"{cid}: chỉ {b - a}s — quá ngắn, cân nhắc gộp/trim")
        if a != prev_end:
            errs.append(f"{cid}: start {t1} không nối tiếp clip trước ({prev_end}s) — gap/overlap")
        prev_end = b
    if prev_end != hook_end:
        errs.append(f"Video hook phủ đến {prev_end}s nhưng scene hook cuối kết thúc {hook_end}s")

    # clip .1 phải kèm image prompt nguyên văn; video prompt có camera motion, không dialogue
    for m in re.finditer(r"^## Clip (\d+)\.1\s*\n(.*?)(?=\n## Clip|\Z)", md, re.M | re.S):
        stt, body = int(m.group(1)), m.group(2)
        im = re.search(r"\*\*Image Prompt[^\n]*\n(.*?)(?=\n\*\*Video Prompt)", body, re.S)
        if not im:
            errs.append(f"Clip {stt}.1: thiếu Image Prompt (ảnh 1) — Rule 6.4")
        elif stt in prompts and " ".join(im.group(1).split()) != prompts[stt]:
            errs.append(f"Clip {stt}.1: Image Prompt không khớp nguyên văn prompts.md (scene {stt})")
    for m in re.finditer(r"^## Clip (\d+)\.(\d+)\s*\n(.*?)(?=\n## Clip|\Z)", md, re.M | re.S):
        cid = f"Clip {m.group(1)}.{m.group(2)}"
        vp = re.search(r"\*\*Video Prompt:\*\*\s*\n(.*?)(?=\n---|\Z)", m.group(3), re.S)
        if not vp:
            errs.append(f"{cid}: thiếu Video Prompt")
            continue
        text = " ".join(vp.group(1).split())
        if not re.search(CAMERA_WORDS, text, re.I):
            warns.append(f"{cid}: video prompt chưa có camera motion (Rule 6.3)")
        if re.search(r'"[^"]{3,}"', text):
            errs.append(f"{cid}: video prompt chứa dialogue trong ngoặc kép (Rule 6.3 cấm)")
        # Rule 6.6 — subject persistence
        hits = sorted(set(re.findall(DISCONTINUITY_WORDS, text, re.I)))
        if hits:
            errs.append(f"{cid}: từ gây đứt gãy/subject vanishing: {', '.join(hits)} (Rule 6.6)")
        stt_n = int(m.group(1))
        for cid2 in scene_chars.get(stt_n, []):
            nn = nano.get(cid2, "")
            if nn and nn.lower() not in text.lower():
                errs.append(f"{cid}: thiếu subject anchor `{nn}` — nguy cơ nhân vật biến mất (Rule 6.6)")
            # Rule 1.1a — nano_name dính liền sở hữu cách 's trong video prompt
            if nn and re.search(r"\b" + re.escape(nn) + r"'s\b", text):
                errs.append(f"{cid}: `{nn}'s` — nano_name dính liền sở hữu cách, phá vỡ tham chiếu ảnh ingredient (Rule 1.1a)")
        if len(re.findall(r"\bthen\b", text, re.I)) >= 2:
            warns.append(f"{cid}: nhiều 'then' — nhồi nhiều diễn biến vào 1 clip (Rule 6.6)")

    # Rule 6.7 — chống clip trùng lặp trong cùng scene (hook phẳng)
    vstyle = set(vh.get("video_style", "").lower().replace(",", " ").split())
    by_scene = {}
    for m in re.finditer(r"^## Clip (\d+)\.(\d+)\s*\n(.*?)(?=\n## Clip|\Z)", md, re.M | re.S):
        vp = re.search(r"\*\*Video Prompt:\*\*\s*\n(.*?)(?=\n---|\Z)", m.group(3), re.S)
        if vp:
            words = set(re.findall(r"[a-z']+", vp.group(1).lower())) - vstyle
            by_scene.setdefault(int(m.group(1)), []).append((int(m.group(2)), words))
    for stt, lst in by_scene.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                (k1, w1), (k2, w2) = lst[i], lst[j]
                if not w1 or not w2:
                    continue
                sim = len(w1 & w2) / len(w1 | w2)
                if sim >= 0.75:
                    errs.append(f"Clip {stt}.{k1} vs {stt}.{k2}: trùng lặp {sim:.0%} — mỗi clip phải có beat thị giác MỚI (Rule 6.7)")
                elif sim >= 0.55:
                    warns.append(f"Clip {stt}.{k1} vs {stt}.{k2}: giống nhau {sim:.0%} — cân nhắc thêm thông tin thị giác mới (Rule 6.7)")
    return errs, warns


def run_gate(name, fn):
    errs, warns = fn()
    print(f"== GATE {name}")
    if warns:
        print(f"CẢNH BÁO ({len(warns)}):")
        for w in warns[:25]:
            print(f"  ⚠ {w}")
        if len(warns) > 25:
            print(f"  ... và {len(warns) - 25} cảnh báo khác")
    if errs:
        print(f"LỖI ({len(errs)}):")
        for e in errs[:40]:
            print(f"  ✗ {e}")
        print(f"\n✗ FAIL — {name} CHƯA XONG, sửa lỗi rồi chạy lại gate.")
        sys.exit(1)
    print(f"✓ PASS — {name} đạt chuẩn.")
    sys.exit(0)


# ---------------------------------------------------------------- main

SHOT_CATS = [  # (regex, nhóm)
    (r"extreme wide shot|wide shot", "wide"),
    (r"medium close-up|medium shot", "medium"),
    (r"extreme close-up|close-up", "closeup"),
    (r"over[- ](?:the[- ])?shoulder|low angle|high angle", "angle"),
]


def shot_cat(body):
    order = [(r"extreme close-up", "closeup"), (r"medium close-up", "medium"),
             (r"extreme wide shot", "wide"), (r"over[- ](?:the[- ])?shoulder", "angle"),
             (r"wide shot", "wide"), (r"medium shot", "medium"),
             (r"close-up", "closeup"), (r"two shot", "medium")]
    for pat, cat in order:
        if re.search(pat, body):
            return cat
    return None


def gate_qc():
    """BƯỚC 5 QC — tầng máy: mọi thứ đo đếm được. Ghi report ra output/qc-report.md."""
    errs, warns = [], []
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    style = config.get("style", "").strip()
    mood_map = config.get("mood_map", {})
    fb = config.get("flashback_style", "").strip()
    nano = {c["id"]: c.get("nano_name", "") for c in config.get("characters", [])}
    variants = {cid for cid in nano if "_" in cid}
    _, scenes = load_scenes()
    prompts = load_prompts()

    # chạy lại 2 gate nền
    e, w = gate_step2(); errs += [f"[step2] {x}" for x in e]; warns += [f"[step2] {x}" for x in w]
    e, w = gate_step3(); errs += [f"[step3] {x}" for x in e]; warns += [f"[step3] {x}" for x in w]

    cats, streak_cat, streak = [], None, 0
    seen = {}
    for s in scenes:
        stt = s["stt"]
        if stt not in prompts:
            continue
        text = prompts[stt]
        body = text.replace(style, "").lower()
        p = f"Scene {stt}"

        # QC1 — nhân vật: nano_name phải có trong prompt (character lock)
        for cid in s["characters"]:
            nn = nano.get(cid, "")
            if nn and nn.lower() not in body:
                errs.append(f"{p}: thiếu nano_name `{nn}` (character `{cid}`) trong prompt (QC1)")

        # QC2 — mood keywords verbatim từ mood_map (rule 2.2)
        mk = mood_map.get(s["mood"], "")
        if mk and mk.lower() not in body:
            errs.append(f"{p}: thiếu mood keywords nguyên văn cho mood `{s['mood']}` (QC2)")

        # QC3 — flashback variant phải kèm flashback_style
        if fb and any(c in variants for c in s["characters"]) and fb.lower() not in text.lower():
            warns.append(f"{p}: có variant quá khứ nhưng thiếu flashback_style (QC3)")

        # QC4 — trùng lặp prompt (monotony)
        key = " ".join(body.split()[:12])
        if key in seen:
            warns.append(f"{p}: 12 từ đầu prompt trùng Scene {seen[key]} — nguy cơ 2 ảnh giống nhau (QC4)")
        seen[key] = stt

        # QC5 — shot variety
        c = shot_cat(body)
        cats.append((stt, c))
        if c and c == streak_cat:
            streak += 1
            lim = 2 if c == "closeup" else 3
            if streak == lim + 1:
                warns.append(f"{p}: {streak} scene liên tiếp cùng nhóm shot `{c}` (rule 4.2)")
        else:
            streak_cat, streak = c, 1

    # QC5b — distribution mỗi cửa sổ 10 scene (rule 4.2)
    for i in range(0, len(cats) - 9, 10):
        win = cats[i:i + 10]
        cnt = {}
        for _, c in win:
            cnt[c] = cnt.get(c, 0) + 1
        need = {"wide": 2, "medium": 3, "closeup": 2, "angle": 1}
        for grp, mn in need.items():
            if cnt.get(grp, 0) < mn:
                warns.append(f"Scenes {win[0][0]}-{win[-1][0]}: nhóm shot `{grp}` chỉ {cnt.get(grp, 0)}/{mn} tối thiểu (rule 4.2)")

    # ghi report
    rep = ["# QC Report (tầng máy — tự sinh bởi export.py --qc)", ""]
    rep.append(f"Scenes: {len(scenes)} | Prompts: {len(prompts)} | Lỗi: {len(errs)} | Cảnh báo: {len(warns)}")
    rep.append("")
    if errs:
        rep.append("## LỖI (phải sửa)\n")
        rep += [f"- ✗ {x}" for x in errs]
    if warns:
        rep.append("\n## CẢNH BÁO (cân nhắc)\n")
        rep += [f"- ⚠ {x}" for x in warns]
    rep.append("""
## QC định tính (AI/người thực hiện sau khi tầng máy PASS — rubric trong .claude/rules/qc.md)

- [ ] HOOK: đọc toàn bộ scene + video prompt trong cửa sổ hook, đối chiếu SRT — mỗi clip có 1 chuyển động/thông tin thị giác mới, không 2 clip liền kề cùng camera motion, ảnh mở vòng lặp thị giác đúng narration
- [ ] SUBJECT PERSISTENCE (Rule 6.6): từng video prompt neo subject bằng nano_name + đặc điểm nhận diện, 1 chuyển động chính liên tục, camera bám subject, clip Extend giữ nguyên mô tả — chống nhân vật biến mất giữa clip
- [ ] MOOD ARC: bảng cảm xúc leo thang đúng cấu trúc — emotional_peak nổi bật hơn scene liền trước (shot gần hơn hoặc lighting tương phản)
- [ ] KHỚP NARRATION: sample ≥10 scene ngẫu nhiên giữa bài — prompt không mâu thuẫn description (trang phục, vật thể, thời tiết, trạng thái vật lý)
- [ ] VISUAL STATE: không từ trừu tượng/cốt truyện sót lại, vật thể chính có chất liệu, trạng thái đóng/mở/cũ/mới tường minh
- [ ] ERA: sample close-up vật thể — đúng niên đại, không anachronism ngoài danh sách forbidden
- [ ] KẾT LUẬN: PASS / FAIL + danh sách scene cần sửa

Verdict cuối: (điền sau khi QC định tính)
""")
    (OUTPUT / "qc-report.md").write_text("\n".join(rep), encoding="utf-8")
    return errs, warns


def export_prompts_list():
    """Xuất output/prompts-list.txt từ metadata.json — prompt đánh số thứ tự, cách nhau 1 dòng trống, để copy chạy hàng loạt."""
    meta_file = OUTPUT / "metadata.json"
    if not meta_file.exists():
        sys.exit("LỖI: chưa có output/metadata.json — chạy Bước 4 (python3 scripts/export.py) trước.")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    entries = [f"{sc['stt']}. {sc['prompt']}" for sc in meta["scenes"]]
    out_file = OUTPUT / "prompts-list.txt"
    out_file.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    print(f"✓ Đã ghi {out_file.name} — {len(entries)} prompt.")
    sys.exit(0)


def _tagify(s):
    """Chuyển tên hiển thị (nano_name/id) thành ASSET_TAG viết hoa, gạch dưới — quy ước Uni-X."""
    return re.sub(r"[^A-Z0-9]+", "_", s.upper()).strip("_")


UNIX_BATCH_SIZE = 100


def export_unix():
    """Xuất output/unix-batch-NN.txt theo cú pháp Uni-X Studio:
    (Image Prompt i/n)
    Assets: TAG1, TAG2
    Prompt: ... [TAG1] ... [TAG2] ...
    Chia nhóm tối đa 100 ảnh/file (giới hạn 1 lượt vẽ của Uni-X)."""
    meta_file = OUTPUT / "metadata.json"
    if not meta_file.exists():
        sys.exit("LỖI: chưa có output/metadata.json — chạy Bước 4 (python3 scripts/export.py) trước.")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))

    char_tag = {c["id"]: _tagify(c["nano_name"]) for c in config.get("characters", []) if c.get("nano_name")}
    char_name = {c["id"]: c["nano_name"] for c in config.get("characters", [])}
    settings = config.get("settings", [])
    setting_tag = {s["id"]: _tagify(s["id"]) for s in settings}

    def find_setting_id(prompt_text):
        for s in settings:
            probe = s["keywords"].split(", ")[0]
            if probe and probe in prompt_text:
                return s["id"]
        return None

    rows, unmatched = [], []
    for sc in meta["scenes"]:
        text = sc["prompt"]
        tags = []
        for cid in sc["characters"]:
            if cid not in char_tag:
                continue
            tag, name = char_tag[cid], char_name[cid]
            tags.append(tag)
            # cú pháp [TAG] tự phân định ranh giới nên không cần né sở hữu cách như Rule 1.1a
            # (khác Flow — Flow khớp theo tên trần trong văn bản, dễ vỡ khi dính 's ngay sau tên)
            m = re.search(r"\b" + re.escape(name) + r"\b", text)
            if m:
                text = text[:m.start()] + f"[{tag}]" + text[m.end():]
        sid = find_setting_id(text)
        if sid:
            tag = setting_tag[sid]
            tags.append(tag)
            probe = next(s["keywords"] for s in settings if s["id"] == sid).split(", ")[0]
            idx = text.find(probe)
            if idx != -1:
                text = text[:idx] + f"[{tag}] " + text[idx:]
        else:
            unmatched.append(sc["stt"])
        rows.append((sc["stt"], list(dict.fromkeys(tags)), text))

    n_batches = (len(rows) + UNIX_BATCH_SIZE - 1) // UNIX_BATCH_SIZE
    written = []
    for b in range(n_batches):
        chunk = rows[b * UNIX_BATCH_SIZE:(b + 1) * UNIX_BATCH_SIZE]
        out_file = OUTPUT / f"unix-batch-{b + 1:02d}.txt"
        n = len(chunk)
        body = []
        for i, (stt, tags, text) in enumerate(chunk, start=1):
            body.append(f"(Image Prompt {i}/{n})")
            body.append(f"Assets: {', '.join(tags)}")
            body.append(f"Prompt: {text}")
            body.append("")
        out_file.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
        written.append((out_file.name, chunk[0][0], chunk[-1][0], n))

    for name, lo, hi, n in written:
        print(f"✓ Đã ghi {name} — scene {lo}-{hi} ({n} ảnh)")
    if unmatched:
        print(f"⚠ {len(unmatched)} scene không xác định được setting/asset bối cảnh (Assets chỉ có nhân vật): {unmatched[:20]}{'...' if len(unmatched) > 20 else ''}")
    sys.exit(0)


def main():
    if "--prompts-list" in sys.argv:
        export_prompts_list()
    if "--unix-export" in sys.argv:
        export_unix()
    if "--step2" in sys.argv:
        run_gate("BƯỚC 2 (scene-breakdown)", gate_step2)
    if "--step3" in sys.argv:
        run_gate("BƯỚC 3 (prompts)", gate_step3)
    if "--qc" in sys.argv:
        run_gate("QC (tầng máy) — report: output/qc-report.md", gate_qc)
    validate_only = "--validate" in sys.argv
    out_file = OUTPUT / "metadata.json"

    if validate_only:
        meta = json.loads(out_file.read_text(encoding="utf-8"))
    else:
        config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
        title, scenes = load_scenes()
        prompts = load_prompts()

        missing = [s["stt"] for s in scenes if s["stt"] not in prompts]
        if missing:
            sys.exit(f"LỖI: thiếu prompt cho scene: {missing} — kiểm tra prompts.md/prompts.json")

        meta_scenes = []
        for s in scenes:
            dur = ts_to_sec(s["end"]) - ts_to_sec(s["start"])
            meta_scenes.append({
                "stt": s["stt"],
                "start": s["start"],
                "end": s["end"],
                "duration_s": dur,
                "beat_type": s["beat_type"],
                "mood": s["mood"],
                "description": s["description"],
                "characters": s["characters"],
                "prompt": prompts[s["stt"]],
                "image_file": f"{s['stt']}.jpg",
            })

        meta = {
            "project": {
                "title": title or config.get("project", {}).get("title", ""),
                "style": config.get("style", ""),
                "total_scenes": len(meta_scenes),
                "total_duration": sum(x["duration_s"] for x in meta_scenes),
            },
            "characters": config.get("characters", []),
            "scenes": meta_scenes,
        }

    errs, warns = validate(meta, srt_total_seconds())

    if not validate_only:
        out_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ----- báo cáo
    beats = {}
    for sc in meta["scenes"]:
        beats[sc["beat_type"]] = beats.get(sc["beat_type"], 0) + 1
    n = len(meta["scenes"])
    print(f"== {'VALIDATE' if validate_only else 'EXPORT'}: {meta['project']['title'][:60]}")
    print(f"Scenes: {n} | Tổng thời lượng: {meta['project']['total_duration']}s")
    print("Beat distribution: " + ", ".join(f"{k}: {v} ({v*100//n}%)" for k, v in sorted(beats.items())))
    if warns:
        print(f"\nCẢNH BÁO ({len(warns)}):")
        for w in warns[:20]:
            print(f"  ⚠ {w}")
    if errs:
        print(f"\nLỖI ({len(errs)}):")
        for e in errs[:40]:
            print(f"  ✗ {e}")
        sys.exit(1)
    print("\n✓ PASS toàn bộ rules 5.1–5.8" + ("" if validate_only else f" — đã ghi {out_file.name}"))


if __name__ == "__main__":
    main()
