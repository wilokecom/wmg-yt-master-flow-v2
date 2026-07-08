# Rule: Visual Style

Quy tắc đảm bảo phong cách hình ảnh đồng bộ xuyên suốt toàn bộ project.

## 2.1 — Style Anchor

- Mỗi project define một **style string** cố định trong `config.json > style`.
- Style string PHẢI được append vào **cuối mọi prompt**, không ngoại lệ.
- KHÔNG được thay đổi, rút gọn, hoặc diễn giải lại style string giữa các prompt.

### 2.1a — Style string PHẢI dứt khoát về medium (QUAN TRỌNG)

Style string PHẢI tuyên bố rõ ảnh là **ảnh chụp (photograph)** hay **tranh vẽ (illustration)** — chọn 1, không lửng lơ. Đây là nguyên nhân số 1 gây lỗi "lúc ảnh người thật, lúc tranh hư cấu": cụm mơ hồ như `realistic illustration` chứa 2 tín hiệu trái ngược, mỗi lần generate model tự chọn ngẫu nhiên 1 hướng.

- CẤM trộn từ khóa 2 medium trong cùng style string: `realistic illustration`, `photorealistic painting`, `illustrated photo`...
- Preset khuyến nghị (chọn ở Bước 1, ghi vào config):

| Hướng | Style string mẫu |
|---|---|
| Ảnh thật điện ảnh | `photorealistic cinematic film still, 35mm film look, natural skin texture, soft depth of field` |
| Tranh vẽ điện ảnh | `painterly digital illustration, cinematic composition, rich brushwork texture, soft depth of field` |

- Style anchor KHÔNG chứa lighting keywords (warm golden lighting, dramatic light...) — lighting thuộc Phần 4 (mood_map theo từng scene). Style chỉ khóa medium + chất liệu + thẩm mỹ ống kính. Trộn lighting vào style sẽ mâu thuẫn với mood lạnh/tối của scene.
- Ảnh tham chiếu nhân vật (ingredients/reference trong Flow) PHẢI cùng medium với style string — ref ảnh thật đi với style tranh vẽ (hoặc ngược lại) sẽ cho kết quả dao động giữa 2 kiểu.

## 2.2 — Mood-to-Visual Mapping

- Mỗi project define một bảng **mood_map** trong `config.json > mood_map`.
- Khi Bước 2 phân loại mood cho scene, Bước 3 PHẢI dùng đúng visual keywords tương ứng từ bảng này.
- KHÔNG được tự sáng tạo visual keywords ngoài bảng.

Bảng mặc định (có thể override trong config):

| Mood | Visual Keywords |
|---|---|
| nostalgic | soft golden light, warm palette, slight gaussian blur |
| tense | cool blue-gray tones, hard shadows, tight framing |
| hopeful | morning light, open composition, warm highlights |
| shock | dramatic side lighting, shallow DOF, extreme close-up |
| calm | even soft lighting, neutral tones, balanced composition |
| sad | muted desaturated palette, overcast lighting, empty space |
| determined | strong directional light, firm posture, clear focus |
| dismissive | cold office light, distant framing, clinical atmosphere |

## 2.3 — Setting Reuse

- Mỗi location xuất hiện lần đầu → tạo entry trong `config.json > settings[]`.
- Khi location đó xuất hiện lại ở scene sau, PHẢI dùng lại cùng bộ setting keywords.
- KHÔNG được thêm chi tiết mới mâu thuẫn với lần trước.
- Cho phép thêm chi tiết BỔ SUNG (không mâu thuẫn) nếu script đề cập rõ.

Ví dụ:
```json
{
  "id": "marin_office",
  "name": "Văn phòng CEO",
  "keywords": "modern corporate office, large mahogany desk, floor-to-ceiling windows, city skyline view, warm afternoon light"
}
```

Khi scene 1 và scene 25 đều ở văn phòng CEO → cả 2 prompt đều chứa cùng keywords trên.

