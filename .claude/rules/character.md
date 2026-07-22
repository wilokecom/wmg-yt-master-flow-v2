# Rule: Character Consistency

Quy tắc đảm bảo nhân vật nhất quán xuyên suốt toàn bộ bộ prompt.

## 1.1 — Character Lock

- Mọi nhân vật PHẢI được define trong `config.json > characters[]` ở Bước 1 TRƯỚC KHI viết bất kỳ prompt nào.
- **`nano_name` = chính tên nhân vật** (tên gọi ngắn trong truyện: "Jonah", "Clare"; variant: "Young Jonah"). Bước 1 tự đặt, không cần user cấu hình. Khi scene có nhân vật hoặc nhóm nhân vật nào, prompt ảnh/video gọi đúng tên đó.
- Mỗi nhân vật có một bộ **anchor keywords** mô tả ngoại hình cố định.
- Bộ anchor keywords hoặc `nano_name` PHẢI xuất hiện trong mọi prompt có nhân vật đó.
- KHÔNG được tự thêm chi tiết ngoại hình ngoài anchor keywords (ví dụ: không tự thêm râu, kính, sẹo nếu không có trong character sheet).

Ví dụ anchor keywords:
```
Jonas: "36-year-old man, short brown hair, blue button-down shirt, sturdy build"
Marin: "34-year-old woman, shoulder-length black hair, gray blazer, confident posture"
```

### 1.1a — nano_name PHẢI xuất hiện nguyên vẹn, không dính liền ký tự khác (QUAN TRỌNG)

Flow tham chiếu ảnh ingredient nhân vật bằng cách khớp đúng chuỗi `nano_name`. Nếu prompt gắn ký tự khác dính liền ngay sau tên — phổ biến nhất là sở hữu cách `'s` — khớp lệnh tham chiếu có thể bị hỏng, khiến Flow không nhận ra đó là cùng 1 nhân vật.

- CẤM viết `nano_name` ở dạng sở hữu cách dính liền: `Dalton's`, `Owen's`, `Clare's`...
- Khi cần mô tả biểu cảm/bộ phận/vật sở hữu của nhân vật, diễn đạt lại để tên đứng riêng, KHÔNG dính `'s`:
  - Sai: `"Dalton's blank puzzled expression as he shrugs..."`
  - Đúng: `"Dalton, blank and puzzled, shrugging..."` hoặc `"Dalton wearing a blank puzzled expression as he shrugs..."`
  - Sai: `"Owen's collar catching the light..."`
  - Đúng: `"Owen, collar catching the light,..."` hoặc mô tả lại thành hành động của Owen thay vì sở hữu cách.
- Áp dụng cho MỌI nơi nano_name xuất hiện: `output/prompts.md` (Rule 4.1 Phần 1) và `output/video-prompts.md` (Rule 6.6 subject anchor).
- Lưu ý khi tự kiểm bằng mắt: kiểm tra "có nano_name" bằng substring KHÔNG đủ — `"dalton's"` vẫn chứa substring `"dalton"` nên nhìn qua tưởng đã có character lock, nhưng thực ra sai dạng. Phải kiểm bằng ranh giới từ (word boundary), coi `Name's` là vi phạm dù có chứa tên.

### 1.1b — Trang phục trong anchor PHẢI có màu cụ thể

Mọi trang phục trong character description PHẢI kèm màu cụ thể, không chỉ nêu tên loại trang phục — thiếu màu khiến anchor không khóa đủ, mỗi lần Flow generate sẽ tự chọn màu ngẫu nhiên khác nhau giữa các scene (nhân vật "đổi màu áo" giữa các cảnh liền kề).

- Sai: `"sharp tailored blazer"`, `"dress shirt with sleeves rolled up"`, `"cardigan over a blouse"`
- Đúng: `"sharp navy blue tailored blazer"`, `"steel blue dress shirt with sleeves rolled up"`, `"dusty rose cardigan over a cream blouse"`
- Áp dụng ngay từ Bước 1 khi soạn `config.json > characters[].description` — không để việc bổ sung màu trở thành lần vá lỗi sau này.

### 1.1c — Description PHẢI mở đầu bằng DANH TỪ GIỚI TÍNH + tuổi (QUAN TRỌNG)

Ảnh ingredient nhân vật (Rule 1.4) được vẽ từ `characters[].description`. Nếu description KHÔNG nêu rõ giới tính bằng một danh từ tường minh (`man`/`woman`/`boy`/`girl`), model image gen tự đoán giới tính — và đoán sai thường xuyên (vd nghề "diesel mechanic" + "warm smile" bị vẽ thành phụ nữ). Sai ở ảnh ingredient sẽ lan ra MỌI scene tham chiếu nhân vật đó.

