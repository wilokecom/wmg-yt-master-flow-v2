---
name: step4-prompts
description: Bước 4 — Prompt Generation. Compose prompt ảnh 5 phần cho từng scene từ scene-breakdown + config → output/prompts.md (+ output/video-prompts.md nếu video_hook bật). Dùng khi user nói "chạy bước 4", "tạo prompt", "generate prompt". Cần Bước 2 PASS trước.
---

# Bước 4 — Prompt Generation

## Nhiệm vụ DUY NHẤT
Duyệt từng scene trong `output/scene-breakdown.md` + `input/config.json` → compose prompt ảnh → `output/prompts.md`. Nếu `video_hook.enabled` → sinh thêm `output/video-prompts.md`. KHÔNG sửa scene-breakdown/config (thấy lỗi nguồn → DỪNG, báo user quay lại bước tương ứng).

## Pre-flight (thiếu → DỪNG, báo user)
1. `python3 scripts/export.py --step2` PASS.
2. `input/config.json` có style + mood_map + characters + settings đầy đủ.

## MỤC TIÊU SỐ — tính trước khi viết
- Tổng prompt = đúng tổng số scene (đếm bằng `grep -c` trên scene-breakdown) — không thiếu, không thừa. In con số này ra trước khi bắt đầu.

## Template 5 phần (BẮT BUỘC, cách nhau dấu phẩy, không xuống dòng)
```
[1. Characters + action], [2. Setting], [3. Shot type + lens], [4. Mood keywords], [5. Style anchor]
```
1. **Characters + action**: gọi đúng `nano_name`; CẤM sở hữu cách dính liền (`Dalton's` → diễn đạt lại `Dalton, blank and puzzled,`); action lấy từ Description; ≤3 nhân vật/prompt.
2. **Setting**: scene ở location đã define → prompt PHẢI chứa NGUYÊN VĂN cụm ĐẦU của `settings[].keywords` (Bước 6 dò tag bằng cụm này — rút gọn là mất tag). Ngoại lệ: extreme close-up vật thể / không gian phụ 1 lần.
3. **Shot type + lens**: COPY NGUYÊN VĂN cụm shot từ Visual Notes của scene (đã kèm lens đúng bảng Rule 4.8). Close-up/medium close-up có mặt người → thêm `full head within frame`.
4. **Mood keywords**: tra `mood_map[mood của scene]` → copy NGUYÊN VĂN **kể cả dấu phẩy nội bộ** (bỏ 1 phẩy = gate FAIL).
5. **Style anchor**: copy nguyên văn `config.style`, đúng 1 lần, không rút gọn. Scene flashback (characters chứa ID trong `flashback_variants`) → append thêm `flashback_style`.

## Ràng buộc CỨNG (gate `--step4` chặn)
- Đủ prompt cho mọi scene; 20–75 từ (mệnh đề chống watermark không tính); style + mood verbatim.
- CẤM trong prompt: chữ/text hiển thị trong ảnh; từ hàm ý cốt truyện (`secret/hidden/mysterious/memories...` → dịch thành trạng thái thị giác: `closed/locked/dimly lit/faded photograph`); từ phủ định (`no/not/without/never` — positive framing: `empty street` thay vì `no cars`); từ âm thanh; từ trong `era.forbidden`.
- Prompt không mâu thuẫn Description (trang phục/vật thể/thời tiết); scene `(replay scene N)` → dùng ĐÚNG setting của scene N.
- Shot distribution mỗi **thập kỷ tuyệt đối theo STT** (1-10, 11-20...): ≥2 wide (`24mm`/`35mm lens`), ≥3 medium (`50mm`/`85mm lens` — medium close-up đếm là MEDIUM), ≥2 closeup THẬT (`85mm portrait`/`100mm macro`), ≥1 angle (over-shoulder/low/high).

## Thuật toán batch (chống tràn context)
- ≤40 scene: viết tuần tự, append từng cụm.
- 41–80 scene: batch 25–30 scene — đọc đúng đoạn scene-breakdown tương ứng → viết → **append ngay vào prompts.md** → batch tiếp.
- >80 scene: **sub-agent song song**, batch chia theo BỘI SỐ 10 (1-30, 31-60...), mỗi sub-agent ghi `output/prompts-batch-N.md`, phiên chính nối bằng `cat` (không đọc nội dung vào context). Spec giao sub-agent PHẢI ghi rõ:
  1. Cửa sổ shot distribution là **thập kỷ tuyệt đối theo STT toàn cục**, không phải 10 scene đầu batch.
  2. Nhóm shot quyết định bởi TOKEN LENS (closeup ⟺ `85mm portrait`/`100mm macro`; medium close-up = MEDIUM).
  3. Mood keywords copy nguyên văn KỂ CẢ dấu phẩy.
  4. Style anchor nguyên văn; nano_name không dính `'s`; cụm định danh setting nguyên văn.
- Sau khi gộp batch: phiên chính kiểm lại ràng buộc TOÀN CỤC (distribution, đủ prompt) bằng gate — không tin self-check của batch.

## Video Hook (chỉ khi `video_hook.enabled = true`)
Sinh `output/video-prompts.md` theo Rule 6.1→6.7 (`.claude/rules/video-prompt.md`). Tóm tắt cứng:
- Hook = các scene có `start` < `duration_s` (mặc định 60s). Mỗi clip ≤ `max_clip_s` (8s), phủ liên tục.
- **Mỗi clip = 1 CÚ CẮT sang cảnh khác** (hard cut, ảnh riêng): clip `.1` = copy NGUYÊN VĂN image prompt của scene; clip `.k` = ảnh phụ `[stt]-[k].jpg` với image prompt 5 phần riêng (reaction/insert/đảo scale). CẤM Extend tua chậm cùng khung.
- Video prompt: camera motion + 1 chuyển động tiến triển, neo subject bằng nano_name + đặc điểm, KHÔNG dialogue trong ngoặc kép, KHÔNG từ đứt gãy (`suddenly/appears/disappears/reveals/transforms...`), kết `Audio: [ambient nhẹ]`. Dùng `clean uncluttered frame` — CẤM `free of watermarks` trong prompt video (Flow chặn).
- 2 clip liền kề: khác hình VÀ khác camera motion. Chuỗi clip leo thang như trailer.

## LOOP ENGINE (lặp đến khi máy xác nhận — KHÔNG tự tuyên bố xong)
1. Chạy `python3 scripts/export.py --step4`.
2. `✗ FAIL` → đọc TỪNG dòng lỗi → sửa đúng block prompt liên quan (Edit theo đoạn) → chạy lại gate.
3. `✓ PASS` còn cảnh báo → xử lý từng cảnh báo hoặc ghi lý do chấp nhận.
4. `✓ PASS` sạch → Bước 4 XONG.
5. Sau 5 vòng cùng 1 lỗi không giảm → DỪNG, báo user. CẤM sửa scene-breakdown/config để "né" lỗi prompt mà không báo user.

## Kết quả trả về
- Tổng prompt / tổng scene; số clip hook (nếu có); dòng PASS của gate. Bước tiếp: `step5-export`.

## Tham khảo
`.claude/rules/prompt-structure.md` (4.1→4.8), `.claude/rules/character.md` (1.1a-c), `.claude/rules/video-prompt.md` (6.x).
