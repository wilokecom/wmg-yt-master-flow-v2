#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bước 5 — Export metadata.json (tự động, không cần AI viết tay).

Nguồn dữ liệu (ưu tiên JSON, fallback parse Markdown):
  1. output/scene-breakdown.json  (nếu có)  else parse output/scene-breakdown.md
  2. output/prompts.json          (nếu có)  else parse output/prompts.md
  3. input/config.json
  4. output/sfx.json              (tùy chọn — Bước 3, merge field sfx theo stt)

Output: output/metadata.json + báo cáo validate (rules 5.1 → 5.8) in ra stdout.

Cách chạy (từ thư mục gốc project):
    python3 scripts/export.py            # export + validate (bước 5)
    python3 scripts/export.py --validate # chỉ validate metadata.json hiện có
    python3 scripts/export.py --step1    # GATE bước 1: đếm asset (nhân vật/bối cảnh/tổng) + character-refs.md phủ đủ
    python3 scripts/export.py --refs-list     # xuất output/character-refs-list.txt (prompt đánh số, copy vẽ ảnh ingredient hàng loạt) + character-refs-map.txt (ảnh thứ N → TAG.jpg để đổi tên)
    python3 scripts/export.py --step2    # GATE bước 2: scene-breakdown.md đạt chuẩn chưa
    python3 scripts/export.py --step3    # GATE bước 3: output/sfx.json đạt chuẩn chưa (cần beat xong trước)
    python3 scripts/export.py --sfx-export    # xuất output/sfx-timeline.json — MODULE SFX ĐỘC LẬP (timestamp+keywords), chỉ cần bước 1-3
    python3 scripts/export.py --step4    # GATE bước 4: prompts.md đạt chuẩn chưa
    python3 scripts/export.py --prompts-list  # xuất output/prompts-list.txt (prompt đánh số, để copy chạy hàng loạt)
    python3 scripts/export.py --video-list    # xuất output/video-prompts-list.txt (ảnh phụ cần vẽ + video prompt đánh số)
    python3 scripts/export.py --unix-export   # xuất output/unix-batch-NN.txt (cú pháp Uni-X Studio, nhóm 100 ảnh/file)

QUY TẮC: bước 2/3/4 CHƯA XONG chừng nào gate tương ứng chưa PASS.
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
            "visual_notes": cells[8] if len(cells) > 8 else "",
            # SFX KHÔNG còn nằm trong scene-breakdown — tách sang Bước 3 (output/sfx.json),
            # merge vào metadata theo stt lúc export (xem load_sfx/merge_sfx).
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
        sys.exit("CHƯA CÓ output/prompts.md — bước 4 chưa chạy.")
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


# ---------------------------------------------------------------- typewriter cues
# input/typewriter.json (TÙY CHỌN) — nguồn duy nhất cho hiệu ứng đánh máy (editor overlay).
# 1 nguồn → 2 output: field `typewriter` trong metadata.json + output/typewriter-cues.md.
# Không có file nguồn → pipeline chạy y như cũ.

def load_typewriter():
    f = INPUT / "typewriter.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def merge_typewriter(tw, meta_scenes):
    """Gắn cue vào scene khớp stt trong meta_scenes. Trả (errors, warnings, n_merged)."""
    errs, warns = [], []
    by_stt = {sc["stt"]: sc for sc in meta_scenes}
    n = 0
    for cue in tw.get("cues", []):
        cid = f"Typewriter cue {cue.get('id', '?')}"
        stt = cue.get("stt")
        if stt not in by_stt:
            errs.append(f"{cid}: stt {stt} không tồn tại trong scenes")
            continue
        if not str(cue.get("text", "")).strip():
            errs.append(f"{cid}: text rỗng")
            continue
        sc = by_stt[stt]
        at = cue.get("at", "")
        # KAIZEN 2026-07-22 (typewriter) — thời lượng gõ tính MÁY từ độ dài text
        # (65+ gõ chậm ~0.18s/ký tự, kẹp 1.5–6.0s) để editor đặt âm gõ phím bắt đầu
        # tại `at` và DỪNG đúng lúc chữ gõ xong — chữ và âm khớp nhau máy móc.
        type_s = min(6.0, max(1.5, round(len(str(cue.get("text", ""))) * 0.18, 1)))
        if TS_RE.match(str(at)):
            # at lệch scene = LỖI CỨNG (trước là cảnh báo): chữ sẽ hiện đè lên scene khác
            # → đúng loại bug "chữ 1 nơi, âm đánh chữ 1 nơi".
            if not (ts_to_sec(sc["start"]) <= ts_to_sec(at) < ts_to_sec(sc["end"])):
                errs.append(f"{cid}: at={at} NGOÀI khoảng scene {stt} [{sc['start']}–{sc['end']}) — "
                            f"cue phải nằm trong scene của nó; sửa `at` hoặc `stt` trong input/typewriter.json")
                continue
            if ts_to_sec(at) + type_s > ts_to_sec(sc["end"]):
                warns.append(f"{cid}: chữ gõ {type_s}s từ at={at} sẽ CHƯA XONG khi scene {stt} kết thúc ({sc['end']}) "
                             f"— dời `at` sớm hơn hoặc rút ngắn text")
        else:
            warns.append(f"{cid}: at `{at}` sai format HH:MM:SS")
        sc["typewriter"] = {k: v for k, v in cue.items() if k != "stt"}
        sc["typewriter"]["type_s"] = type_s
        n += 1
    return errs, warns, n


