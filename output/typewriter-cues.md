# Typewriter Cues — hiệu ứng đánh máy (overlay lúc dựng — SINH BỞI export.py, sửa nguồn input/typewriter.json)

**QUY TẮC ÂM THANH ĐÁNH CHỮ (BẮT BUỘC khi dựng):**
1. Âm gõ phím CHỈ phát tại đúng cột `Time` của từng cue, chạy đồng bộ với chữ đang gõ, DỪNG sau đúng `Gõ (s)` giây (lúc chữ gõ xong).
2. Scene KHÔNG có trong bảng này = KHÔNG có chữ và KHÔNG có âm đánh chữ.
3. Âm đánh chữ KHÔNG lấy từ field `sfx` trong metadata.json — `sfx` là âm bối cảnh của cảnh (gió, cửa, bước chân...), trộn ở lớp riêng, không liên quan hiệu ứng chữ.

- **font**: chữ in hoa lớn, serif máy chữ, đổ bóng nhẹ cho dễ đọc trên nền ảnh
- **size**: chiếm khoảng 1/8 chiều cao khung — khán giả 65+ xem trên điện thoại phải đọc được
- **speed**: gõ chậm, đều; âm gõ phím chạy đúng theo thời lượng cột Gõ (s) rồi dừng
- **hold**: giữ dòng 1-2s sau khi gõ xong rồi mờ dần
- **position**: 1/3 dưới khung, tránh che mặt nhân vật

| # | Time | Gõ (s) | Scene | Ảnh nền | Loại | Text gõ | Sync |
|---|---|---|---|---|---|---|---|
| tw01 | 00:00:13 | 1.5 | 2 (00:00:10–00:00:19) | 2.jpg | stat | `$91,400` | gõ đúng lúc narration đọc con số đấu giá — cú móc đầu tiên của hook |
| tw02 | 00:00:28 | 1.5 | 4 (00:00:24–00:00:37) | 4.jpg | stat | `22 YEARS` | đè lên hình đồi kudzu một màu — con số giải thích vì sao không ai trả giá |
| tw03 | 00:02:58 | 1.6 | 18 (00:02:54–00:03:11) | 18.jpg | stat | `104 ACRES` | khi narration đọc mô tả thửa đất trong hồ sơ hạt |
| tw04 | 00:04:23 | 3.8 | 26 (00:04:21–00:04:31) | 26.jpg | stat | `THREE GROWING SEASONS` | đồng hồ đếm ngược của cả phim — gõ chậm hơn các cue khác một nhịp |
| tw05 | 00:07:00 | 1.5 | 41 (00:06:57–00:07:10) | 41.jpg | stat | `83 GOATS` | đúng lúc cổng mở và đàn dê tràn xuống |
| tw06 | 00:10:00 | 1.8 | 58 (00:09:59–00:10:04) | 58.jpg | stat | `NINE TREES` | khoảnh khắc đếm xong — trả lời câu hỏi treo từ phút đầu của hook |
| tw07 | 00:17:08 | 1.8 | 96 (00:17:06–00:17:17) | 96.jpg | time_card | `SUMMER TWO` | time card mở màn mùa hè thứ hai |
| tw08 | 00:21:02 | 1.8 | 118 (00:21:00–00:21:12) | 118.jpg | time_card | `YEAR THREE` | time card mở màn năm thứ ba, lúc bắt đầu trồng cây |
| tw09 | 00:24:27 | 3.1 | 137 (00:24:25–00:24:35) | 137.jpg | time_card | `SPRING, YEAR FOUR` | time card ngày hạt tới thẩm định — cao trào hành chính |
| tw10 | 00:26:38 | 1.5 | 151 (00:26:36–00:26:47) | 151.jpg | stat | `$462,800` | định giá lại — đặt cạnh trí nhớ về $91,400 ở đầu phim |
| tw11 | 00:27:32 | 2.2 | 156 (00:27:30–00:27:38) | 156.jpg | stat | `1,341 POUNDS` | vụ hồ đào đầu tiên sau 22 năm |
| tw12 | 00:31:34 | 6.0 | 180 (00:31:32–00:31:45) | 180.jpg | moral | `NEVER DEAD GROUND — ONLY COVERED GROUND` | câu thesis của cả phim, gõ chậm nhất, giữ dòng lâu nhất trước khi mờ |

> Chỉ 12 cue cho video 33 phút — dùng thưa để mỗi lần chữ hiện lên đều có sức nặng.
> Âm gõ phím CHỈ phát tại cột Time của từng cue và dừng sau đúng cột Gõ (s); scene không có trong bảng thì không có chữ và không có âm đánh chữ.
> Muốn thêm/sửa cue: chỉ sửa file này rồi chạy lại python3 scripts/export.py — KHÔNG sửa tay metadata.json hay typewriter-cues.md.
