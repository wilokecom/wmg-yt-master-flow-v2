# Rule: Prompt Structure

Quy tắc cấu trúc prompt đảm bảo output đồng nhất, dùng được cho Nano Banana.

## 4.1 — Prompt Template

Mọi prompt PHẢI tuân theo cấu trúc 5 phần, theo đúng thứ tự:

```
[1. Characters + action], [2. Setting/environment], [3. Shot type], [4. Mood visual keywords], [5. Style anchor]
```

Các phần cách nhau bằng dấu phẩy. KHÔNG dùng dấu chấm, dấu chấm phẩy, hoặc xuống dòng giữa các phần.

### Chi tiết từng phần:

**Phần 1 — Characters + Action:**
- Gọi nhân vật bằng `nano_name` đã define trong config.
- Mô tả hành động cụ thể đang diễn ra.
- Ví dụ: `Jonas standing in a dimly lit basement inspecting a junction box with a flashlight`
- CẤM viết `nano_name` dính liền sở hữu cách (`Jonas's`, `Dalton's`...) — phá vỡ khớp lệnh tham chiếu ảnh ingredient trong Flow. Diễn đạt lại để tên đứng riêng (chi tiết + ví dụ: Rule 1.1a trong `character.md`).

**Phần 2 — Setting/Environment:**
- Dùng đúng keywords từ `config.json > settings[]` nếu location đã define.
- **Cụm ĐẦU TIÊN (trước dấu phẩy đầu) của `settings[].keywords` là định danh bối cảnh** — prompt PHẢI chứa nguyên văn cụm này khi scene ở location đó. Bước 6 (`--unix-export`) nhận diện setting để gắn asset tag bằng đúng cụm này (khớp KHÔNG phân biệt hoa-thường); viết cụm rút gọn khác đi sẽ làm scene mất tag bối cảnh (xem KAIZEN 2026-07-06, 2026-07-07). Khi cần tiết kiệm từ, giữ cụm đầu nguyên vẹn và lược các cụm sau.
- **Cụm định danh nên NGẮN** (một danh ngữ lõi, vd `long wall of dark black-brown slum gum residue`), KHÔNG nhồi kích thước/vị trí/số đo vào cụm đầu (`...six feet high along a wire fence line` để ra sau dấu phẩy) — cụm càng dài agent càng dễ lược mất khi viết prompt, gây trượt tag.
- Ngoại lệ: cận cảnh chi tiết (extreme close-up vật thể) hoặc không gian phụ xuất hiện 1 lần không cần chứa cụm định danh.
- Thêm chi tiết cụ thể của scene nếu script đề cập.
- Ví dụ: `old concrete basement with exposed conduit pipes and low ceiling`

**Phần 3 — Shot Type:**
- Chọn 1 trong các shot types dưới đây:
  - `extreme wide shot` — toàn cảnh, thấy cả không gian
  - `wide shot` — thấy toàn thân nhân vật + bối cảnh
  - `medium shot` — từ thắt lưng trở lên
  - `medium close-up` — từ ngực trở lên
  - `close-up` — khuôn mặt hoặc chi tiết
  - `extreme close-up` — 1 chi tiết nhỏ (tay, mắt, vật thể)
  - `over-shoulder shot` — nhìn qua vai nhân vật này sang nhân vật kia
  - `low angle shot` — nhìn từ dưới lên
  - `high angle shot` — nhìn từ trên xuống
- Ví dụ: `medium shot from low angle`

**Phần 4 — Mood Visual Keywords:**
- Lấy từ `config.json > mood_map` theo mood đã phân loại ở Bước 2.
- KHÔNG tự sáng tạo, PHẢI dùng đúng keywords trong bảng.
- **Copy NGUYÊN VĂN kể cả DẤU PHẨY nội bộ** — CẤM bỏ/đổi phẩy giữa các cụm. Sai thường gặp của sub-agent batch: gộp `strong directional light, firm posture, clear focus` thành `strong directional light firm posture clear focus` (bỏ phẩy) → gate `--step4` + `--qc` QC2 báo "thiếu mood keywords nguyên văn" (KAIZEN 2026-07-17). Gate so khớp CHÍNH XÁC chuỗi mood_map, thiếu 1 dấu phẩy = FAIL.
- Ví dụ: `cool blue-gray tones, hard shadows, tight framing`