def write_typewriter_cues(tw, meta_scenes):
    """Sinh output/typewriter-cues.md cho editor từ cùng nguồn đã merge vào metadata."""
    by_stt = {sc["stt"]: sc for sc in meta_scenes}
    lines = ["# Typewriter Cues — hiệu ứng đánh máy (overlay lúc dựng — SINH BỞI export.py, sửa nguồn input/typewriter.json)", ""]
    # KAIZEN 2026-07-22 — hợp đồng ÂM THANH tường minh cho editor: bug thực tế là âm gõ phím
    # bị rải khắp video (cả đoạn không có chữ) và lệch thời gian với chữ.
    lines += [
        "**QUY TẮC ÂM THANH ĐÁNH CHỮ (BẮT BUỘC khi dựng):**",
        "1. Âm gõ phím CHỈ phát tại đúng cột `Time` của từng cue, chạy đồng bộ với chữ đang gõ, DỪNG sau đúng `Gõ (s)` giây (lúc chữ gõ xong).",
        "2. Scene KHÔNG có trong bảng này = KHÔNG có chữ và KHÔNG có âm đánh chữ.",
        "3. Âm đánh chữ KHÔNG lấy từ field `sfx` trong metadata.json — `sfx` là âm bối cảnh của cảnh (gió, cửa, bước chân...), trộn ở lớp riêng, không liên quan hiệu ứng chữ.",
        "",
    ]
    for k, v in tw.get("style", {}).items():
        lines.append(f"- **{k}**: {v}")
    lines += ["", "| # | Time | Gõ (s) | Scene | Ảnh nền | Loại | Text gõ | Sync |", "|---|---|---|---|---|---|---|---|"]
    for cue in tw.get("cues", []):
        sc = by_stt.get(cue.get("stt"))
        if not sc:
            continue
        text = str(cue.get("text", "")).replace("|", "/").replace("\n", " ↵ ")
        sync = str(cue.get("sync", "")).replace("|", "/")
        type_s = (sc.get("typewriter") or {}).get("type_s", min(6.0, max(1.5, round(len(str(cue.get("text", ""))) * 0.18, 1))))
        lines.append(f"| {cue.get('id', '')} | {cue.get('at', '')} | {type_s} | {cue['stt']} ({sc['start']}–{sc['end']}) | {sc['image_file']} | {cue.get('type', '')} | `{text}` | {sync} |")
    notes = tw.get("notes", [])
    if notes:
        lines.append("")
        for nt in notes:
            lines.append(f"> {nt}")
    out = OUTPUT / "typewriter-cues.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------- SFX (Bước 3)

def load_sfx():
    """Đọc output/sfx.json (do Bước 3 sinh). None nếu chưa có."""
    f = OUTPUT / "sfx.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def merge_sfx(sfx, meta_scenes):
    """Gắn field sfx (mảng keyword) vào scene khớp stt. Trả (errors, warnings, n_merged).

    sfx.json schema:
      {"sfx": [{"stt": 1, "keywords": ["rotary phone dialing", ...]}, {"stt": 2, "keywords": []}, ...]}
    """
    errs, warns = [], []
    by_stt = {sc["stt"]: sc for sc in meta_scenes}
    seen = set()
    for e in sfx.get("sfx", []):
        stt = e.get("stt")
        if stt not in by_stt:
            errs.append(f"SFX stt {stt} không tồn tại trong scenes")
            continue
        kws = e.get("keywords", [])
        if not isinstance(kws, list):
            errs.append(f"SFX stt {stt}: keywords phải là mảng")
            continue
        by_stt[stt]["sfx"] = [str(k).strip() for k in kws
                              if str(k).strip() and str(k).strip() not in ("-", "—")]
        seen.add(stt)
    missing = sorted(set(by_stt) - seen)
    if missing:
        warns.append(f"{len(missing)} scene chưa có entry trong sfx.json (giữ sfx=[]): {missing[:15]}"
                     f"{'...' if len(missing) > 15 else ''}")
    return errs, warns, len(seen)


# ---------------------------------------------------------------- gates

BEAT_BOUNDS = {  # rule 3.1: min, max (giây)
    "establishing": (10, 18), "dialogue": (6, 12), "emotional_peak": (10, 18),
    "tension": (5, 10), "reflection": (10, 18), "resolution": (12, 25),
}
# rule 3.3 — chuyển beat cấm trực tiếp (phải có beat đệm ở giữa)
FORBIDDEN_TRANS = {
    ("tension", "resolution"), ("establishing", "emotional_peak"), ("resolution", "tension"),
}
REST_BEATS = {"establishing", "reflection"}  # rule 3.6 — beat "nghỉ mắt"


def gate_step1():
    """GATE bước 1 — đếm asset (nhân vật + bối cảnh + tổng) & kiểm character-refs.md phủ đủ.

    Nguồn đếm = config.json (characters[] + settings[]) — chính xác, kể cả variant.
    In dòng đếm ra stdout để user tick khi vẽ ingredient, dù PASS hay FAIL.
    """
    errs, warns = [], []
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    chars = config.get("characters", [])
    setts = config.get("settings", [])
    nchar, nset = len(chars), len(setts)
    total = nchar + nset
    print(f"── ĐẾM ASSET (từ config.json): Nhân vật: {nchar} | Bối cảnh: {nset} | TỔNG asset cần vẽ: {total}")

    # sanity config
    if nchar == 0:
        errs.append("config.characters[] rỗng — chưa có nhân vật nào.")
    for c in chars:
        if not (c.get("nano_name") or "").strip():
            errs.append(f"character id `{c.get('id', '?')}` thiếu nano_name.")
    for s in setts:
        if not (s.get("id") or "").strip():
            errs.append("có setting thiếu `id`.")

    # Rule 2.2/4.7 — mood_map CHỈ được chứa ánh sáng + màu + khung hình, KHÔNG chứa cụm
    # SHOT SCALE. Mood được append vào MỌI prompt mang mood đó, nên một cụm scale lọt vào
    # sẽ chọi với Phần 3 của những scene dùng shot khác (KAIZEN 2026-07-20).
    SCALE_TERMS = r"(extreme close-up|close-up|extreme wide|wide shot|medium shot|over-shoulder|low angle|high angle|macro|\d+mm)"
    for mood, kw in (config.get("mood_map") or {}).items():
        hit = sorted(set(re.findall(SCALE_TERMS, kw, re.I)))
        if hit:
            errs.append(
                f"mood_map[`{mood}`] chứa cụm shot scale: {', '.join(hit)} — mood chỉ được là "
                f"ánh sáng/màu/khung hình (Rule 2.2, 4.7). Cụm này sẽ chọi với shot type của mọi scene dùng mood đó."
            )

    # character-refs.md phải phủ đủ mọi asset
    ref = OUTPUT / "character-refs.md"
    if not ref.exists():
        errs.append("Chưa có output/character-refs.md — Bước 1 chưa sinh prompt ảnh tham chiếu asset.")
        return errs, warns
    txt = ref.read_text(encoding="utf-8")
    low = txt.lower()
    miss_char = [c["nano_name"] for c in chars
                 if (c.get("nano_name") or "").strip() and c["nano_name"].lower() not in low]
    miss_set = [s["id"] for s in setts
                if (s.get("id") or "").strip()
                and s["id"].lower() not in low and s["id"].upper() not in txt
                and (s.get("name", "").lower() not in low if s.get("name") else True)]
    if miss_char:
        errs.append(f"character-refs.md THIẾU ref cho {len(miss_char)} nhân vật: {miss_char}")
    if miss_set:
        errs.append(f"character-refs.md THIẾU ref cho {len(miss_set)} bối cảnh: {miss_set}")
    ok = total - len(miss_char) - len(miss_set)
    print(f"── COVERAGE character-refs.md: {ok}/{total} asset có prompt tham chiếu")
    return errs, warns


