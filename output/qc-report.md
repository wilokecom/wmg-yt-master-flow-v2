# QC Report (tầng máy — tự sinh bởi export.py --qc)

Scenes: 202 | Prompts: 202 | Lỗi: 0 | Cảnh báo: 15


## CẢNH BÁO (cân nhắc)

- ⚠ [step2] Scene 45: 8+ scene liên tiếp không có establishing/reflection để nghỉ mắt cho khán giả 65+ (rule 3.6)
- ⚠ [step2] Scene 88: establishing 19s ngoài khoảng 10-18s (rule 3.1)
- ⚠ [step2] Scene 101: reflection 21s ngoài khoảng 10-18s (rule 3.1)
- ⚠ [step2] Scene 102: reflection 7s ngoài khoảng 10-18s (rule 3.1)
- ⚠ [step2] Scene 106: dialogue 5s ngoài khoảng 6-12s (rule 3.1)
- ⚠ [step2] Scene 111: 8+ scene liên tiếp không có establishing/reflection để nghỉ mắt cho khán giả 65+ (rule 3.6)
- ⚠ [step2] Scene 122: dialogue 14s ngoài khoảng 6-12s (rule 3.1)
- ⚠ [step2] Scene 124: establishing 6s ngoài khoảng 10-18s (rule 3.1)
- ⚠ [step2] Scene 156: 8+ scene liên tiếp không có establishing/reflection để nghỉ mắt cho khán giả 65+ (rule 3.6)
- ⚠ Scene 58: 3 scene liên tiếp cùng nhóm shot `closeup` (rule 4.2)
- ⚠ Scene 81: 3 scene liên tiếp cùng nhóm shot `closeup` (rule 4.2)
- ⚠ Scenes 1-10: nhóm shot `medium` chỉ 2/3 tối thiểu (rule 4.2)
- ⚠ Scenes 51-60: nhóm shot `medium` chỉ 1/3 tối thiểu (rule 4.2)
- ⚠ Scenes 61-70: nhóm shot `wide` chỉ 0/2 tối thiểu (rule 4.2)
- ⚠ Scenes 111-120: nhóm shot `wide` chỉ 1/2 tối thiểu (rule 4.2)

## QC định tính (AI/người thực hiện sau khi tầng máy PASS — rubric trong .claude/rules/qc.md)

- [x] HOOK: đọc TOÀN BỘ 12 clip + 6 image prompt cửa sổ hook (0→00:01:02), đối chiếu SRT entry 1-11. Ảnh mở khớp narration từng khoảng giây: nhà bị tịch biên (families lose everything) → macro chữ nhỏ 8pt (page 47 / clause 9) → chồng hợp đồng 400 trang → tháp ngân hàng → máy in nhả giấy → tay ký tên → chồng chữ ký → gia đình chất rơ-moóc + gã vest cười → cận nụ cười gã vest → Asher nhỏ bé giữa đồng → cận mặt Asher kiên định. Mỗi clip là 1 cú cắt sang hình mới, escalation như trailer. **Đã sửa:** clip 6.1 push-in→pull-back để 5.2/6.1/6.2 không còn 3 push-in liên tiếp.
- [x] SUBJECT PERSISTENCE (Rule 6.6): mọi clip neo subject (vật thể hoặc nano_name); clip 6.1/6.2 neo "Asher"; không sở hữu cách, không từ đứt gãy thời gian (gate xác nhận). 1 chuyển động liên tục/clip, camera bám subject.
- [x] MOOD ARC: không vùng phẳng >7 scene cùng mood. Arc leo thang có cấu trúc: hạn hán sad/tense → Asher determined (đọc hợp đồng) → cao trào hiên nhà → tòa án triumphant (scene 157) → đòn Collins shock (193) → mưa kết hopeful. 29 emotional_peak rải đều.
- [x] KHỚP NARRATION: sample 12 scene giữa bài (40,60,75,90,100,115,130,145,160,175,185,196) — prompt khớp description: vest xám đám tang (145), flannel+mũ Pioneer của Walter (175), bếp củi (90), ghim thông báo tịch biên (100), máy photocopy Chicago (60). Không mâu thuẫn trang phục/vật thể/thời tiết/trạng thái.
- [x] VISUAL STATE: prompt dùng trạng thái nhìn thấy được (ghim thông báo, đút củi vào bếp, hàm nghiến, tay đặt trên bàn, cửa mở toang). Gate xác nhận 0 từ cốt truyện/phủ định/âm thanh. Object-insert có chất liệu + macro (sổ đỏ 1892, kính lúp trên chữ 8pt, sổ da sờn).
- [x] ERA: bối cảnh đương đại (không có khối era), props nhất quán 2010s nông thôn/doanh nghiệp (bếp củi, mũ hạt giống, cặp da, máy photocopy) — không anachronism.
- [x] KẾT LUẬN: **PASS**. Không scene nào mâu thuẫn narration hay hỏng khớp ingredient. 1 sửa đã áp dụng (clip 6.1 camera motion).

### Verdict cuối: **PASS** ✅ (tầng máy 0 lỗi + tầng định tính PASS)

**15 cảnh báo tầng máy — đã rà, CHẤP NHẬN (ghi rõ lý do):**
- Duration-bound (88/101/102/106/122/124) & rest-run 3.6 (45/111/156): nằm đúng ranh giới câu (Rule 3.4 ưu tiên) / interstitial CTA / 3 cao trào cố ý dồn dập. Chi tiết trong QC Notes của `scene-breakdown.md`.
- Rule 4.2 shot (streak 58/81; cửa sổ 1-10, 51-60, 61-70, 111-120 thiếu medium/wide): đều nằm trong chuỗi đọc/khám phá hợp đồng (macro tài liệu) — ép variety sẽ phá close-up vật thể. Đã lock object-insert khi rebalance (xem KAIZEN 2026-07-08).

→ Prompt sẵn sàng giao sang Flow/Uni-X để vẽ hàng loạt.
