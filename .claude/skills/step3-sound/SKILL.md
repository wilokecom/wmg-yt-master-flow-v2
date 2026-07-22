---
name: step3-sound
description: Bước 3 — Sound Extraction. Đọc output/scene-breakdown.md, suy keyword âm thanh diegetic cho từng scene, ghi output/sfx.json + xuất module độc lập output/sfx-timeline.json (timestamp + keywords, dùng được ở folder dựng video khác chỉ với subtitle + voiceover). Dùng khi user nói "chạy bước 3", "tìm âm thanh", "trích sfx", hoặc chỉ cần SFX cho một kịch bản. Cần Bước 2 PASS trước.
---

# Bước 3 — Sound Extraction (trích keyword SFX)

## Nhiệm vụ DUY NHẤT
Đọc từng scene trong `output/scene-breakdown.md` → suy ra keyword âm thanh **diegetic có thật trong cảnh** → ghi `output/sfx.json`. KHÔNG sửa scene-breakdown, KHÔNG viết prompt, KHÔNG phân tích waveform (đây là suy luận từ description, không phải xử lý audio).

## Pre-flight (thiếu → DỪNG, báo "THIẾU BEAT: chạy Bước 2 trước")
1. `output/scene-breakdown.md` tồn tại.
2. `python3 scripts/export.py --step2` PASS (số scene/stt còn đổi thì SFX sẽ lệch).

## MỤC TIÊU SỐ — BẮT BUỘC tính và IN RA trước khi viết keyword nào
SFX là **ĐIỂM NHẤN cảm xúc đặt đúng chỗ**, KHÔNG phải lớp phủ toàn video (KAIZEN 2026-07-22: model tạo keyword cho 186/186 scene — sai mục đích; video có narration + nhạc nền phủ suốt, sfx chỉ chấm phá):

1. N = tổng số scene (đếm bằng lệnh trên scene-breakdown).
2. In ra: **số scene có keyword kỳ vọng ≈ 15–40% × N** (vd 186 scene → 30–75 điểm nhấn, ~1-2 điểm nhấn/phút).
3. Nếu bạn thấy mình đang viết keyword cho mọi scene liên tiếp → đang rải thảm, dừng lại chọn lọc. Gate chặn LỖI khi >75% scene có keyword, cảnh báo khi >50%.

## Ràng buộc CỨNG
- **Phủ đủ MỌI scene**: mỗi stt trong scene-breakdown có đúng 1 entry; scene không phải điểm nhấn → `"keywords": []` tường minh. **Đa số entry là `[]` là dấu hiệu làm ĐÚNG.** Gate chặn thiếu/trùng/stt lạ.
- **Tiêu chí CHỌN scene điểm nhấn** (Rule 8.9, thỏa ≥1): (1) narration/description có sự kiện âm cụ thể — đặc biệt khi narration TỰ nhắc âm thanh (búa gõ, cổng mở, chuông, mưa, đàn thú, điện thoại, phong bì xé); (2) khoảnh khắc cảm xúc cần nhấn (emotional_peak, mở hook, chuyển hồi); (3) motif âm lặp của truyện (giữ trọn chuỗi để editor dùng cùng 1 file âm).
- **Chỉ diegetic**: âm thanh thực sự phát ra trong khung cảnh. CẤM nhạc nền/score/cảm xúc (`tense music`, `sad piano`). CẤM bịa âm thanh không có căn cứ trong description. Room tone CHỈ khi cảnh cần nền đặc trưng khác biệt (phiên tòa, hầm nhà thờ đông người) — KHÔNG phải mặc định cho scene tĩnh.
- **CẤM âm đánh chữ/gõ phím** (`typewriter/typing/keyboard/keystroke` — Rule 8.7, gate chặn LỖI): âm gõ phím thuộc hiệu ứng typewriter overlay (editor đặt tại `at` của cue trong typewriter-cues.md), KHÔNG phải sfx của cảnh — kể cả scene có cue typewriter. Ngoại lệ duy nhất: description scene có máy đánh chữ/bàn phím thật đang được gõ.
- **Đa dạng** (Rule 8.8, gate đo): không để 1 keyword phủ >25% scene có âm (>50% = LỖI), không lặp 1 keyword 4+ scene liên tiếp; room tone đổi theo location (`farm store room tone` ≠ `quiet kitchen room tone`).
- **Hợp mood** (Rule 8.8): mood quyết định CHỌN âm nào trong cảnh — tense/shock: âm gọn sắc đơn lẻ (heavy door slam); sad/nostalgic: âm mềm thưa xa (distant wind, slow clock ticking); calm/hopeful: ambience mềm (morning birdsong); determined: âm lao động chắc nhịp (mallet striking stake). Vẫn phải diegetic — không bịa âm "cho hợp mood".
- Scene tĩnh trong phòng → room tone (`office room tone`, `quiet room ambience`, `courtroom murmur`).
- Keyword "tìm được trên thư viện sfx": cụm danh từ + hành động cụ thể, tiếng Anh viết thường, 1–3 cụm/scene (`rotary phone dialing` ✅, `phone sound` ❌; `heavy wooden door slam` hơn `door`).