- Mỗi `description` PHẢI bắt đầu bằng cụm `[tuổi]-year-old [man/woman/boy/girl]` (hoặc `[man/woman] in his/her [thập niên]`), TRƯỚC nghề nghiệp/đặc điểm.
  - Sai: `"25-year-old diesel mechanic, short dark brown hair, easy warm smile"` (không có danh từ giới tính → model tự đoán)
  - Sai: `"61-year-old apple farmer, deep-set patient eyes"` (nghề nghiệp trung tính, "clean-shaven" không đủ khóa)
  - Đúng: `"25-year-old man, sturdy diesel mechanic build, short dark brown hair, easy warm smile"`
  - Đúng: `"61-year-old man, weathered apple farmer, deep-set patient eyes"`
- KHÔNG dựa vào tín hiệu gián tiếp (nghề nghiệp, "stubble", "clean-shaven", đại từ `his/her` ở field `name`) để suy giới tính — phải có DANH TỪ trong chính `description`.
- Gate `--step2` cảnh báo mọi character mà `description` thiếu token giới tính (`man/woman/boy/girl/male/female`) — xử lý ở Bước 1, không để lọt sang bước sau.

## 1.2 — Costume Change Protocol

- Nếu nhân vật thay đổi ngoại hình (flashback hồi trẻ, ngày khác, sự kiện khác...), PHẢI tạo một **variant** riêng trong character sheet.
- Variant format: `[id]_[context]`, ví dụ: `jonas_young`, `marin_casual`.
- Scene breakdown PHẢI ghi rõ variant nào được sử dụng.
- Mỗi variant có bộ anchor keywords riêng, KHÔNG trộn lẫn giữa các variant.

Ví dụ:
```json
{
  "id": "jonas_young",
  "name": "Jonas Reed (28 tuổi)",
  "nano_name": "Young Jonas",
  "description": "28-year-old man, short brown hair, wet gray hoodie, worn sneakers"
}
```

## 1.3 — Max Characters Per Scene

- Tối đa **3 nhân vật** trong 1 prompt.
- Nếu scene có 4+ người, PHẢI tách thành 2+ ảnh liên tiếp.
- Khi tách, chia nhân vật theo nhóm tương tác tự nhiên (ai đang nói với ai).
- Nhân vật phụ/nền (crowd, bystanders) KHÔNG tính vào giới hạn 3 — mô tả chung bằng "background figures" hoặc "crowd".

## 1.4 — Character Reference Prompt (ảnh ingredient cho Flow)

Mỗi nhân vật trong config PHẢI có 1 prompt tạo **ảnh tham chiếu** (ingredient), sinh ra ở Bước 1, lưu vào `output/character-refs.md`. Ảnh này dùng làm ingredient trong Flow cho mọi scene có nhân vật đó.

**Template (học từ prompt do Nano Banana nâng cấp):**

```
Medium studio shot of [description đầy đủ từ config: tuổi, đặc điểm mặt, trang phục, phụ kiện đặc trưng], symmetrical forward-facing posture, neutral calm expression, captured with a Hasselblad H6D-100c and a 50mm lens, skin rendered with natural realistic texture, clamshell lighting with a bottom silver reflector creating a soft luminous glow, head and shoulders composition with clear headroom, full head entirely within frame, seamless solid white background, [MEDIUM của style anchor]
```

Quy tắc:
- **[MEDIUM của style anchor]**: chỉ lấy phần tuyên bố medium (ví dụ `photorealistic cinematic film still, natural skin texture` hoặc `painterly digital illustration`), KHÔNG kèm lighting keywords của scene (warm golden lighting...) — ảnh ref cần lighting studio trung tính để Flow tự hòa vào lighting từng scene.
- Ảnh ref PHẢI cùng medium với style anchor của project (Rule 2.1a). Đổi style anchor → PHẢI tạo lại toàn bộ ảnh ref.
- Mỗi variant (Rule 1.2) có ref prompt riêng.
- Phụ kiện nhận diện (safety pin, notebook...) PHẢI xuất hiện trong ref prompt — đây là anchor thị giác giúp nhân vật nhất quán giữa các scene.
- **Đầu `character-refs.md` PHẢI có header đếm asset** `Nhân vật: N | Bối cảnh: M | TỔNG asset cần vẽ: N+M` (N = số `characters[]` kể cả variant, M = số `settings[]`) + số đếm ở mỗi mục con — để user tick khi vẽ ingredient. Gate `--step1` in lại con số này từ `config.json` và kiểm coverage (mỗi asset phải có 1 ref prompt).
- **Format máy-đọc-được (BẮT BUỘC — cho `--refs-list`):** mỗi asset (nhân vật LẪN bối cảnh) là 1 heading `### TAG — Tên (ghi chú)` + prompt nằm TRONG code block ``` ngay dưới heading. TAG = asset tag khi upload (nano_name/setting id viết hoa, khoảng trắng → `_`). `python3 scripts/export.py --refs-list` parse format này để xuất `character-refs-list.txt` (prompt đánh số, copy vẽ hàng loạt) + `character-refs-map.txt` (`N -> TAG.jpg` — ảnh thứ N đổi tên thành gì); THỨ TỰ list = thứ tự asset trong file, nên user vẽ hàng loạt xong chỉ cần đổi tên theo map. Sai format (thiếu heading `###`, prompt ngoài code block) = asset rớt khỏi list — lệnh tự đối chiếu số lượng với config và báo lỗi.
