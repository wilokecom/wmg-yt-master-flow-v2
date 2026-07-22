# QC Report (tầng máy — tự sinh bởi export.py --qc)

Scenes: 186 | Prompts: 186 | Lỗi: 0 | Cảnh báo: 0


## QC định tính (thực hiện 2026-07-22 — rubric .claude/rules/qc.md 7.2)

- [x] **HOOK** — đọc TOÀN BỘ 6 scene hook + 11 video prompt, đối chiếu SRT 0-63s.
  - Khớp narration từng khoảng giây: 1.1 phiên đấu giá không ai trả giá / 1.2 búa nằm im khi thềm lặng đi / 2.1 Corinne giơ thẻ / 2.2 phản ứng những gương mặt quay lại / 3.1 tấm séc bảo hiểm / 4.1 làn sóng kudzu ("still water takes a low field") / 4.2 mái kho chìm dưới lá — khớp chính xác câu "Then the hay barn. Then the shape of the hills" / 5.1 dolly dọc đường ("read from the highway") / 6.1 tiếng cười / 6.2 mặt Corinne bất động (beat treo).
  - Visual hook ảnh đầu: phiên đấu giá mà KHÔNG một cánh tay nào giơ lên — bất thường đủ để đặt câu hỏi, và chính là câu narration đầu tiên.
  - Camera motion 11 clip: pull-back / static / push-in / pan / tilt / tracking / static / dolly / push-in / handheld sway / locked-off — KHÔNG cặp liền kề nào trùng chuyển động.
  - Mỗi clip 1 ảnh riêng, hard cut, không clip nào tua chậm cùng khung.
- [x] **SUBJECT PERSISTENCE (Rule 6.6)** — clip 2.1 (clip duy nhất trong hook có nhân vật ở cột Characters) neo `Corinne in the olive-green canvas barn coat` + `camera holds her centered`; các clip còn lại neo vật thể chính (búa, mái kho, thân cây, chuông). Mỗi clip đúng 1 chuyển động liên tục; không từ đứt gãy thời gian.
- [x] **MOOD ARC** — 186 scene, KHÔNG vùng phẳng nào ≥6 scene cùng mood (kiểm bằng máy). Arc đúng cấu trúc 4 mùa: mở bằng dismissive/sad (bị coi thường) → determined xen tense suốt mùa 1-2 → cụm vindication dày lên từ scene 78 (báo cáo đất) và 150-155 (định giá lại + vụ hồ đào) → kết bằng nostalgic/hopeful (treo chuông). 34 emotional_peak đều nằm ở đúng nút thắt (cái giếng, chín thân cây, vành vỏ bị gặm, thư của hạt, tháo chuông).
- [x] **KHỚP NARRATION** — sample ngẫu nhiên 12 scene giữa bài (24, 29, 32, 36, 49, 56, 57, 58, 80, 121, 141, 158): 12/12 prompt khớp description, không mâu thuẫn trang phục/vật thể/thời tiết/trạng thái. Ghi chú: scene 29 chọn khoảnh khắc cuối của đoạn (đứng nhìn đồi kudzu) thay vì cảnh ký giấy — đúng Rule 4.6 (chọn 1 khoảnh khắc tĩnh).
- [x] **SFX (Rule 8.7/8.8)** — 299 keyword / 298 cụm khác nhau; 0 âm đánh chữ, 0 nhạc nền. Hợp mood trong các scene đã sample: 58 (shock) `palm patting rough tree bark`, 121 (hopeful) `grafting tape wound around a stem`, 158 (calm) `kitchen lamp buzzing faintly`. Room tone đổi theo location, không dùng lại một cụm.
- [x] **VISUAL STATE** — sample cho thấy vật thể chính đều có chất liệu + trạng thái tường minh (`creased pale blue paper settlement check`, `bark stripped in a clean ring down to pale wet wood`, `tightly wrapped graft union`). Không sót từ trừu tượng/cốt truyện. Giấy tờ tả bằng `faint ink marks`/`faint gray printed columns` — không chữ đọc được.
- [x] **ERA** — project KHÔNG có khối `era` (bối cảnh đương đại Georgia), không áp dụng. Không phát hiện anachronism trong sample.

### Quyết định có chủ ý (ghi lại để không bị coi là lỗi ở lần review sau)
1. **Clip 5.2 (43-48s)** cho thấy thân cây hồ đào nhợt dưới tán TRƯỚC khi narration nhắc tới chín cái cây (scene 7, 63s). Đây là foreshadow kiểu trailer, không mâu thuẫn narration đang đọc ("một làn sóng xanh không bao giờ đổi hình") — hình mơ hồ, chỉ gợi "có gì đó bên trong". Giữ.
2. **Scene 17** (hành lang bên trong tòa án) KHÔNG gắn asset `COURTHOUSE_STEPS` — asset đó là mặt tiền ngoài trời, dùng chung sẽ ra ảnh sai. Chấp nhận không có tag bối cảnh.
3. **63/186 scene không có asset tag bối cảnh** — đã rà từng scene ở Bước 6: 31 close-up vật thể, 21 medium ở không gian phụ 1 lần, 6 angle, 5 wide ở không gian 1 lần (nghĩa trang, hầm nhà thờ, hành lang tuyến điện). Không scene nào thuộc diện "toàn/trung cảnh ở location đã define mà trượt tag".
4. **Ảnh ingredient `COURTHOUSE_STEPS`** (do user vẽ) có chữ khắc đọc được trên mặt tiền. Không chặn sản xuất; nếu muốn sạch tuyệt đối theo Rule 4.5 thì vẽ lại ảnh ref đó với mặt đá trơn.

### KẾT LUẬN
**PASS.** Tầng máy: 0 lỗi, 0 cảnh báo (`--qc`). Tầng định tính: 7/7 mục đạt, 0 scene phải sửa lại. Bộ prompt sẵn sàng giao sang Flow/Uni-X để vẽ hàng loạt.

### Lượt kiểm bổ sung (QC lần 2 — nguồn không đổi)
- Sample thứ hai 10 scene khác lượt đầu (33, 55, 59, 70, 73, 84, 93, 132, 154, 169): 10/10 khớp description; scene 154 dùng đúng `Older Otis`. Tổng 2 lượt: 22 scene kiểm tay.
- Cặp replay: scene 2↔20 (cùng trang phục + bối cảnh, khác tư thế) ĐẠT; scene 4↔179 (cùng nguyên văn cụm định danh đồi kudzu) ĐẠT.
- 5 ảnh phụ hook đã gắn asset tag trong video-prompts-list.txt (COURTHOUSE_STEPS ×3, KUDZU_HILLSIDE, UNDER_CANOPY, CORINNE).

### Cập nhật SFX theo Rule 8.9 mới (sau QC lượt 2 — user yêu cầu 2026-07-22)
Phát hiện sfx cũ FULL-COVERAGE 186/186 scene (sai mục đích — sfx phải là điểm nhấn cảm xúc). Đã tinh chỉnh: **68/186 scene có keyword (37%)**, 126 cụm đều khác nhau, 0 âm đánh chữ, 0 nhạc nền; giữ trọn motif chuông đồng (38→42→96→112→174→175→177→178→185→186). Gate `--step3` mới (đo mật độ) PASS; metadata.json + sfx-timeline.json đã rebuild; tầng máy `--qc` chạy lại 0 lỗi 0 cảnh báo. Mục SFX của verdict lượt 1 (299 keyword/186 scene) hết hiệu lực — thay bằng số liệu này.

Verdict cuối: **PASS — 2026-07-22 (lượt 3, sau tinh chỉnh mật độ SFX)**
