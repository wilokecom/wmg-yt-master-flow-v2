# QC Report (tầng máy — tự sinh bởi export.py --qc)

Scenes: 178 | Prompts: 178 | Lỗi: 0 | Cảnh báo: 0


## QC định tính (AI/người thực hiện sau khi tầng máy PASS — rubric trong .claude/rules/qc.md)

- [ ] HOOK: đọc toàn bộ scene + video prompt trong cửa sổ hook, đối chiếu SRT — mỗi clip có 1 chuyển động/thông tin thị giác mới, không 2 clip liền kề cùng camera motion, ảnh mở vòng lặp thị giác đúng narration
- [ ] SUBJECT PERSISTENCE (Rule 6.6): từng video prompt neo subject bằng nano_name + đặc điểm nhận diện, 1 chuyển động chính liên tục, camera bám subject, clip Extend giữ nguyên mô tả — chống nhân vật biến mất giữa clip
- [ ] MOOD ARC: bảng cảm xúc leo thang đúng cấu trúc — emotional_peak nổi bật hơn scene liền trước (shot gần hơn hoặc lighting tương phản)
- [ ] KHỚP NARRATION: sample ≥10 scene ngẫu nhiên giữa bài — prompt không mâu thuẫn description (trang phục, vật thể, thời tiết, trạng thái vật lý)
- [ ] VISUAL STATE: không từ trừu tượng/cốt truyện sót lại, vật thể chính có chất liệu, trạng thái đóng/mở/cũ/mới tường minh
- [ ] ERA: sample close-up vật thể — đúng niên đại, không anachronism ngoài danh sách forbidden
- [ ] KẾT LUẬN: PASS / FAIL + danh sách scene cần sửa

Verdict cuối: (điền sau khi QC định tính)
