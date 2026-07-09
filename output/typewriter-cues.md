# Typewriter Cues — hiệu ứng đánh máy (overlay lúc dựng — SINH BỞI export.py, sửa nguồn input/typewriter.json)

- **font**: clean bold monospace (typewriter feel)
- **size**: large — dễ đọc cho khán giả 65+ (≥ 6-8% chiều cao khung)
- **color**: off-white với viền/đổ bóng mềm để nổi trên nền
- **position**: lower third hoặc giữa khung, tránh che mặt nhân vật
- **typing_speed**: chậm (~8-12 ký tự/giây), có con trỏ nhấp nháy
- **hold**: giữ trọn dòng 1.5-2s sau khi gõ xong rồi mờ dần

| # | Time | Scene | Ảnh nền | Loại | Text gõ | Sync |
|---|---|---|---|---|---|---|
| 1 | 00:00:05 | 1 (00:00:00–00:00:12) | 1.jpg | number | `$3,800` | Gõ đúng lúc narration đọc con số, nổi trên nền bốn hồ chết — mồi hook. |
| 2 | 00:02:14 | 12 (00:02:02–00:02:19) | 12.jpg | time_card | `TWO YEARS LATER` | Time card kiểu trailer, xuất hiện khi narration foreshadow 'Two years later'. |
| 3 | 00:02:47 | 15 (00:02:41–00:02:53) | 15.jpg | cta | `Type 1 if you believe` | CTA bình luận — gõ khi narration mời 'type a one in the comments'. |
| 4 | 00:05:40 | 29 (00:05:34–00:05:48) | 29.jpg | quote | `"Nothing worth keeping is ever truly finished." — Dad` | Câu thesis của cha, gõ chậm trên cận cảnh dòng bút chì trên deed. |
| 5 | 00:09:26 | 49 (00:09:21–00:09:31) | 49.jpg | number | `~1,800 fish. Belly-up.` | Cú sốc die-off — gõ khi narration nói 'nearly eighteen hundred'. |
| 6 | 00:11:22 | 60 (00:11:16–00:11:27) | 60.jpg | beat | `Lost a third. Saved the rest.` | Nhịp lật của cứu-đàn-cá lúc bình minh, sau đêm chạy guồng quạt. |
| 7 | 00:23:01 | 121 (00:22:59–00:23:10) | 121.jpg | thesis | `It was a bid.` | Cú nhận ra giữa phim — gõ đúng câu 'It was a bid.', giữ nặng. |
| 8 | 00:31:09 | 161 (00:31:07–00:31:19) | 161.jpg | reveal | `SIX FIGURES` | Payoff — con số sáu chữ số cuối năm hai, không phô trương, gõ chắc. |
| 9 | 00:33:19 | 169 (00:33:00–00:33:23) | 169.jpg | moral | `A pair of hands patient enough to notice.` | Câu moral kết, gõ chậm trên hồ bình minh trước CTA cuối. |

> Dùng THƯA (9 cue / 33 phút) để mỗi dòng giữ được sức nặng — không rải khắp.
> Text tiếng Anh khớp narration (video language = en).
> Đây là overlay editor thêm lúc dựng, KHÔNG phải chữ trong ảnh AI — không đụng Rule 4.5.
> Muốn thêm/sửa/bớt: chỉ sửa file này rồi chạy lại `python3 scripts/export.py` (1 nguồn → metadata + typewriter-cues.md).