**Phần 5 — Style Anchor:**
- Copy nguyên văn `config.json > style`.
- KHÔNG thay đổi, rút gọn, hoặc diễn giải lại.
- Ví dụ: `cinematic realistic illustration, warm golden lighting, soft depth of field`

### Ví dụ prompt hoàn chỉnh:

```
Jonas standing in a dimly lit basement inspecting a junction box with a flashlight, old concrete walls with exposed conduit pipes and low ceiling, medium shot from low angle, cool blue-gray tones hard shadows tight framing, cinematic realistic illustration warm golden lighting soft depth of field
```

## 4.2 — Shot Type Distribution

Trong mỗi **10 scene liên tiếp**, PHẢI đảm bảo:

| Shot Type | Tối thiểu | Tối đa liên tiếp |
|---|---|---|
| Wide / extreme wide | 2 | 3 |
| Medium / medium close-up | 3 | 3 |
| Close-up / extreme close-up | 2 | 2 |
| Over-shoulder / angle shots | 1 | 2 |

Mục đích: tránh đơn điệu, giữ sự đa dạng visual cho khán giả 65+.

**LƯU Ý phân loại (KAIZEN 2026-07-15):** `shot_cat` trong `export.py` phân nhóm theo LENS, nên quota `Close-up/extreme close-up ≥2/thập kỷ` CHỈ tính `close-up (85mm portrait lens)` và `extreme close-up (100mm macro lens)`. `medium close-up (85mm lens)` và `medium shot (50mm lens)` đều đếm là **Medium** — một thập kỷ trộn nhiều medium close-up vẫn có thể 0/2 closeup. Khi soạn Visual Notes (Bước 2) và prompt (Bước 4), mỗi 10 scene chủ động đặt ≥2 close-up THẬT (mặt/cảm xúc/insert vật thể) + ≥1 angle, đừng dựa vào medium close-up để lấp quota closeup.

## 4.3 — No Conflicting Details

- Prompt KHÔNG được mâu thuẫn với narration text trong scene breakdown.
- Nếu script nói "Jonas mặc áo sơ mi xanh" → prompt KHÔNG được mô tả áo trắng.
- Nếu script nói "trời mưa" → prompt PHẢI có yếu tố mưa.
- AI PHẢI cross-check prompt với `description` trong scene breakdown trước khi finalize.
- Scene REPLAY lại đúng khoảnh khắc của cold open (cấu trúc "N hours earlier") PHẢI dùng cùng setting với scene cold-open tương ứng — Bước 2 ghi chú "(replay scene N)" vào Visual Notes để batch/sub-agent Bước 4 thấy ràng buộc (KAIZEN 2026-07-11).

## 4.4 — Prompt Length

- Tối thiểu: 20 từ (đủ thông tin để AI vẽ).
- Tối đa: 75 từ (quá dài sẽ làm AI image gen bị loãng focus).
- Khuyến nghị: 35-55 từ.

## 4.5 — Negative Constraints

Trong prompt, KHÔNG được có:
- Văn bản / chữ viết trên ảnh (text, letters, words, signage with readable text).
- Tên riêng dạng text hiển thị (ví dụ: "a sign saying Jonas Reed" — KHÔNG).
- Mô tả âm thanh (ví dụ: "loud music playing" — không thể hiện bằng ảnh).
- Chỉ dẫn thời lượng (ví dụ: "hold for 12 seconds" — không thuộc prompt ảnh).

## 4.6 — Visual State, Not Narrative (QUAN TRỌNG)