def gate_step2():
    """GATE bước 2 — kiểm tra scene-breakdown.md. Trả về (errors, warnings)."""
    errs, warns = [], []
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    char_ids = {c["id"] for c in config.get("characters", [])}
    moods = set(config.get("mood_map", {}).keys())
    _, scenes = load_scenes()
    srt_end = srt_total_seconds()

    # Rule 1.1c — description PHẢI có danh từ giới tính (chống ảnh ingredient sai giới tính)
    for c in config.get("characters", []):
        if not re.search(r"\b(man|woman|boy|girl|male|female)\b", c.get("description", ""), re.I):
            warns.append(f"Character `{c.get('id')}`: description thiếu danh từ giới tính (man/woman/boy/girl) — ảnh ingredient dễ bị vẽ sai giới tính (Rule 1.1c)")

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

    # KAIZEN 2026-07-22 — GRANULARITY: chống cắt scene quá thô (bug: 32 phút → ~30 scene,
    # có scene dài vài phút, gate cũ vẫn PASS). Max tuyệt đối của mọi beat = 25s (resolution)
    # → số scene tối thiểu = ceil(SRT / 25). Nhịp slideshow chuẩn 65+ là 10-14s/ảnh.
    abs_max = max(hi for _, hi in BEAT_BOUNDS.values())
    if srt_end:
        min_scenes = -(-srt_end // abs_max)  # ceil
        if len(scenes) < min_scenes:
            errs.append(
                f"GRANULARITY FAIL: chỉ {len(scenes)} scene cho video {srt_end}s ({srt_end/60:.0f} phút) — "
                f"tối thiểu {min_scenes} scene vì không scene nào được vượt {abs_max}s (rule 3.1). "
                f"Nhịp chuẩn 10-14s/ảnh → kỳ vọng ~{srt_end // 12} scene. Cắt lại chi tiết hơn."
            )

    prev = None
    streak, streak_beat = 0, None
    rest_run = 0  # rule 3.6 — số scene liên tiếp không có establishing/reflection
    for s in scenes:
        p = f"Scene {s['stt']}"
        dur = ts_to_sec(s["end"]) - ts_to_sec(s["start"])
        if dur <= 0:
            errs.append(f"{p}: Dur={dur}s — phải gộp vào scene liền kề")
        if prev and prev["end"] != s["start"]:
            errs.append(f"{p}: gap/overlap với scene trước (end {prev['end']} vs start {s['start']})")
        # Rule 4.8 — Visual Notes phải ghi shot type kèm ĐÚNG tên lens (KAIZEN 2026-07-21).
        # Bước 4 copy nguyên văn cụm shot từ đây, nên ký pháp sai ở 1 scene sẽ lan ra prompt.
        vn = s.get("visual_notes", "")
        if re.search(r"\b(shot|close-up)\b", vn, re.I) and not re.search(r"\blens\b", vn, re.I):
            errs.append(f"{p}: Visual Notes có shot type nhưng thiếu tên lens (rule 4.8) — dùng đúng bảng: "
                        f"24mm wide-angle lens / 35mm lens / 50mm lens / 85mm lens / 85mm portrait lens / 100mm macro lens")
        if s["beat_type"] not in BEAT_TYPES:
            errs.append(f"{p}: beat_type `{s['beat_type']}` không hợp lệ")
        else:
            lo, hi = BEAT_BOUNDS[s["beat_type"]]
            # KAIZEN 2026-07-22 — vượt max là LỖI CỨNG: model yếu từng cắt scene dài vài phút
            # mà gate chỉ cảnh báo nên vẫn PASS. Dưới min giữ mức cảnh báo (ít hại hơn).
            if dur > hi:
                errs.append(f"{p}: {s['beat_type']} {dur}s VƯỢT max {hi}s (rule 3.1) — PHẢI tách scene")
            elif 0 < dur < lo:
                warns.append(f"{p}: {s['beat_type']} {dur}s dưới min {lo}s (rule 3.1) — cân nhắc gộp vào scene liền kề")
        if s["mood"] not in moods:
            warns.append(f"{p}: mood `{s['mood']}` không có trong mood_map")
        for cid in s["characters"]:
            if cid not in char_ids:
                errs.append(f"{p}: character `{cid}` chưa define trong config")
        # KAIZEN 2026-07-22 — nhân vật chỉ hiện diện qua GIỌNG NÓI (điện thoại, lời kể) không được
        # liệt kê ở cột Characters: QC1 sẽ ép gọi nano_name vào prompt → model vẽ thêm người không
        # có trong khung. Chỉ liệt kê nhân vật NHÌN THẤY ĐƯỢC trong ảnh (Rule 4.6 visual state).
        if len(s["characters"]) > 1 and re.search(
                r"(qua|trên|bằng)\s+điện thoại|gọi điện|nhấc máy|đầu dây|on the phone", s.get("description", ""), re.I):
            warns.append(f"{p}: mô tả có cuộc gọi điện thoại nhưng liệt kê {len(s['characters'])} nhân vật — "
                         f"người ở đầu dây bên kia KHÔNG có trong khung, bỏ khỏi cột Characters (Rule 4.6)")
        # 4+ liên tiếp cùng beat
        if s["beat_type"] == streak_beat:
            streak += 1
            if streak == 4:
                warns.append(f"{p}: 4+ scene liên tiếp cùng beat `{streak_beat}` (rule 3.2)")
        else:
            streak, streak_beat = 1, s["beat_type"]
        # rule 3.3 — chuyển beat cấm trực tiếp
        if prev and (prev["beat_type"], s["beat_type"]) in FORBIDDEN_TRANS:
            warns.append(f"{p}: chuyển beat cấm `{prev['beat_type']}`→`{s['beat_type']}` — cần beat đệm ở giữa (rule 3.3)")
        # rule 3.6 — nghỉ mắt: mỗi 5-7 scene nên có 1 establishing/reflection
        if s["beat_type"] in REST_BEATS:
            rest_run = 0
        else:
            rest_run += 1
            if rest_run == 8:
                warns.append(f"{p}: 8+ scene liên tiếp không có establishing/reflection để nghỉ mắt cho khán giả 65+ (rule 3.6)")
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
    """GATE bước 3 (Sound Extraction) — output/sfx.json phủ đủ scene + hợp lệ.

    Điều kiện tiên quyết: Bước 2 (beat) phải xong — nếu scene-breakdown thiếu/FAIL,
    gate báo THIẾU BEAT và dừng (không kiểm sfx vì chưa có scene để soi).
    """
    errs, warns = [], []

    # 1. Beat phải có trước
    if not (OUTPUT / "scene-breakdown.md").exists() and not (OUTPUT / "scene-breakdown.json").exists():
        errs.append("THIẾU BEAT: chưa có output/scene-breakdown.md — chạy Bước 2 (--step2) trước khi tìm âm thanh.")
        return errs, warns
    beat_errs, _ = gate_step2()
    if beat_errs:
        errs.append(f"BEAT (Bước 2) chưa PASS ({len(beat_errs)} lỗi) — sửa xong Bước 2 rồi mới làm SFX. Chạy --step2 để xem chi tiết.")
        return errs, warns

    _, scenes = load_scenes()
    scene_stts = {s["stt"] for s in scenes}

    # 2. sfx.json phải tồn tại (Bước 3 đã chạy)
    f = OUTPUT / "sfx.json"
    if not f.exists():
        errs.append("Chưa có output/sfx.json — Bước 3 chưa chạy. (Video chủ ý không sfx: vẫn tạo file với keywords=[] cho mọi scene.)")
        return errs, warns
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        errs.append(f"output/sfx.json không phải JSON hợp lệ: {ex}")
        return errs, warns

    entries = data.get("sfx")
    if not isinstance(entries, list):
        errs.append("output/sfx.json thiếu mảng \"sfx\" (schema: {\"sfx\": [{\"stt\": .., \"keywords\": [..]}]})")
        return errs, warns

    seen = set()
    for e in entries:
        stt = e.get("stt")
        if stt not in scene_stts:
            errs.append(f"sfx entry stt {stt} không có scene tương ứng")
            continue
        if stt in seen:
            errs.append(f"sfx entry trùng stt {stt}")
        if not isinstance(e.get("keywords", []), list):
            errs.append(f"sfx stt {stt}: keywords phải là mảng (scene tĩnh không âm thanh = [])")
        seen.add(stt)

    missing = sorted(scene_stts - seen)
    if missing:
        errs.append(f"THIẾU sfx cho {len(missing)} scene: {missing[:15]}{'...' if len(missing) > 15 else ''} "
                    f"— mọi scene phải có entry (scene không âm thanh dùng keywords=[]).")

    # KAIZEN 2026-07-22 (sfx) — Rule 8.7: âm đánh chữ/gõ phím thuộc hiệu ứng typewriter
    # (đặt tại cue `at` trong typewriter-cues.md), CẤM nằm trong sfx — trừ khi trong CẢNH
    # thật sự có máy chữ/bàn phím (đọc description). Bug thực tế: video dựng ra toàn tiếng
    # gõ phím, vang cả ở đoạn không có chữ, lệch thời gian với chữ.
    TW_SFX = re.compile(r"typewriter|typing|keyboard|keystroke|key\s?clack", re.I)
    TW_DIEGETIC = re.compile(r"typewriter|keyboard|máy\s*(đánh\s*)?chữ|bàn phím|đánh máy|gõ phím", re.I)
    desc_by_stt = {s["stt"]: (s.get("description", "") + " " + s.get("visual_notes", "")) for s in scenes}
    kw_of = {}
    for e in entries:
        stt = e.get("stt")
        kws = e.get("keywords", [])
        if stt not in scene_stts or not isinstance(kws, list):
            continue
        kw_of[stt] = [str(k).strip().lower() for k in kws if str(k).strip()]
        for k in kw_of[stt]:
            if TW_SFX.search(k) and not TW_DIEGETIC.search(desc_by_stt.get(stt, "")):
                errs.append(f"sfx stt {stt}: `{k}` — âm đánh chữ/gõ phím KHÔNG được nằm trong sfx (Rule 8.7): "
                            f"âm này thuộc hiệu ứng typewriter, editor đặt tại `at` của cue trong typewriter-cues.md. "
                            f"Chỉ hợp lệ khi description scene có máy chữ/bàn phím thật.")

    # Rule 8.8 — đa dạng: 1 keyword phủ áp đảo toàn video = sfx đơn điệu
    n_nonempty = sum(1 for v in kw_of.values() if v)
    if n_nonempty >= 10:
        freq = {}
        for v in kw_of.values():
            for k in set(v):
                freq[k] = freq.get(k, 0) + 1
        top_k, top_c = max(freq.items(), key=lambda x: x[1])
        share = top_c / n_nonempty
        if share > 0.5:
            errs.append(f"SFX ĐƠN ĐIỆU: `{top_k}` xuất hiện ở {top_c}/{n_nonempty} scene có âm thanh ({share:.0%}) "
                        f"— gần như toàn video 1 loại âm. Đa dạng theo bối cảnh/mood (Rule 8.8).")
        elif share > 0.25:
            warns.append(f"SFX lặp nhiều: `{top_k}` ở {top_c}/{n_nonempty} scene ({share:.0%}) — cân nhắc đa dạng hơn (Rule 8.8)")
        prev_runs = {}
        for stt in sorted(kw_of):
            cur = {}
            for k in set(kw_of[stt]):
                cur[k] = prev_runs.get(k, 0) + 1
                if cur[k] == 4:
                    warns.append(f"sfx: `{k}` lặp 4+ scene liên tiếp (tới stt {stt}) — đổi chất liệu âm theo cảnh (Rule 8.8)")
            prev_runs = cur

    # KAIZEN 2026-07-22 (mật độ) — Rule 8.9: SFX là ĐIỂM NHẤN cảm xúc đặt đúng chỗ,
    # KHÔNG phải lớp phủ toàn video (bug: model tạo keyword cho 186/186 scene).
    if scene_stts:
        share = n_nonempty / len(scene_stts)
        if share > 0.75:
            errs.append(f"SFX FULL-COVERAGE: {n_nonempty}/{len(scene_stts)} scene có keyword ({share:.0%}) — "
                        f"sfx là điểm nhấn cảm xúc (~15-40% scene, Rule 8.9); scene không có sự kiện âm "
                        f"thật trong narration để keywords=[]. Chọn lọc lại, đừng rải thảm.")
        elif share > 0.5:
            warns.append(f"SFX dày: {n_nonempty}/{len(scene_stts)} scene có keyword ({share:.0%}) — "
                         f"kỳ vọng ~15-40% (Rule 8.9), cân nhắc bớt các scene chỉ có tiếng nền chung chung")
    return errs, warns


def gate_step4():
    """GATE bước 4 — kiểm tra prompts.md khớp scene-breakdown + rules 4.x."""
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
    # KAIZEN 2026-07-17 — mood keywords phải verbatim NGAY từ Bước 4 (không đợi --qc):
    # sub-agent batch hay bỏ dấu phẩy trong cụm mood (vd "firm posture clear focus"),
    # --step4 cũ chỉ kiểm style anchor nên lỗi lọt tới QC. Kiểm luôn ở đây.
    mood_map = config.get("mood_map", {})
    scene_mood = {s["stt"]: s.get("mood", "") for s in scenes}

    for stt in sorted(set(prompts) & scene_stts):
        text = prompts[stt]
        # KAIZEN 2026-07-09 — mệnh đề chống watermark trong style anchor không tính vào ngân sách từ
        n = len(text.replace("clean frame free of watermarks, logos, or AI icons", "").split())
        if n < 20 or n > 75:
            (errs if n < 15 or n > 90 else warns).append(f"Prompt {stt}: {n} từ (chuẩn 20-75, rule 4.4)")
        if style and style not in text:
            errs.append(f"Prompt {stt}: thiếu style anchor nguyên văn (rule 2.1)")
        if style and text.count(style) > 1:
            errs.append(f"Prompt {stt}: style anchor bị lặp {text.count(style)} lần")
        # Rule 2.2 / 4.1 Phần 4 — mood keywords verbatim (KAIZEN 2026-07-17)
        mk = mood_map.get(scene_mood.get(stt, ""), "")
        if mk and mk not in text:
            errs.append(f"Prompt {stt}: thiếu mood keywords nguyên văn cho mood `{scene_mood[stt]}` (rule 2.2/4.1)")
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
        # KAIZEN 2026-07-09 — cần mệnh đề chống icon AI do model tự vẽ.
        # KAIZEN 2026-07-11 (ĐÈ LÊN, cho prompt VIDEO): từ "watermarks" khiến bộ lọc Flow/Gemini
        # đọc thành yêu cầu GỠ watermark → CHẶN CỨNG prompt. Với video dùng `clean uncluttered frame`
        # (watermark Veo đóng sau render, prompt không gỡ được nên mệnh đề kia vô dụng mà rủi ro cao).
        low = text.lower()
        if "clean uncluttered frame" not in low and "free of watermarks" not in low:
            warns.append(f"{cid}: thiếu mệnh đề khung sạch (`clean uncluttered frame` — Rule 6.3, KAIZEN 2026-07-11)")
        elif "free of watermarks" in low:
            warns.append(f"{cid}: chứa `free of watermarks` — Flow/Gemini có thể CHẶN prompt video, đổi sang `clean uncluttered frame` (KAIZEN 2026-07-11)")
        # Rule 6.6 — subject persistence
        hits = sorted(set(re.findall(DISCONTINUITY_WORDS, text, re.I)))
        if hits:
            errs.append(f"{cid}: từ gây đứt gãy/subject vanishing: {', '.join(hits)} (Rule 6.6)")
        stt_n, clip_k = int(m.group(1)), m.group(2)
        for cid2 in scene_chars.get(stt_n, []):
            nn = nano.get(cid2, "")
            # Rule 6.2/6.6 — chỉ ép subject anchor ở clip .1 (dùng ảnh chính scene);
            # clip .k hard-cut được phép cắt sang insert vật thể/bối cảnh, không có nhân vật
            if nn and clip_k == "1" and nn.lower() not in text.lower():
                errs.append(f"{cid}: clip .1 thiếu subject anchor `{nn}` — phải neo nhân vật của scene (Rule 6.6)")
            # Rule 1.1a — nano_name dính liền sở hữu cách 's (áp mọi clip)
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

    # Rule 6.7 — 2 clip LIỀN KỀ (kể cả khác scene) không được cùng primary camera motion (chống hook phẳng)
    # (QC định tính 2026-07-11 bắt được 2.1/2.2 đều "push-in" mà similarity từ vựng vẫn thấp → lọt lưới sim-check)
    MOTION = re.compile(r"push[- ]?in|pull[- ]?back|tracking|static camera|camera holds|dolly|crane|handheld|locked[- ]?off|\bpan\b|\bzoom\b|\btilt\b|\bsway\b", re.I)
    seq = []
    for m in re.finditer(r"^## Clip (\d+)\.(\d+)\s*\n(.*?)(?=\n## Clip|\Z)", md, re.M | re.S):
        vp = re.search(r"\*\*Video Prompt:\*\*\s*\n(.*?)(?=\n---|\Z)", m.group(3), re.S)
        mo = MOTION.search(" ".join(vp.group(1).split())) if vp else None
        seq.append((f"{m.group(1)}.{m.group(2)}", mo.group(0).lower().replace(" ", "").replace("-", "") if mo else None))
    for i in range(1, len(seq)):
        if seq[i][1] and seq[i][1] == seq[i - 1][1]:
            warns.append(f"Clip {seq[i][0]} và {seq[i-1][0]} liền kề cùng camera motion `{seq[i][1]}` — mỗi cú cắt nên đổi chuyển động máy (Rule 6.7)")
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
    # Rule 4.8 — phân loại theo LENS (deterministic) + từ khóa góc máy.
    # KHÔNG dựa vào cụm scale (vd "extreme close-up") vì cụm đó cũng nằm trong
    # mood_map (shock) → mọi scene shock bị đếm nhầm là closeup; và "extreme wide
    # ESTABLISHING shot" không khớp "extreme wide shot" → trả None (KAIZEN 2026-07-08).
    if re.search(r"over[- ](?:the[- ])?shoulder|low angle|high angle", body):
        return "angle"
    if "24mm" in body or "35mm lens" in body:
        return "wide"
    if "100mm macro" in body or "85mm portrait" in body:
        return "closeup"
    if "85mm lens" in body or "50mm lens" in body:
        return "medium"
    # fallback khi prompt thiếu lens — dựa cụm scale
    for pat, cat in [(r"extreme close-up", "closeup"), (r"medium close-up", "medium"),
                     (r"extreme wide|wide shot|establishing shot", "wide"),
                     (r"medium shot", "medium"), (r"close-up", "closeup")]:
        if re.search(pat, body):
            return cat
    return None


def gate_qc():
    """BƯỚC 7 QC — tầng máy: mọi thứ đo đếm được. Ghi report ra output/qc-report.md."""
    errs, warns = [], []
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    style = config.get("style", "").strip()
    mood_map = config.get("mood_map", {})
    fb = config.get("flashback_style", "").strip()
    nano = {c["id"]: c.get("nano_name", "") for c in config.get("characters", [])}
    # QC3: config khai báo flashback_variants tường minh thì dùng nó; chỉ khi thiếu
    # mới fallback heuristic "_" (heuristic sai với variant tiến triển timeline, vd eli_9)
    if "flashback_variants" in config:
        variants = set(config.get("flashback_variants") or [])
    else:
        variants = {cid for cid in nano if "_" in cid}
    _, scenes = load_scenes()
    prompts = load_prompts()

    # chạy lại 3 gate nền (beat, sfx, prompt)
    e, w = gate_step2(); errs += [f"[step2] {x}" for x in e]; warns += [f"[step2] {x}" for x in w]
    e, w = gate_step3(); errs += [f"[step3-sfx] {x}" for x in e]; warns += [f"[step3-sfx] {x}" for x in w]
    e, w = gate_step4(); errs += [f"[step4] {x}" for x in e]; warns += [f"[step4] {x}" for x in w]

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
- [ ] SFX (Rule 8.7/8.8): trong các scene đã sample — keyword âm khớp bối cảnh VÀ hợp mood (tense=âm gọn sắc, sad=âm mềm thưa, calm=ambience mềm), đa dạng theo location; KHÔNG âm đánh chữ/gõ phím nào ngoài cue typewriter; scene có cue typewriter không bị ghi thêm âm gõ phím vào sfx
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
        sys.exit("LỖI: chưa có output/metadata.json — chạy Bước 5 (python3 scripts/export.py) trước.")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    entries = [f"{sc['stt']}. {sc['prompt']}" for sc in meta["scenes"]]
    out_file = OUTPUT / "prompts-list.txt"
    out_file.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    print(f"✓ Đã ghi {out_file.name} — {len(entries)} prompt.")
    sys.exit(0)


def export_refs_list():
    """Xuất 2 file từ output/character-refs.md (Bước 1):
    - character-refs-list.txt: prompt đánh số phẳng — copy-paste tạo ảnh ingredient hàng loạt.
    - character-refs-map.txt: `N -> TAG.jpg` — ảnh thứ N (theo đúng thứ tự list) đổi tên thành gì.
    THỨ TỰ list = đúng thứ tự asset xuất hiện trong character-refs.md — nhờ đó sau khi vẽ
    hàng loạt, chỉ cần đổi tên ảnh theo map là khớp asset tag khi upload Flow/Uni-X.
    Format nguồn (Rule 1.4): mỗi asset = heading `### TAG — ...` + prompt trong code block."""
    src = OUTPUT / "character-refs.md"
    if not src.exists():
        sys.exit("LỖI: chưa có output/character-refs.md — chạy Bước 1 trước.")
    md = src.read_text(encoding="utf-8")
    pat = re.compile(r"^###\s+([^\n]+?)\s*$\n+```[^\n]*\n(.*?)\n```", re.M | re.S)
    assets = []
    for m in pat.finditer(md):
        tag = m.group(1).split("—")[0].strip()
        prompt = " ".join(m.group(2).split())
        if prompt:
            assets.append((tag, prompt))
    if not assets:
        sys.exit("LỖI: không parse được asset nào từ character-refs.md — mỗi asset phải là heading "
                 "`### TAG — Tên` kèm prompt trong code block ``` ngay dưới (Rule 1.4).")

    lst = OUTPUT / "character-refs-list.txt"
    lst.write_text("\n\n".join(f"{i}. {p}" for i, (_, p) in enumerate(assets, 1)) + "\n", encoding="utf-8")
    mp = OUTPUT / "character-refs-map.txt"
    mp.write_text("\n".join(f"{i} -> {_tagify(t)}.jpg" for i, (t, _) in enumerate(assets, 1)) + "\n", encoding="utf-8")
    print(f"✓ Đã ghi {lst.name} — {len(assets)} prompt (thứ tự = thứ tự asset trong character-refs.md)")
    print(f"✓ Đã ghi {mp.name} — map đổi tên: ảnh thứ N → TAG.jpg")

    # đối chiếu số lượng với config — thiếu/thừa là dấu hiệu character-refs.md sai format hoặc sót asset
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))
    expect = len(config.get("characters", [])) + len(config.get("settings", []))
    if expect and len(assets) != expect:
        print(f"✗ Số prompt parse được ({len(assets)}) ≠ tổng asset trong config ({expect}) — "
              f"asset thiếu heading `###` hoặc thiếu code block; chạy `--step1` để soi asset nào thiếu ref.")
        sys.exit(1)
    sys.exit(0)


