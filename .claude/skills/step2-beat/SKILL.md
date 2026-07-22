---
name: step2-beat
description: Bước 2 — Beat Analysis. Cắt input/subtitle.srt thành bảng phân cảnh output/scene-breakdown.md theo nhịp dựng. Dùng khi user nói "chạy bước 2", "phân tích nhịp dựng", "cắt scene". Cần Bước 1 xong trước (config.json đã chốt).
---

# Bước 2 — Beat Analysis (cắt scene)

## Nhiệm vụ DUY NHẤT
Đọc `input/subtitle.srt` + `input/config.json` → cắt thành scene → ghi bảng `output/scene-breakdown.md`. KHÔNG viết prompt (Bước 4), KHÔNG trích SFX (Bước 3), KHÔNG sửa config (thiếu nhân vật/địa điểm trong config → DỪNG, hỏi user, quay lại Bước 1).

## Pre-flight (thiếu → DỪNG, báo user)
1. `input/subtitle.srt` tồn tại.
2. `input/config.json` đã chốt — `python3 scripts/export.py --step1` PASS. (Chế độ SFX-only: chỉ cần config.json hợp lệ user đã chốt — không cần character-refs/`--step1` PASS.)

## MỤC TIÊU SỐ — BẮT BUỘC tính và IN RA trước khi cắt bất kỳ scene nào
Đây là neo chống cắt sai độ hạt (KAIZEN 2026-07-22: model cắt video 32 phút thành ~30 scene, có scene dài vài phút):

1. T = giây kết thúc của entry SRT cuối cùng (đọc bằng lệnh, ví dụ `tail`/`grep` — không ước lượng).
2. In ra 3 con số:
   - **Số scene TỐI THIỂU** = ⌈T / 25⌉ (25s = max dài nhất của mọi beat type — Rule 3.1)
   - **Số scene KỲ VỌNG** ≈ T / 12 (nhịp slideshow 10–14s/ảnh cho khán giả 65+)
   - **Tổng thời lượng T** (để đối chiếu coverage)
3. Ví dụ: video 32 phút (1920s) → tối thiểu 77 scene, kỳ vọng ~160 scene. Nếu ước tính của bạn thấp hơn mức tối thiểu → bạn đang cắt sai — cắt nhỏ hơn ngay từ đầu, đừng đợi gate FAIL.

## Ràng buộc CỨNG (gate `--step2` chặn LỖI — không thương lượng)

| Beat Type | Min (s) | Max (s) | Default | Dùng cho |
|---|---|---|---|---|
| establishing | 10 | 18 | 13 | giới thiệu bối cảnh mới, wide |
| dialogue | 6 | 12 | 9 | hội thoại, medium/over-shoulder |
| emotional_peak | 10 | 18 | 13 | cảm xúc mạnh, close-up |
| tension | 5 | 10 | 7 | xung đột, tin xấu, nhịp nhanh |
| reflection | 10 | 18 | 14 | nội tâm, hồi tưởng |
| resolution | 12 | 25 | 18 | kết, bài học, giữ lâu |

- Scene VƯỢT max của beat type = LỖI CỨNG → tách. Dur=0 = LỖI → gộp vào scene liền kề. Dưới min = cảnh báo → cân nhắc gộp.
- Tổng số scene < ⌈T/25⌉ = LỖI CỨNG (GRANULARITY FAIL).
- Scene 1 bắt đầu `00:00:00`; `end` scene N = `start` scene N+1 (không gap/overlap); bảng phủ đến HẾT SRT.
- Cắt tại ranh giới câu hoàn chỉnh trong SRT (Rule 3.4) — không cắt giữa câu.
- `Characters` chỉ dùng ID có trong config; `Mood` chỉ dùng key có trong `mood_map`.
- Visual Notes: shot type PHẢI kèm ĐÚNG tên lens (LỖI cứng nếu thiếu chữ `lens`): `extreme wide shot, 24mm wide-angle lens` / `wide shot, 35mm lens` / `medium shot, 50mm lens` / `medium close-up, 85mm lens` / `close-up, 85mm portrait lens` / `extreme close-up, 100mm macro lens` / over-shoulder–low–high angle + lens tương ứng.
- KHÔNG dùng ký tự `|` trong cell Description/Visual Notes (vỡ bảng markdown).

## Thuật toán (segment — BẮT BUỘC với video >20 phút, khuyến nghị mọi video)
1. Chia SRT thành segment ~10 phút.
2. Với TỪNG segment: đọc segment → cắt scene theo tiêu chí Rule 3.5 (đổi location / thời gian / nhân vật focus / mood / lượt thoại / vượt max duration) → gán beat_type + mood + characters + Description + Visual Notes (shot + lens, chủ động đặt ≥2 close-up THẬT + ≥1 angle mỗi 10 scene — `medium close-up` KHÔNG đếm là closeup) → **append ngay các dòng vào bảng trong file** → mới đọc segment tiếp theo. KHÔNG giữ toàn bộ bảng trong đầu viết 1 lần.
3. Cấu trúc kể chuyện: scene REPLAY khoảnh khắc cold-open → ghi `(replay scene N)` vào Visual Notes; mỗi 5–7 scene có ≥1 establishing/reflection; không 4+ scene liên tiếp cùng beat; tránh transition cấm (`tension→resolution`, `establishing→emotional_peak`, `resolution→tension`).
4. Xong segment cuối: đếm số dòng bằng lệnh (`grep -c`), so với MỤC TIÊU SỐ; viết mục `## Beat Distribution`.
5. Mood không rõ → chọn mood trung tính gần nhất trong mood_map, không bịa mood kịch tính. Hai cách cắt đều hợp lý và lệch nhau nhiều → nêu lựa chọn còn lại khi báo kết quả.

## Format output
```markdown
# Scene Breakdown: [Title]
Total scenes: [N] | Total duration: [HH:MM:SS]

| STT | Start | End | Dur(s) | Beat Type | Mood | Characters | Description | Visual Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | 00:00:00 | 00:00:12 | 12 | establishing | calm | marin | ... | wide shot, 35mm lens |

## Beat Distribution
- establishing: X (Y%) ...
```

## LOOP ENGINE (lặp đến khi máy xác nhận — KHÔNG tự tuyên bố xong)
1. Chạy `python3 scripts/export.py --step2`.
2. `✗ FAIL` → đọc TỪNG dòng lỗi → sửa đúng block scene liên quan (Edit theo đoạn — KHÔNG Write lại cả file) → chạy lại gate.
3. `✓ PASS` còn cảnh báo → xử lý từng cảnh báo: sửa, hoặc ghi lý do chấp nhận vào mục `## QC Notes` cuối file.
4. `✓ PASS` sạch (cảnh báo còn lại đã có lý do) → Bước 2 XONG.
5. Sau 5 vòng cùng 1 lỗi không giảm → DỪNG, báo user kèm danh sách lỗi. CẤM: nới check trong `export.py`, xóa bớt đoạn SRT, ghi số Dur không khớp timestamp để "cho khớp".

## Kết quả trả về
- Số scene thực / mục tiêu số; coverage (end cuối vs T); beat distribution; dòng PASS của gate.
- Bước tiếp: `step3-sound`. Video dài → khuyên user mở phiên mới.

## Tham khảo
`.claude/rules/beat-analysis.md` (Rule 3.1→3.6 đầy đủ). Nguyên tắc hành vi: CLAUDE.md.
