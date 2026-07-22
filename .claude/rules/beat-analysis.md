# Rule: Beat Analysis

Quy tắc phân tích nhịp dựng — cách cắt script thành các scene với beat type và duration phù hợp.

## 3.1 — Beat Types & Duration Bounds

Mỗi scene PHẢI được gán 1 trong 6 beat types. Thời lượng giữ ảnh phải nằm trong khoảng cho phép:

| Beat Type | ID | Min (s) | Max (s) | Default (s) | Mô tả |
|---|---|---|---|---|---|
| Establishing | `establishing` | 10 | 18 | 13 | Giới thiệu bối cảnh/location mới. Wide shot. |
| Dialogue | `dialogue` | 6 | 12 | 9 | Hội thoại giữa nhân vật. Medium/over-shoulder. |
| Emotional Peak | `emotional_peak` | 10 | 18 | 13 | Khoảnh khắc cảm xúc mạnh. Close-up biểu cảm. |
| Tension/Conflict | `tension` | 5 | 10 | 7 | Xung đột, căng thẳng, tin xấu. Nhịp nhanh. |
| Reflection | `reflection` | 10 | 18 | 14 | Suy nghĩ nội tâm, hồi tưởng. Tone ấm/mềm. |
| Resolution/Moral | `resolution` | 12 | 25 | 18 | Kết thúc, bài học. Giữ lâu để chiêm nghiệm. |

Cột **Default** là duration khuyến nghị khi narration không đủ rõ để quyết định duration cụ thể. Ưu tiên tính duration thực từ SRT; chỉ dùng Default khi cần ước lượng trước khi có SRT alignment chính xác.

Nếu duration tính ra nằm ngoài khoảng min-max → điều chỉnh cắt scene (tách hoặc gộp) cho đến khi nằm trong khoảng.

## 3.2 — Rhythm Variation

- KHÔNG được có **4+ scene liên tiếp** cùng beat type.
- Nếu phát hiện, PHẢI xử lý bằng 1 trong 2 cách:
  - **Gộp**: 2 scene cùng beat type liền nhau → gộp thành 1 scene dài hơn (nếu vẫn trong max duration).
  - **Chen**: thêm 1 beat type khác ở giữa (ví dụ: chen `establishing` giữa chuỗi `dialogue`).
- Mục tiêu: tạo nhịp thở, tránh đều đều gây buồn ngủ cho khán giả 65+.

## 3.3 — Transition Rule

Các transition sau bị CẤM — không được nhảy trực tiếp:

| Từ | Sang | Yêu cầu |
|---|---|---|
| `tension` | `resolution` | Phải có ≥1 `emotional_peak` hoặc `reflection` ở giữa |
| `establishing` | `emotional_peak` | Phải có ≥1 `dialogue` hoặc `reflection` ở giữa |
| `resolution` | `tension` | Phải có ≥1 `establishing` ở giữa (bối cảnh mới) |

Lý do: cảm xúc cần "hạ cánh" mềm, đặc biệt với khán giả lớn tuổi.

## 3.4 — SRT Alignment

- Mỗi scene PHẢI bắt đầu và kết thúc tại **ranh giới câu hoàn chỉnh** trong SRT.
- KHÔNG được cắt giữa câu nói.
- Timestamp `start` và `end` lấy từ SRT entry tương ứng (dùng thời điểm bắt đầu của subtitle entry đầu tiên và thời điểm kết thúc của subtitle entry cuối cùng trong scene).

## 3.5 — Scene Splitting Criteria

Một đoạn narration NÊN được tách thành scene mới khi xảy ra ≥1 trong các điều kiện sau:

1. **Thay đổi location** — câu chuyện chuyển sang địa điểm khác.
2. **Thay đổi thời gian** — nhảy thời gian (flashback, "ngày hôm sau", "3 tuần sau"...).
3. **Thay đổi nhân vật chính** — focus chuyển sang nhân vật khác.
4. **Thay đổi mood rõ ràng** — từ vui sang buồn, từ căng thẳng sang nhẹ nhõm.
5. **Dialogue turn** — lượt nói chuyển người (mỗi lượt nói dài có thể là 1 scene).
6. **Vượt max duration** — đoạn text quá dài cho 1 beat type → bắt buộc tách.

## 3.5a — Visual Notes phải ghi shot type kèm ĐÚNG tên lens

Cột `Visual Notes` là nguồn mà Bước 4 (kể cả sub-agent batch) **copy nguyên văn** cụm shot type sang Phần 3 của prompt — nên ký pháp sai ở đây sẽ nhân bản ra toàn bộ prompt.

- Viết shot type kèm đúng tên lens trong bảng Rule 4.8: `24mm wide-angle lens`, `35mm lens`, `50mm lens`, `85mm lens`, `85mm portrait lens`, `100mm macro lens`.
  - Sai: `extreme wide shot 24mm`, `close-up 85mm portrait` (tự đặt ký pháp `<số>mm` rời, thiếu chữ `lens`)
  - Đúng: `extreme wide shot, 24mm wide-angle lens`, `close-up, 85mm portrait lens`
- Gate `--step2` báo LỖI cứng nếu ô Visual Notes có cụm shot mà thiếu chữ `lens` (KAIZEN 2026-07-21).

## 3.6 — Audience-Specific Adjustments

Vì đối tượng khán giả là người 65+:

- Ưu tiên duration ở **nửa trên** của khoảng cho phép (gần max hơn min).
- Tránh nhịp nhanh kéo dài — không quá 3 scene `tension` (5-10s) liên tiếp.
- Mỗi 5-7 scene nên có 1 scene `establishing` hoặc `reflection` để mắt được nghỉ.
