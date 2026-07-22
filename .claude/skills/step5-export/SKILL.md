---
name: step5-export
description: Bước 5 — Export. Chạy scripts/export.py sinh output/metadata.json (merge sfx + typewriter), sửa file NGUỒN khi có lỗi. Dùng khi user nói "chạy bước 5", "export", "xuất metadata". Cần Bước 3 + 4 PASS trước.
---

# Bước 5 — Export metadata.json (SCRIPT làm — AI KHÔNG viết metadata tay)

## Nhiệm vụ DUY NHẤT
Chạy `python3 scripts/export.py` → script parse scene-breakdown + prompts + config + sfx.json (+ typewriter.json nếu có) → sinh + validate `output/metadata.json`. Vai trò của AI: đọc lỗi script báo → **sửa file NGUỒN** → chạy lại. TUYỆT ĐỐI KHÔNG sửa trực tiếp `metadata.json` / `typewriter-cues.md` (file sinh ra).

## Pre-flight
1. `--step2`, `--step3`, `--step4` đều PASS (chạy nhanh 3 gate nếu chưa chắc).

## LOOP ENGINE
1. Chạy `python3 scripts/export.py`.
2. Script báo LỖI → xác định file nguồn tương ứng (`scene-breakdown.md` / `prompts.md` / `sfx.json` / `typewriter.json` / `config.json`) → sửa đúng chỗ → chạy lại. Lặp đến PASS.
3. Script in **LƯU Ý thiếu `input/typewriter.json`** → KHÔNG im lặng đi tiếp: sau khi PASS, chủ động ĐỀ XUẤT bộ cue cho user duyệt (rút từ SRT: con số kịch tính, time card, câu thesis/moral; THƯA ~6–14 cue/video dài; khán giả 65+ cần chữ lớn, gõ chậm, giữ dòng 1–2s) → user duyệt → tạo `input/typewriter.json` → chạy lại export. TRỪ KHI user đã nói video này không dùng typewriter.
   - Suy `stt` cho cue bằng cách tìm scene chứa timestamp trong metadata — KHÔNG đoán.
   - Cue `at` NGOÀI khoảng scene = LỖI cứng (chữ sẽ hiện đè scene khác); script tự tính `type_s` (thời lượng gõ theo độ dài text) và cảnh báo nếu chữ chưa gõ xong đã hết scene → sửa `at`/text trong file nguồn.
   - `typewriter-cues.md` sinh ra kèm khối "QUY TẮC ÂM THANH ĐÁNH CHỮ" cho editor (âm gõ CHỈ tại `at`, dừng sau `type_s`; scene không cue = không âm đánh chữ; âm đánh chữ không lấy từ sfx) — KHÔNG xóa/sửa khối này.
4. Sau 5 vòng cùng 1 lỗi không giảm → DỪNG, báo user.

## Sau khi PASS
Review nhanh checklist định tính (không đọc cả file — dùng số liệu script in ra): beat distribution hợp lý, tổng duration khớp SRT, số cue typewriter merge đủ.

## Kết quả trả về
- Dòng EXPORT/PASS của script; beat distribution; số scene có sfx; số cue typewriter. Bước tiếp: `step6-unix` rồi `step7-qc`.

## Tham khảo
`.claude/rules/metadata.md` (5.1→5.8).
