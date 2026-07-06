# Rule: Video Prompt (Hook — Veo/Flow)

Quy tắc sinh video prompt cho phần hook, dùng kèm ảnh 1 (image-to-video trong Flow). Nguồn: Veo 3 prompt guide chính thức của Google DeepMind.

## 6.1 — Phạm vi Video Hook

- Config `video_hook`: `enabled`, `duration_s` (cửa sổ hook, vd 120 = 2 phút đầu), `max_clip_s` (mặc định 8), `video_style`.
- Scene thuộc hook ⟺ `start` của scene < `duration_s`. Scene cuối chạm mốc được phủ TRỌN VẸN (hook kết thúc tại end của scene đó, có thể lệch vài giây so với duration_s).
- Trong hook: mỗi scene có CẢ image prompt (như thường, nằm trong prompts.md) VÀ video prompt (file riêng `output/video-prompts.md`, kèm bản copy image prompt).

## 6.2 — Chia clip THEO BEAT NỘI DUNG (không chia đều máy móc)

- Số clip tối thiểu = `ceil(duration / max_clip_s)`, mỗi clip ≤ max_clip_s, phủ liên tục hết scene.
- **Ranh giới clip đặt theo beat của narration**: TRƯỚC khi chia, đọc SRT của scene và liệt kê các beat nội dung (mỗi diễn biến/thông tin/phản ứng = 1 beat). Mỗi clip nhận ĐÚNG 1 beat. Chia đều chỉ là phương án cuối khi narration thuần mô tả.
- Clip KHÔNG vượt ranh giới scene. Đánh số `[stt].[k]` (vd 3.1, 3.2).
- **Frame đầu:** clip .1 dùng ảnh của scene (`[stt].jpg`). Clip .k tiếp theo: nếu tiếp diễn cùng góc máy → **Extend** từ clip trước; nếu beat mới cần CÚ CẮT sang góc/chủ thể khác (reaction shot, insert chi tiết) → tạo **ảnh phụ** `[stt]-[k].jpg` với image prompt riêng ghi ngay trong block clip đó (ảnh phụ chỉ phục vụ video hook, KHÔNG đưa vào metadata.json).

## 6.3 — Template Video Prompt (theo Veo guide)

```
[Camera motion + framing], [Subject (nano_name) + hành động TIẾN TRIỂN trong 8s], [Location ngắn], [Lighting/mood từ mood_map], [video_style], Audio: [ambient nhẹ]
```

Quy tắc:
- **Mô tả chuyển động, không tả lại ảnh tĩnh** — ảnh 1 đã khóa bố cục/nhân vật/bối cảnh. Video prompt chỉ đạo diễn: camera làm gì, nhân vật cử động gì, ánh sáng/khói/bụi chuyển thế nào.
- **Camera motion cho khán giả 65+**: slow push-in, slow pull-back, gentle pan trái/phải, subtle handheld sway, static camera với chuyển động trong khung. CẤM: whip pan, crash zoom, shaky cam mạnh, cut nội clip.
- **Hành động tiến triển** phải khớp narration của scene (đọc Description trong scene-breakdown) và vẽ được trong ≤8s: một cử chỉ, một ánh mắt, một bước đi — không nhồi nhiều diễn biến.
- **KHÔNG dialogue** (không đặt câu thoại trong ngoặc kép) — video hook sẽ lồng narration riêng; nhân vật giữ miệng khép hoặc biểu cảm tĩnh.
- **Audio**: chỉ ambient nhẹ làm nền dưới narration (room tone, distant city hum, soft footsteps). Ghi cuối prompt dạng `Audio: soft ambient room tone`.
- **Nhất quán thị giác**: lighting/mood keywords cùng bộ với image prompt của scene (tra mood_map); `video_style` trong config phải cùng medium với style anchor ảnh (Rule 2.1a).
- Độ dài video prompt: 40-100 từ.

## 6.4 — Format output `output/video-prompts.md`

```markdown
# Video Prompts — Hook: [Title]
Hook window: 0 → [HH:MM:SS] | Clips: [N] | Max clip: 8s

---
## Clip 3.1
**Scene:** 3 | **Time:** 00:00:38 → 00:00:45 | **Duration:** 7s | **Frame đầu:** ảnh 3.jpg
**Image Prompt (ảnh 1):**
[copy NGUYÊN VĂN prompt của scene 3 từ prompts.md]
**Video Prompt:**
[video prompt theo template 6.3]

---
## Clip 3.2
**Scene:** 3 | **Time:** 00:00:45 → 00:00:52 | **Duration:** 7s | **Frame đầu:** Extend từ Clip 3.1
**Video Prompt:**
...
```