Model tạo ảnh KHÔNG hiểu cốt truyện — nó chỉ vẽ đúng những gì prompt mô tả bằng mắt. Mọi ý nghĩa câu chuyện PHẢI được dịch thành **trạng thái vật lý nhìn thấy được**:

- **Ghi rõ trạng thái vật thể**: đóng/mở, khóa/không khóa, mới/cũ, nguyên/vỡ. Câu chuyện nói "chiếc hòm khó mở chứa bí mật" → prompt viết `an old iron chest with the lid firmly closed, sealed by a heavy rusted padlock` — TUYỆT ĐỐI KHÔNG viết "chest containing a secret" (model sẽ vẽ thứ bên trong → hòm mở).
- **CẤM từ ngữ hàm ý cốt truyện** (model không vẽ được hoặc vẽ sai): secret, hidden, mysterious, forbidden, unknown, memories, past, story... → thay bằng dấu hiệu thị giác: `secret` → `closed/locked/covered`, `mysterious` → `dimly lit, obscured by shadow`, `old memories` → `faded photograph, worn edges`.
- **Positive framing** (theo guide chính thức của Google): mô tả cái MUỐN thấy, không mô tả cái không muốn. Viết `empty street` thay vì `no cars`; `bare desk` thay vì `without papers`. CẤM các từ phủ định trong prompt: no, not, without, never.
- **Nhân quả không vẽ được**: "vừa mới xảy ra", "sắp mở", "đang định" → chọn 1 khoảnh khắc tĩnh cụ thể và mô tả nó (bàn tay đặt trên nắp hòm, chìa khóa cắm trong ổ chưa xoay).

## 4.7 — Mood bằng ngôn ngữ điện ảnh

Để mood ổn định và đúng cảm xúc câu chuyện (theo guide Nano Banana — "prompt like a Creative Director"):

- Mood keywords trong mood_map nên dùng **ánh sáng + màu + khung hình**, là 3 thứ model kiểm soát tốt nhất: `golden hour backlighting, long shadows`, `chiaroscuro lighting, high contrast`, `muted teal color grading`.
- Cảm xúc nhân vật mô tả qua **biểu hiện vật lý nhìn thấy**: `slumped shoulders, eyes downcast` thay vì `feeling defeated`; `clenched jaw, white knuckles` thay vì `angry inside`.
- KHÔNG dùng từ trừu tượng làm mood: tension, grief, hope... đứng một mình — luôn kèm biểu hiện thị giác.
- **Mood KHÔNG được chứa cụm shot scale** (`extreme close-up`, `wide shot`, `50mm`...). Scale là việc của Phần 3, do Bước 2 quyết theo quota Rule 4.2; nhét scale vào mood làm mọi scene cùng mood bị ép về một cỡ khung, mâu thuẫn với shot đã chọn (Rule 2.2, KAIZEN 2026-07-20).

## 4.8 — Ngôn ngữ máy quay & an toàn khung hình

Học từ prompt do Nano Banana tự nâng cấp: tên ống kính và framing tường minh cho ảnh ổn định hơn hẳn.

**Bảng lens theo shot type — Phần 3 của prompt PHẢI kèm lens tương ứng:**

| Shot type | Lens đi kèm |
|---|---|
| extreme wide shot | 24mm wide-angle lens |
| wide shot | 35mm lens |
| medium shot / over-shoulder shot | 50mm lens |
| medium close-up | 85mm lens |
| close-up | 85mm portrait lens |
| extreme close-up | 100mm macro lens |

Ví dụ Phần 3: `medium shot from low angle, 50mm lens`. Dùng NHẤT QUÁN bảng này trong toàn project — đổi lens tùy tiện giữa các scene cùng loại shot sẽ làm ảnh không đồng bộ.

**An toàn khung hình:** với close-up và medium close-up có mặt người, thêm `full head within frame` để chống lỗi cắt cụt đầu.

**Chất liệu (materiality):** khi vật thể là chi tiết chính của scene, mô tả chất liệu cụ thể: `worn leather briefcase` thay vì `briefcase`, `rusted iron padlock` thay vì `lock`.
