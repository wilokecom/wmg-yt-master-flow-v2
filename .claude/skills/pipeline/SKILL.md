---
name: pipeline
description: Chạy toàn bộ pipeline WMG storyboard từ Bước 1 → 7 tuần tự, mỗi bước theo đúng skill riêng và dừng ở gate FAIL. Dùng khi user nói "chạy toàn bộ pipeline", "chạy hết các bước", "full pipeline".
---

# Pipeline — chạy tuần tự Bước 1 → 7

## Nhiệm vụ
Điều phối: chạy lần lượt từng bước, mỗi bước theo ĐÚNG skill của nó, không gộp tắt, không bỏ bước.

## Quy trình
1. **Xác định điểm bắt đầu bằng máy, không đoán**: chạy lần lượt `python3 scripts/export.py --step1 / --step2 / --step3 / --step4 / --validate` — gate đầu tiên FAIL (hoặc file output đầu tiên chưa tồn tại) chính là bước cần làm. Mọi gate PASS + metadata hợp lệ → chỉ còn Bước 6/7.
2. Với từng bước chưa xong, theo thứ tự 1 → 2 → 3 → 4 → 5 → 6 → 7:
   - Invoke skill tương ứng (`step1-setup`, `step2-beat`, `step3-sound`, `step4-prompts`, `step5-export`, `step6-unix`, `step7-qc`) và làm theo SKILL.md của bước đó — bao gồm Pre-flight, MỤC TIÊU SỐ và LOOP ENGINE.
   - Bước chỉ được coi là xong khi gate của nó PASS. Gate FAIL sau 5 vòng sửa → DỪNG pipeline tại đó, báo user.
3. **Điểm dừng chờ user** (không tự vượt): Bước 1 cần user chốt config (style, timeline chính, era) — dừng hỏi rồi mới đi tiếp.
4. **Chống tràn context** (video >20 phút): áp nghiêm quy tắc segment/batch trong skill Bước 2 và 4. Context gần đầy → dừng ở RANH GIỚI bước, báo user mở phiên mới (dữ liệu đã an toàn trong file; phiên mới chạy lại các lệnh gate ở mục 1 là biết đang dở đâu).

## CẤM
- Tự tuyên bố "bước X xong" khi gate chưa PASS.
- Làm việc của bước sau khi bước trước còn FAIL (vd viết prompt khi beat chưa PASS).
- Sinh nội dung bằng vòng lặp script thay vì làm thật; tắt/nới check cho gate xanh.

## Kết quả trả về
Sau mỗi bước: báo ngắn kết quả gate. Kết thúc: tổng kết bước nào xong, bước nào đang chờ gì từ user.