## 6.5 — Gate

`python3 scripts/export.py --step3` tự kiểm khi `video_hook.enabled = true`: file tồn tại, clip phủ liên tục từ 00:00:00 đến hết scene hook cuối, mỗi clip 2-8s, clip .1 có image prompt khớp nguyên văn prompts.md, video prompt có camera motion, không chứa dialogue trong ngoặc kép.

## 6.6 — Subject Persistence (chống nhân vật biến mất giữa clip)

Lỗi phổ biến: nhân vật đột ngột biến mất rồi hiện lại giữa clip (subject morphing/vanishing). Nguyên nhân: model mất dấu chủ thể khi prompt không neo subject, quá nhiều chuyển động, hoặc từ ngữ gây đứt gãy thời gian.

Quy tắc BẮT BUỘC cho mọi video prompt:

1. **Neo subject**: video prompt PHẢI gọi nano_name kèm 1 đặc điểm nhận diện từ config (vd `Jonah in the clay-stained flannel shirt`) — KHÔNG chỉ dùng "he/she/the man". Scene không nhân vật → neo vật thể chính thay thế. CẤM gọi nano_name ở dạng sở hữu cách dính liền (`Jonah's`) — phá vỡ khớp lệnh tham chiếu ảnh ingredient, xem Rule 1.1a trong `character.md`.
2. **Subject hiện diện suốt clip**: mô tả 1 hành động LIÊN TỤC từ đầu đến cuối; kết thúc clip subject vẫn trong khung. Muốn nhân vật rời khung → chỉ ở giây cuối clip (`walks out of frame at the very end`) và clip Extend kế tiếp KHÔNG được gọi lại nhân vật đó.
3. **1 clip = 1 chuyển động chính**: một cử chỉ nhân vật + camera nhẹ. KHÔNG nhồi nhân vật + xe chạy + cây đung đưa + mây trôi cùng lúc — model sẽ bỏ rơi bớt yếu tố gây nhấp nháy.
4. **Camera bám subject**: camera motion phải giữ subject trong khung suốt clip (`camera holds on Jonah`, `slow push-in on...`). CẤM pan/push rời khỏi subject giữa clip trừ khi chủ đích chuyển focus sang vật thể được nêu rõ.
5. **CẤM từ đứt gãy thời gian**: suddenly, appears, disappears, vanishes, reveals, transforms, morphs, materializes, cut to, teleports, "then... then...". Muốn diễn biến → mô tả chuyển động liên tục (`slowly raises`, `gradually turns`).
6. **Extend giữ nguyên mô tả**: clip Extend lặp lại đúng subject anchor + bối cảnh của clip trước, chỉ thay hành động tiến triển. Đổi cách mô tả = model vẽ lại khác = nhân vật nhảy hình.

## 6.7 — Kịch tính hóa: mỗi clip 1 beat thị giác MỚI (chống hook phẳng)

Lỗi đã gặp: 3 clip cùng scene đều là "nhân vật ngồi trong phòng" chỉ khác camera motion → hook nhạt, không giữ chân. Quy tắc BẮT BUỘC:

1. **CẤM 2 clip cùng scene chỉ khác camera motion.** Mỗi clip phải thêm ≥1 thông tin thị giác MỚI cho khán giả: hành động mới, phản ứng của nhân vật khác, chi tiết vật thể mới (insert shot), hoặc chuyển chủ thể focus.
2. **Escalation trong scene**: các clip của 1 scene phải leo thang như ngôn ngữ dựng phim — điển hình: wide (bối cảnh + sự việc) → medium (hành động chính của subject) → close-up (phản ứng / chi tiết đắt giá). Clip sau "gần hơn hoặc căng hơn" clip trước.
3. **Khai thác beat từ narration**: video prompt phải lột tả đúng diễn biến câu chuyện tại giây đó (đọc SRT), không mô tả chung chung bối cảnh. Narration nói "Earl cười đến nghiêng ghế" → clip phải là Earl ngửa đầu cười, ghế nghiêng — không phải "Jonah ngồi trong phòng" lần thứ ba.
4. **Reaction shot là vũ khí cảm xúc**: scene có ≥2 nhân vật → ít nhất 1 clip là phản ứng của nhân vật không nói (ánh mắt, nụ cười khẩy, bàn tay siết) — dùng ảnh phụ nếu cần cú cắt.
5. **Gate tự kiểm**: 2 video prompt cùng scene trùng lặp từ vựng cao sẽ bị chặn (similarity check). QC định tính kiểm "mỗi clip 1 thông tin mới" trên toàn hook.