## Thuật toán (2 lượt — chọn trước, viết sau)
1. **Lượt 1 — CHỌN điểm nhấn**: đọc bảng scene-breakdown theo đoạn (block 50–80 scene), đánh dấu các scene thỏa tiêu chí Rule 8.9 (sự kiện âm cụ thể / đỉnh cảm xúc / motif). Đếm lại: nằm trong khoảng 15–40% chưa? Vượt → cắt bớt những scene chỉ có tiếng nền chung chung.
2. **Lượt 2 — VIẾT keyword**: chỉ cho các scene đã chọn, 1–3 cụm/scene theo Rule 8.3 + bảng mood 8.8. Mọi scene còn lại → `[]`.
3. Ghi `output/sfx.json` đúng schema:
```json
{ "sfx": [ { "stt": 1, "keywords": ["rotary phone dialing", "phone cord stretch"] }, { "stt": 2, "keywords": [] } ] }
```

## LOOP ENGINE (lặp đến khi máy xác nhận — KHÔNG tự tuyên bố xong)
1. Chạy `python3 scripts/export.py --step3`.
2. `✗ FAIL` → đọc từng dòng lỗi → sửa đúng entry trong `sfx.json` → chạy lại gate.
3. `✓ PASS` → chạy tiếp `python3 scripts/export.py --sfx-export` (bước 4 dưới) → Bước 3 XONG.
4. Sau 5 vòng cùng 1 lỗi không giảm → DỪNG, báo user. CẤM sửa tay `metadata.json` (Bước 5 tự merge sfx theo stt).

## Xuất module SFX độc lập (BẮT BUỘC sau khi gate PASS)
```bash
python3 scripts/export.py --sfx-export
```
Sinh `output/sfx-timeline.json` — file TỰ ĐỦ: mỗi scene có `start/end/duration_s/mood/description/keywords`, timestamp cùng timeline SRT/voiceover nên mang sang folder dựng video khác là khớp ngay, KHÔNG cần prompts/metadata (Bước 4/5).
- **Chế độ SFX-only**: user chỉ cần SFX cho 1 kịch bản → chạy Bước 1 (config, bỏ qua character-refs) → Bước 2 → Bước 3 → cầm `sfx-timeline.json` đi dùng. Pipeline ảnh không bị ảnh hưởng: Bước 5 vẫn merge từ `sfx.json` như cũ.
- Sửa âm thanh → sửa `output/sfx.json` → chạy lại `--sfx-export` (và Bước 5 nếu project có pipeline ảnh).

## Kết quả trả về
- Số scene có keyword / số scene `[]` / tổng; dòng PASS của gate; đường dẫn `output/sfx-timeline.json` + timeline phủ (0 → HH:MM:SS). Bước tiếp (nếu làm full pipeline): `step4-prompts`.

## Tham khảo
`.claude/rules/sound.md` (Rule 8.1→8.6).