def _tag_by_text(text, config):
    """Gắn asset tag cho 1 prompt CHỈ dựa vào nội dung chữ (dùng cho ảnh phụ video hook —
    ảnh phụ không nằm trong metadata nên không có sẵn danh sách character id).
    Cùng quy ước với export_unix: nhân vật = nano_name, bối cảnh = cụm định danh đầu tiên
    của settings[].keywords, khớp KHÔNG phân biệt hoa-thường. Trả (tags, text đã chèn [TAG])."""
    tags = []
    for c in config.get("characters", []):
        nn = (c.get("nano_name") or "").strip()
        if not nn:
            continue
        m = re.search(r"\b" + re.escape(nn) + r"\b", text)
        if m:
            tag = _tagify(nn)
            tags.append(tag)
            text = text[:m.start()] + f"[{tag}]" + text[m.end():]
    for s in config.get("settings", []):
        probe = s["keywords"].split(", ")[0]
        m = re.search(re.escape(probe), text, re.IGNORECASE)
        if probe and m:
            tag = _tagify(s["id"])
            tags.append(tag)
            text = text[:m.start()] + f"[{tag}] " + text[m.start():]
            break  # 1 bối cảnh / ảnh
    return list(dict.fromkeys(tags)), text


def export_video_list():
    """Xuất output/video-prompts-list.txt từ output/video-prompts.md (Bước 4).

    Hai khối để chạy hàng loạt:
      A. IMAGE PROMPT của các ẢNH PHỤ `[stt]-[k].jpg` (clip .k hard-cut) — phải vẽ TRƯỚC.
         (ảnh chính của scene đã nằm trong prompts-list.txt/unix-batch, không lặp lại ở đây)
      B. VIDEO PROMPT đánh số theo thứ tự clip, kèm tên ảnh dùng làm frame đầu.
    """
    src = OUTPUT / "video-prompts.md"
    if not src.exists():
        sys.exit("LỖI: chưa có output/video-prompts.md — chạy Bước 4 (video hook) trước.")
    md = src.read_text(encoding="utf-8")
    clips = []
    for m in re.finditer(r"^## Clip (\d+)\.(\d+)\s*\n\*\*Scene:\*\*[^\n]*?\*\*Duration:\*\* (\d+)s[^\n]*\n(.*?)(?=\n## Clip|\Z)",
                         md, re.M | re.S):
        stt, k, dur, body = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        im = re.search(r"\*\*Image Prompt[^\n]*\n(.*?)(?=\n\*\*Video Prompt)", body, re.S)
        vp = re.search(r"\*\*Video Prompt:\*\*\s*\n(.*?)(?=\n---|\n## |\Z)", body, re.S)
        clips.append({"stt": stt, "k": k, "dur": dur,
                      "img": " ".join(im.group(1).split()) if im else None,
                      "vid": " ".join(vp.group(1).split()) if vp else None})
    if not clips:
        sys.exit("LỖI: không parse được clip nào từ video-prompts.md (sai format Rule 6.4).")

    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))

    # CHỈ video prompt. Asset gắn y như khi tạo ảnh: nhân vật/bối cảnh nào có ingredient và
    # được nhắc trong prompt thì gắn [TAG] tại chỗ + liệt kê ở dòng Assets (rỗng nếu không có).
    # Ảnh làm frame đầu ghi ở dòng `Frame:` (image prompt của ảnh phụ nằm trong video-prompts.md).
    lines = [f"# VIDEO PROMPT — HOOK — {len(clips)} clip, tổng {sum(c['dur'] for c in clips)}s",
             "# Chạy image-to-video: upload ảnh ở dòng `Frame:` rồi dán dòng `Prompt:`.",
             "# Assets = ingredient được nhắc trong prompt (quy ước tag giống unix-batch).", ""]
    n_tagged = 0
    for i, c in enumerate(clips, 1):
        frame = f"{c['stt']}.jpg" if c["k"] == 1 else f"{c['stt']}-{c['k']}.jpg"
        tags, text = _tag_by_text(c["vid"] or "", config)
        n_tagged += 1 if tags else 0
        lines += [f"(Video Prompt {i}/{len(clips)})",
                  f"Assets: {', '.join(tags)}",
                  f"Frame: {frame} | Clip {c['stt']}.{c['k']} | {c['dur']}s",
                  f"Prompt: {text or '(THIẾU video prompt)'}", ""]
    out = OUTPUT / "video-prompts-list.txt"
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"✓ Đã ghi {out.name} — {len(clips)} video prompt ({n_tagged} clip có asset tag)")
    sys.exit(0)


