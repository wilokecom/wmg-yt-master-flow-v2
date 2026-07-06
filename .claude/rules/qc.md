# Rule: QC (Bước 5 — kiểm định chất lượng)

Bước QC chạy SAU khi bước 4 PASS, TRƯỚC khi giao prompt sang Flow. Gồm 2 tầng bắt buộc theo thứ tự.

## 7.1 — Tầng máy (bắt buộc PASS trước)

```bash
python3 scripts/export.py --qc
```

Tự kiểm và ghi report vào `output/qc-report.md`:
- Toàn bộ gate bước 2 + 3 (coverage, style anchor, era, negative framing, video hook...)
- **QC1 Character lock**: scene có nhân vật → prompt phải chứa đúng nano_name
- **QC2 Mood verbatim**: prompt phải chứa nguyên văn mood keywords từ mood_map
- **QC3 Flashback**: scene có variant quá khứ phải kèm flashback_style
- **QC4 Chống trùng lặp**: 2 prompt mở đầu giống nhau → nguy cơ 2 ảnh giống nhau gây nhàm
- **QC5 Shot variety**: phân phối shot mỗi 10 scene + giới hạn liên tiếp (rule 4.2)

LỖI → sửa file nguồn (scene-breakdown.md / prompts.md / config) → chạy lại đến PASS. KHÔNG sửa qc-report.md tay.

## 7.2 — Tầng định tính (AI đọc — theo checklist trong qc-report.md)

Nguyên tắc: KHÔNG đọc lại toàn bộ 200 prompt (tràn context). Chỉ đọc đúng các vùng sau:

1. **HOOK (quan trọng nhất — quyết định giữ chân)**: đọc TOÀN BỘ scene + image prompt + video prompt trong cửa sổ hook, đối chiếu SRT đoạn đầu:
   - Ảnh/clip đầu tiên phải chứa yếu tố bất thường thị giác (visual hook) khớp câu narration đầu — khán giả phải tự hỏi "chuyện gì đây?"
   - Mỗi clip có đúng 1 chuyển động/thông tin mới; không 2 clip liền kề trùng camera motion
   - Vòng lặp mở của narration phải có hình tương ứng (vật thể/chi tiết được nhắc mà chưa giải thích → phải xuất hiện trong ảnh)
2. **MOOD ARC**: nhìn cột Mood + Beat toàn bảng scene-breakdown (không cần đọc prompt) — cảm xúc phải leo thang có nhịp, emotional_peak phải nổi bật hơn scene liền trước (shot gần hơn / lighting tương phản); không vùng phẳng >7 scene cùng mood
3. **KHỚP NARRATION**: sample ngẫu nhiên ≥10 scene giữa bài (dùng lệnh lấy đúng block, không đọc cả file) — prompt không mâu thuẫn description: trang phục, vật thể, thời tiết, trạng thái vật lý (Rule 4.3, 4.6)
4. **VISUAL STATE + ERA**: trong các scene đã sample — vật thể chính có chất liệu, trạng thái tường minh, đúng niên đại
5. Ghi kết quả vào cuối `output/qc-report.md` mục "QC định tính": verdict PASS/FAIL + danh sách scene cần sửa kèm lý do

## 7.3 — Điều kiện hoàn tất QC

QC xong ⟺ `--qc` PASS (0 lỗi) VÀ mục "QC định tính" trong qc-report.md có verdict PASS. Chỉ khi đó mới giao prompt sang Flow. Nếu model sản xuất là model nhỏ (Sonnet...), tầng định tính NÊN chạy bằng model mạnh hơn hoặc phiên riêng chỉ làm QC.