### 2.3a — Setting Reference Prompt (ảnh ingredient bối cảnh)

Bước 5 (`--unix-export`) gắn asset tag cho CẢ nhân vật LẪN bối cảnh (vd `[COURTROOM]`, `[EAST_FENCE_WALL]`). Nghĩa là mỗi setting cũng là một **asset/ingredient** mà user phải vẽ TRƯỚC rồi mới reference vào scene — y như ảnh nhân vật. Nếu chỉ sinh ảnh ref cho nhân vật, user sẽ thấy tag `[COURTROOM]` trong prompt Uni-X mà không có ảnh bối cảnh nào để upload.

Quy tắc:
- Bước 1 PHẢI sinh **prompt ảnh tham chiếu cho từng setting** trong `config.json > settings[]`, lưu chung `output/character-refs.md` (mục "Bối cảnh / Setting Assets") — cùng file với ảnh ref nhân vật để user vẽ trọn bộ asset trước.
- Template ref bối cảnh (ảnh nền trống, không người, để reference vào nhiều scene):
```
Wide establishing shot of an empty [keywords của setting — nguyên văn cụm định danh + chi tiết], no people present rephrased as unoccupied, natural even lighting, [MEDIUM của style anchor]
```
  Diễn đạt "trống/không người" bằng cụm tích cực: `an empty courtroom`, `an unoccupied workshop` — KHÔNG dùng `no people` (positive framing, Rule 4.6).
- **[MEDIUM của style anchor]**: chỉ lấy phần tuyên bố medium (giống ảnh ref nhân vật, Rule 1.4) — KHÔNG kèm lighting/mood của scene; ảnh nền cần trung tính để hòa vào lighting từng scene.
- Asset tag của setting = `id` viết hoa (Bước 5). Đặt tên ảnh ingredient bối cảnh đúng tag đó khi upload lên Uni-X.
- Cùng medium với style anchor project (Rule 2.1a). Đổi style → vẽ lại toàn bộ ảnh ref (cả nhân vật lẫn bối cảnh).

## 2.4 — Flashback Visual Differentiation

- Scene có beat_type `reflection` hoặc diễn ra ở thời điểm quá khứ PHẢI có sự khác biệt visual rõ ràng so với hiện tại.
- Mặc định: thêm `soft warm vignette, slightly faded colors, dreamy atmosphere` vào prompt flashback.
- Có thể override trong `config.json > flashback_style`.

## 2.5 — Era Lock (khóa niên đại)

Khi project có bối cảnh thời kỳ cụ thể, config define khối `era`:

```json
"era": {
  "name": "1990s rural America",
  "keywords": "1990s rural American South, weathered clapboard farmhouses, gravel roads, old pickup trucks, CRT television, corded telephone, handwritten ledgers",
  "wardrobe": "1990s American workwear, plaid flannel shirts, faded denim, worn leather work boots, canvas jackets, trucker caps",
  "forbidden": ["smartphone", "laptop", "flat-screen", "tablet", "earbuds", "LED", "USB", "wifi", "electric car", "modern SUV", "computer monitor", "drone", "solar panel"]
}
```

Quy tắc:
- **Bước 1**: mọi `characters[].description` PHẢI mô tả trang phục theo `era.wardrobe`; mọi `settings[].keywords` PHẢI chứa marker niên đại từ `era.keywords` (xe, nhà, đồ vật đúng thời kỳ).
- **Style anchor** nên chứa era aesthetic (vd `1990s rural Americana aesthetic, shot on grainy Kodak film stock`) — đây là cách khóa niên đại mạnh nhất vì xuất hiện trong mọi prompt.
- **Bước 3**: prompt KHÔNG được chứa vật thể ngoài niên đại. Gate `--step3` quét `era.forbidden` — dính từ cấm là LỖI chặn.
- Ảnh tham chiếu nhân vật (Rule 1.4) PHẢI mặc trang phục era — đây là anchor niên đại cho mọi scene.
