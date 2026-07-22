---
name: step1-setup
description: Bước 1 — Project Setup. Tạo input/config.json từ subtitle.srt (nhân vật, bối cảnh, style, mood_map) + sinh prompt ảnh tham chiếu asset (output/character-refs.md). Dùng khi user nói "chạy bước 1", "setup project", "tạo config".
---

# Bước 1 — Project Setup

## Nhiệm vụ DUY NHẤT
Parse `input/subtitle.srt` → tạo `input/config.json` cho user review + sinh `output/character-refs.md` (prompt ảnh ingredient cho MỌI asset). KHÔNG cắt scene (Bước 2), KHÔNG viết prompt scene (Bước 4).

**Chế độ SFX-only** (user nói chỉ cần SFX cho kịch bản này): vẫn tạo + chốt `config.json` (Bước 2 cần characters/settings/mood_map để cắt scene), nhưng BỎ QUA sinh `character-refs.md` và gate `--step1` — không ai vẽ ảnh nên ref là việc thừa. Xong config → sang thẳng Bước 2.

## Pre-flight (thiếu → DỪNG, báo user, không tự bịa)
1. `input/subtitle.srt` tồn tại, đúng format SRT. File SRT tên khác → đổi tên thành `subtitle.srt`.
2. `input/config.example.json` tồn tại — TEMPLATE chuẩn do user quản lý (cấu trúc + mood_map + video_hook mặc định). Thiếu → báo user (có thể khôi phục từ git), không tự bịa template mới.
3. `input/script.txt` (optional) — có thì đọc bổ trợ.
4. Nếu `output/` còn file của project cũ → hỏi user archive trước khi ghi đè.

## Thuật toán
0. **Khởi tạo config từ TEMPLATE (dự án mới):**
   - `input/config.json` đang chứa data project CŨ (title khác, characters không khớp SRT mới) → move vào `archive/old-project-<tên>/config.json` trước.
   - `cp input/config.example.json input/config.json` → mọi dữ liệu project từ đây ghi vào `config.json`.
   - **CẤM sửa `config.example.json`** — nó là template gốc của user, pipeline chỉ ĐỌC. Muốn đổi mặc định chung (mood_map, video_hook...) là việc của user, không phải của bước chạy.
1. Parse SRT → trích: nhân vật (tên, tuổi, vai trò, ngoại hình), variant (flashback/thời kỳ), locations + keywords, tổng thời lượng (timestamp cuối SRT).
2. Auto-fill vào `input/config.json` (đã copy từ template ở bước 0): điền `project.title/description`, `total_duration` = đúng giây SRT, `characters[]`, `settings[]`, `flashback_style` + `flashback_variants` (nếu có flashback), `era` (CHỈ thêm khối này khi bối cảnh có thời kỳ cụ thể); GIỮ nguyên các mặc định template đã có (mood_map, video_hook, `project.file_name`, target_audience) trừ khi SRT/user yêu cầu khác.
3. **HỎI USER trước khi chốt** (không suy đoán ngầm):
   - Config có nhiều variant tuổi/thời kỳ của cùng nhân vật → hỏi variant nào là **timeline chính**, variant nào là flashback → điền `flashback_variants` tường minh (CẤM suy từ dấu `_` trong ID).
   - Chọn `style` — BẮT BUỘC dứt khoát 1 medium (Rule 2.1a), đưa 2 preset: ảnh thật (`photorealistic cinematic film still, 35mm film look, natural skin texture, soft depth of field, clean frame free of watermarks, logos, or AI icons`) hoặc tranh vẽ (`painterly digital illustration, cinematic composition, rich brushwork texture, soft depth of field, clean frame free of watermarks, logos, or AI icons`). CẤM trộn 2 medium; style KHÔNG chứa lighting.
