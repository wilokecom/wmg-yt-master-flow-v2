---
name: step6-unix
description: Bước 6 — Xuất Uni-X prompts. Chạy export.py --unix-export sinh output/unix-batch-NN.txt (asset tag, 100 ảnh/file), rà danh sách scene thiếu setting tag. Dùng khi user nói "chạy bước 6", "xuất unix", "xuất Uni-X prompts". Cần Bước 5 PASS trước.
---

# Bước 6 — Xuất Uni-X Prompts (SCRIPT làm — AI không viết tay)

## Nhiệm vụ DUY NHẤT
Chạy `python3 scripts/export.py --unix-export` → sinh `output/unix-batch-NN.txt` (cú pháp Uni-X: header `(Image Prompt i/n)` đánh số liên tục toàn cục, dòng `Assets:`, dòng `Prompt:` gắn `[TAG]`). Tùy chọn: `--prompts-list` → `output/prompts-list.txt`.

## Pre-flight
1. `output/metadata.json` tồn tại và Bước 5 PASS (nguồn thay đổi → chạy lại Bước 5 trước).

## Thuật toán + LOOP
1. Chạy `python3 scripts/export.py --unix-export`.
2. Script cảnh báo "N scene không xác định được setting" → **PHẢI rà từng scene trong danh sách**, phân loại:
   - CHẤP NHẬN: extreme close-up vật thể, không gian phụ xuất hiện 1 lần (không có entry trong settings[]), hook intro.
   - PHẢI SỬA: scene toàn/trung cảnh ở location ĐÃ define mà thiếu tag → cụm bối cảnh trong prompt lệch với cụm đầu `settings[].keywords` → căn lại config hoặc prompt cho khớp → chạy lại Bước 5 rồi Bước 6.
3. Lặp đến khi danh sách không-tag chỉ còn các scene thuộc diện chấp nhận (ghi rõ kết luận rà soát khi báo user).
4. Nhắc user: tên ảnh ingredient upload Uni-X phải đúng tag (`Owen Consultant` → `OWEN_CONSULTANT`, setting `conference_room_7f` → `CONFERENCE_ROOM_7F`). CHỈ đem file đi vẽ hàng loạt SAU khi Bước 7 QC PASS.

## Kết quả trả về
- Danh sách file batch đã ghi (scene range mỗi file); kết luận rà scene không-tag (bao nhiêu chấp nhận, bao nhiêu đã sửa). Bước tiếp: `step7-qc`.
