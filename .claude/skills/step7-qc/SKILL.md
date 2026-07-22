---
name: step7-qc
description: Bước 7 — QC 2 tầng. Tầng máy (export.py --qc) + tầng định tính (đọc hook, mood arc, sample narration) → verdict trong output/qc-report.md. Dùng khi user nói "chạy QC", "kiểm định chất lượng". BẮT BUỘC trước khi giao prompt sang Flow/Uni-X.
---

# Bước 7 — QC (2 tầng, BẮT BUỘC trước khi vẽ hàng loạt)

## Nhiệm vụ DUY NHẤT
Kiểm định chất lượng toàn bộ output → verdict PASS/FAIL trong `output/qc-report.md`. KHÔNG generate lại nội dung hàng loạt (lỗi tìm ra → sửa đúng scene liên quan, hoặc lỗi nền tảng → báo user cân nhắc archive + chạy lại).

## Tầng 1 — Máy (LOOP ENGINE, phải PASS trước)
1. Chạy `python3 scripts/export.py --qc` (gộp mọi gate + QC1 character lock, QC2 mood verbatim, QC3 flashback, QC4 chống trùng prompt, QC5 shot variety; report ghi vào `qc-report.md`).
2. LỖI → sửa file NGUỒN (scene-breakdown / prompts / config / sfx) → chạy lại đến PASS. KHÔNG sửa tay `qc-report.md` phần máy sinh.
3. Cảnh báo → xử lý từng cái hoặc ghi lý do chấp nhận.
4. **LƯU Ý:** `--qc` GHI ĐÈ `qc-report.md` mỗi lần chạy → chỉ điền verdict định tính SAU lần chạy `--qc` CUỐI CÙNG.

## Tầng 2 — Định tính (AI đọc theo checklist trong qc-report.md — không đọc lại toàn bộ prompt)
1. **HOOK** (quan trọng nhất): đọc TOÀN BỘ scene + image prompt + video prompt trong cửa sổ hook, đối chiếu SRT đoạn đầu — ảnh/clip đầu có visual hook khớp narration; mỗi clip 1 chuyển động/thông tin mới; không 2 clip liền kề trùng camera motion; vòng lặp mở của narration có hình tương ứng.
2. **MOOD ARC**: nhìn cột Mood + Beat toàn bảng (không đọc prompt) — leo thang có nhịp, emotional_peak nổi bật hơn scene liền trước, không vùng phẳng >7 scene cùng mood.
3. **KHỚP NARRATION**: sample ≥10 scene ngẫu nhiên giữa bài (lấy đúng block bằng lệnh) — prompt không mâu thuẫn description (trang phục, vật thể, thời tiết, trạng thái vật lý).
4. **VISUAL STATE + ERA**: trong scene đã sample — vật thể chính có chất liệu + trạng thái tường minh, đúng niên đại.
5. Điền mục "QC định tính" cuối `qc-report.md`: **tick TỪNG ý + verdict PASS/FAIL cụ thể** + danh sách scene cần sửa kèm lý do. Checklist để trống = QC CHƯA XONG dù tầng máy PASS.

## Điều kiện hoàn tất
QC xong ⟺ `--qc` PASS (0 lỗi, cảnh báo đã xử lý/ghi lý do) VÀ verdict định tính PASS đã điền trong qc-report.md. Tìm ra bug loại MỚI → ghi `KAIZEN.md` + codify phòng ngừa (rule/gate) theo Quy tắc Kaizen trong CLAUDE.md.

## Kết quả trả về
- Số lỗi/cảnh báo tầng máy (sau xử lý); verdict định tính + danh sách scene đã sửa; xác nhận sẵn sàng giao Flow/Uni-X.

## Tham khảo
`.claude/rules/qc.md` (7.1→7.3).