4. Ràng buộc từng field (gate + rule chặn):
   - `nano_name` = chính tên nhân vật ("Jonah", variant = "Young Jonah").
   - `description` PHẢI: mở đầu `[tuổi]-year-old man/woman/boy/girl` (Rule 1.1c); mọi trang phục kèm MÀU cụ thể (Rule 1.1b); positive framing — cấm `no/not/without/never` (viết `clean-shaven upper lip` thay vì `without mustache`).
   - `mood_map` CHỈ chứa ánh sáng + màu + khung hình — CẤM cụm shot scale (`close-up`, `wide shot`, `50mm`...) — gate `--step1` chặn LỖI.
   - `settings[].keywords`: cụm ĐẦU (trước dấu phẩy đầu) là định danh bối cảnh — NGẮN, một danh ngữ lõi (Bước 6 dò tag bằng đúng cụm này).
   - Có `era` → description mặc đồ đúng `era.wardrobe`, settings có marker niên đại, điền `era.forbidden`.
5. Sau khi user chốt config → sinh `output/character-refs.md`:
   - Dòng đầu file: `Nhân vật: N | Bối cảnh: M | TỔNG asset cần vẽ: N+M` + số đếm ở mỗi mục con.
   - **Format BẮT BUỘC mỗi asset** (để `--refs-list` parse được): heading `### TAG — Tên (ghi chú)` + prompt nằm TRONG code block ``` ngay dưới. TAG = nano_name/setting id VIẾT HOA, khoảng trắng → `_`.
   - Mỗi nhân vật (kể cả variant): template Rule 1.4 (`.claude/rules/character.md`) — studio shot, [MEDIUM của style anchor] KHÔNG kèm lighting scene.
   - Mỗi setting: template Rule 2.3a (`.claude/rules/visual-style.md`) — ảnh nền trống không người (positive framing: `an empty courtroom`).
   - Nhắc user: đặt tên ảnh ingredient đúng asset tag (nhân vật = nano_name; bối cảnh = `id` VIẾT_HOA).

## LOOP ENGINE (lặp đến khi máy xác nhận — KHÔNG tự tuyên bố xong)
1. Chạy `python3 scripts/export.py --step1`.
2. `✗ FAIL` → đọc TỪNG dòng lỗi → sửa đúng chỗ trong `config.json` / `character-refs.md` → chạy lại gate.
3. `✓ PASS` → chạy tiếp `python3 scripts/export.py --refs-list` (xuất list vẽ hàng loạt — bước dưới). Lệnh này FAIL (số prompt ≠ tổng asset config) → sửa format asset lỗi trong `character-refs.md` → chạy lại.
4. Cả 2 lệnh OK + user đã chốt config → Bước 1 XONG.
5. Sau 5 vòng cùng 1 lỗi không giảm → DỪNG, báo user. CẤM nới check trong `export.py` để gate xanh.

## Xuất list vẽ hàng loạt (BẮT BUỘC sau khi gate PASS)
```bash
python3 scripts/export.py --refs-list
```
Sinh 2 file từ `character-refs.md`:
- `output/character-refs-list.txt` — prompt đánh số phẳng, user copy cả file paste vào công cụ vẽ hàng loạt.
- `output/character-refs-map.txt` — `N -> TAG.jpg`: ảnh thứ N (đúng thứ tự list) đổi tên thành gì để upload làm ingredient.
THỨ TỰ list = thứ tự asset trong `character-refs.md` — vẽ xong theo lô, đổi tên ảnh theo map là khớp asset tag. KHÔNG viết tay 2 file này — sửa `character-refs.md` rồi chạy lại lệnh.

## Kết quả trả về
- Dòng đếm asset + coverage từ gate; xác nhận đã xuất `character-refs-list.txt` + `character-refs-map.txt`; danh sách câu hỏi đã chốt với user (timeline chính, style, era).
- Nhắc user vẽ ảnh ingredient trong Flow/Uni-X TRƯỚC khi generate scene (copy list → vẽ → đổi tên theo map); bước tiếp theo: `step2-beat` (nên mở phiên mới nếu video dài).

## Tham khảo
`.claude/rules/character.md` (1.1→1.4), `.claude/rules/visual-style.md` (2.1a, 2.3a, 2.5). Nguyên tắc hành vi: CLAUDE.md.