def export_sfx_timeline():
    """Xuất output/sfx-timeline.json — MODULE SFX ĐỘC LẬP: timestamp + keywords theo scene.

    Mục đích: chỉ cần chạy Bước 1→3 là cầm file này sang folder dựng video khác dùng ngay
    (kèm subtitle + voiceover — timestamp cùng timeline SRT nên tự khớp), KHÔNG cần
    prompts/metadata (Bước 4/5). Điều kiện: gate step3 (bao gồm beat PASS) sạch lỗi.
    """
    errs, warns = gate_step3()
    if warns:
        print(f"CẢNH BÁO ({len(warns)}):")
        for w in warns[:20]:
            print(f"  ⚠ {w}")
    if errs:
        print(f"LỖI ({len(errs)}):")
        for e in errs[:40]:
            print(f"  ✗ {e}")
        sys.exit("✗ FAIL — sửa Bước 2/3 cho PASS rồi chạy lại --sfx-export.")
    title, scenes = load_scenes()
    by_stt = {e.get("stt"): e.get("keywords", []) for e in (load_sfx() or {}).get("sfx", [])}
    rows = []
    for s in scenes:
        kws = [str(k).strip() for k in (by_stt.get(s["stt"]) or [])
               if str(k).strip() and str(k).strip() not in ("-", "—")]
        rows.append({
            "stt": s["stt"],
            "start": s["start"],
            "end": s["end"],
            "duration_s": ts_to_sec(s["end"]) - ts_to_sec(s["start"]),
            "mood": s.get("mood", ""),
            "description": s.get("description", ""),
            "keywords": kws,
        })
    out = {
        "project": title,
        "total_scenes": len(rows),
        "total_duration_s": ts_to_sec(scenes[-1]["end"]) if scenes else 0,
        "note": "Module SFX độc lập — timestamp cùng timeline với SRT/voiceover nên tự khớp. "
                "Chỉ âm diegetic theo phân cảnh (Rule 8.2); KHÔNG gồm nhạc nền và KHÔNG gồm âm đánh chữ "
                "(âm đánh chữ thuộc typewriter-cues, Rule 8.7). keywords=[] = scene chủ ý im lặng, không phải thiếu.",
        "scenes": rows,
    }
    f = OUTPUT / "sfx-timeline.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_kw = sum(1 for r in rows if r["keywords"])
    print(f"✓ Đã ghi {f.name} — {len(rows)} scene ({n_kw} có keyword, {len(rows) - n_kw} im lặng), "
          f"timeline 00:00:00 → {rows[-1]['end'] if rows else '—'}")
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
        sys.exit("LỖI: chưa có output/metadata.json — chạy Bước 5 (python3 scripts/export.py) trước.")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    config = json.loads((INPUT / "config.json").read_text(encoding="utf-8"))

    char_tag = {c["id"]: _tagify(c["nano_name"]) for c in config.get("characters", []) if c.get("nano_name")}
    char_name = {c["id"]: c["nano_name"] for c in config.get("characters", [])}
    settings = config.get("settings", [])
    setting_tag = {s["id"]: _tagify(s["id"]) for s in settings}

    def find_setting_id(prompt_text):
        # khớp không phân biệt hoa-thường: prompt hay mở đầu Part 2 bằng cụm định danh
        # viết hoa (vd "Long wall...") → case-sensitive sẽ trượt tag (KAIZEN 2026-07-07)
        low = prompt_text.lower()
        for s in settings:
            probe = s["keywords"].split(", ")[0]
            if probe and probe.lower() in low:
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
            m = re.search(re.escape(probe), text, re.IGNORECASE)
            if m:
                text = text[:m.start()] + f"[{tag}] " + text[m.start():]
        else:
            unmatched.append(sc["stt"])
        rows.append((sc["stt"], list(dict.fromkeys(tags)), text))

    total = len(rows)  # đánh số LIÊN TỤC toàn cục + mẫu số là TỔNG THỰC (vd 101/170 ở file 2)
    n_batches = (total + UNIX_BATCH_SIZE - 1) // UNIX_BATCH_SIZE
    written = []
    for b in range(n_batches):
        chunk = rows[b * UNIX_BATCH_SIZE:(b + 1) * UNIX_BATCH_SIZE]
        out_file = OUTPUT / f"unix-batch-{b + 1:02d}.txt"
        n = len(chunk)
        body = []
        for j, (stt, tags, text) in enumerate(chunk):
            gidx = b * UNIX_BATCH_SIZE + j + 1
            body.append(f"(Image Prompt {gidx}/{total})")
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
    if "--refs-list" in sys.argv:
        export_refs_list()
    if "--sfx-export" in sys.argv:
        export_sfx_timeline()
    if "--video-list" in sys.argv:
        export_video_list()
    if "--prompts-list" in sys.argv:
        export_prompts_list()
    if "--unix-export" in sys.argv:
        export_unix()
    if "--step1" in sys.argv:
        run_gate("BƯỚC 1 (đếm asset + character-refs)", gate_step1)
    if "--step2" in sys.argv:
        run_gate("BƯỚC 2 (scene-breakdown)", gate_step2)
    if "--step3" in sys.argv:
        run_gate("BƯỚC 3 (sfx — âm thanh)", gate_step3)
    if "--step4" in sys.argv:
        run_gate("BƯỚC 4 (prompts)", gate_step4)
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
                "sfx": [],  # điền từ output/sfx.json (Bước 3) qua merge_sfx bên dưới
            })

        # SFX (Bước 3, tùy chọn) — merge từ output/sfx.json vào scene khớp stt
        sfx = load_sfx()
        sfx_errs, sfx_warns, sfx_n = ([], [], 0)
        if sfx:
            sfx_errs, sfx_warns, sfx_n = merge_sfx(sfx, meta_scenes)
        else:
            print("ⓘ LƯU Ý: không có output/sfx.json → metadata KHÔNG có hiệu ứng âm thanh (field sfx rỗng).")
            print("  Chạy Bước 3 (Sound Extraction) để sinh output/sfx.json rồi export lại. Nếu video này chủ ý bỏ sfx thì bỏ qua.")

        # Typewriter cues (tùy chọn) — merge từ input/typewriter.json vào scene khớp
        tw = load_typewriter()
        tw_errs, tw_warns, tw_n = ([], [], 0)
        if tw:
            tw_errs, tw_warns, tw_n = merge_typewriter(tw, meta_scenes)
        else:
            print("ⓘ LƯU Ý: không có input/typewriter.json → metadata KHÔNG có hiệu ứng đánh máy (typewriter overlay).")
            print("  Video kể chuyện cho khán giả 65+ thường cần chữ lớn gõ chậm ở các mốc kịch tính: con số (giá tiền, số lượng),")
            print("  time card ('2 năm sau'), câu thesis/moral. Nếu muốn: tạo input/typewriter.json (schema ở .claude/rules/metadata.md 5.7)")
            print("  rồi chạy lại `python3 scripts/export.py`. Nếu chủ ý KHÔNG dùng typewriter cho video này thì bỏ qua ghi chú này.")

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
        if sfx:
            errs += sfx_errs
            warns += sfx_warns
        if tw:
            errs += tw_errs
            warns += tw_warns

    if not validate_only:
        out_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if sfx and not sfx_errs:
            print(f"✓ SFX: merge keyword âm thanh vào {sfx_n} scene từ output/sfx.json")
        if tw and not tw_errs:
            cues_file = write_typewriter_cues(tw, meta_scenes)
            print(f"✓ Typewriter: merge {tw_n} cue vào metadata + đã ghi {cues_file.name}")

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
