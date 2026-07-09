# Rule: Video Prompt (Hook — Veo/Flow)

Quy tắc sinh video prompt cho phần hook, dùng kèm ảnh 1 (image-to-video trong Flow). Nguồn: Veo 3 prompt guide chính thức của Google DeepMind.

## 6.1 — Phạm vi Video Hook

- Config `video_hook`: `enabled`, `duration_s` (cửa sổ hook — **mặc định 60 = 1 phút đầu**), `max_clip_s` (mặc định 8), `video_style`.
- **Mục tiêu hook = cảm xúc CỰC MẠNH & DỒN DẬP trong ~1 phút** (theo phong cách trailer mở đầu của kênh kể chuyện): người xem phải bị giữ chân ngay. Ngắn và mạnh hơn là dài và đều.
- Scene thuộc hook ⟺ `start` của scene < `duration_s`. Scene cuối chạm mốc được phủ TRỌN VẸN (hook kết thúc tại end của scene đó, có thể lệch vài giây so với duration_s).
- Trong hook: mỗi scene có CẢ image prompt (như thường, nằm trong prompts.md) VÀ video prompt (file riêng `output/video-prompts.md`, kèm bản copy image prompt).

## 6.2 — Mỗi CLIP = 1 CÚ CẮT sang cảnh khác (hard cut, ảnh riêng) — KHÔNG tua chậm

Nguyên tắc cốt lõi (sửa sau phản hồi user 2026-07-07): **mỗi video clip phải là một CẢNH KHÁC HẲN, một cú cắt (hard cut) sang shot/chủ thể/góc máy mới, mỗi clip mang 1 ảnh riêng và 1 beat cảm xúc mới.** TUYỆT ĐỐI tránh kiểu 2 clip cùng scene chỉ khác camera motion (vd wide rồi slow push-in cùng khung) — đó là lỗi "1 phân cảnh nhiều prompt không thay đổi nhiều" khiến hook nhạt.

- Số clip = `ceil(scene_duration / max_clip_s)`, mỗi clip ≤ max_clip_s, phủ liên tục hết scene. Scene > 8s BẮT BUỘC tách, nhưng mỗi clip tách ra phải là 1 CÚ CẮT thực sự, không phải tua chậm.
- **Frame đầu / ảnh mỗi clip:**
  - Clip `.1` của scene dùng ảnh chính của scene (`[stt].jpg`) — bản copy image prompt nguyên văn từ prompts.md.
  - MỌI clip `.k` (k≥2) là 1 CÚ CẮT → PHẢI tạo **ảnh phụ riêng** `[stt]-[k].jpg` với image prompt riêng (template 5 phần) ghi ngay trong block clip đó, cắt sang: reaction shot nhân vật khác, insert cận cảnh vật thể đắt giá, đảo scale (wide→close), hoặc đối tượng mới của narration. Ảnh phụ CHỈ phục vụ video hook, KHÔNG vào metadata.json.
  - **CẤM dùng "Extend từ clip trước" trong hook** (Extend = tua tiếp cùng khung = nhạt). Chỉ dùng Extend ở ngoại lệ hiếm khi một chuyển động LIÊN TỤC mạnh hơn hẳn một cú cắt (vd cửa từ từ mở) — và phải ghi rõ lý do.
- **Escalation bắt buộc**: chuỗi clip phải leo thang như dựng trailer — mỗi cú cắt "gần hơn / căng hơn / bất ngờ hơn" clip trước (vd: wide bối cảnh quyền lực → cắt cận vật thể sốc → cắt reaction nhân vật → cắt insert chi tiết đắt). Đọc SRT, chọn hình ẢNH MẠNH NHẤT cho từng khoảng giây.
- Đánh số clip `[stt].[k]` (vd 3.1, 3.2). Mỗi clip vẫn ≤ max_clip_s và không vượt ranh giới scene.

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
- **Chống icon AI / watermark (KAIZEN 2026-07-09)**: `video_hook.video_style` trong config PHẢI kết bằng mệnh đề `clean frame free of watermarks, logos, or AI icons` (preset Bước 1 đã gồm) — nhờ đó MỌI video prompt tự chứa mệnh đề ngay trước `Audio:`. Config cũ chưa có → ghi mệnh đề trực tiếp trước `Audio:`. Image prompt ảnh phụ `[stt]-[k].jpg` cũng kết bằng mệnh đề này (nếu style anchor của config đã gồm thì copy style là đủ). Riêng image prompt clip .1 luôn copy nguyên văn từ prompts.md, KHÔNG tự chèn (gate so khớp verbatim). Gate `--step3` cảnh báo video prompt thiếu mệnh đề. Lưu ý: watermark Veo/Gemini do Google đóng SAU render thì prompt không gỡ được (tier/crop khi dựng).
- Độ dài video prompt: 40-110 từ (đã gồm mệnh đề chống watermark).

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
2. **Subject hiện diện suốt clip (TRONG 1 clip)**: neo subject là để chống nhân vật biến mất GIỮA MỘT clip — mô tả 1 hành động LIÊN TỤC từ đầu đến cuối clip đó. Đây KHÔNG mâu thuẫn với hard cut GIỮA CÁC clip: mỗi clip là 1 shot độc lập (ảnh riêng), cắt sang clip sau là chuyện bình thường của dựng phim. Subject persistence áp trong lòng 1 clip, không bắt mọi clip cùng 1 chủ thể.
3. **1 clip = 1 chuyển động chính**: một cử chỉ nhân vật + camera nhẹ. KHÔNG nhồi nhân vật + xe chạy + cây đung đưa + mây trôi cùng lúc — model sẽ bỏ rơi bớt yếu tố gây nhấp nháy.
4. **Camera bám subject CỦA CLIP ĐÓ**: camera motion giữ chủ thể của chính clip đó trong khung suốt clip (`camera holds on Jonah`, `slow push-in on the folder`). Clip insert vật thể → bám vật thể; clip reaction → bám gương mặt.
5. **CẤM từ đứt gãy thời gian TRONG prompt**: suddenly, appears, disappears, vanishes, reveals, transforms, morphs, materializes, cut to, teleports, "then... then...". (Đây là từ trong VĂN BẢN prompt gây model nhảy hình giữa clip — KHÁC với "cú cắt" giữa 2 clip, vốn là 2 ảnh/2 lượt generate riêng.) Muốn diễn biến trong 1 clip → mô tả chuyển động liên tục (`slowly raises`, `gradually turns`).
6. **Clip .1 neo đủ nhân vật của scene** (gate bắt buộc ở clip .1): clip .1 dùng ảnh chính scene nên phải gọi đúng nano_name mọi nhân vật cột Characters. Clip .k hard-cut (ảnh phụ) KHÔNG bị ép gọi lại nhân vật — nếu cắt sang insert vật thể/bối cảnh thì neo vật thể đó thay thế.

## 6.7 — Kịch tính hóa: mỗi clip 1 beat thị giác MỚI (chống hook phẳng)

Lỗi đã gặp: 3 clip cùng scene đều là "nhân vật ngồi trong phòng" chỉ khác camera motion → hook nhạt, không giữ chân. Quy tắc BẮT BUỘC:

1. **CẤM 2 clip liền kề (kể cả khác scene) chỉ khác camera motion / gần giống nhau về hình.** Mỗi clip là 1 CÚ CẮT sang hình mới: chủ thể mới, góc mới, scale mới, hoặc vật thể insert mới. Nếu 2 clip mô tả gần như cùng 1 hình → gộp/bỏ 1 clip.
2. **Escalation toàn hook (không chỉ trong 1 scene)**: cả chuỗi ~1 phút phải leo thang như trailer — hình sau mạnh/gần/sốc hơn hình trước. Điển hình 1 cụm: wide thiết lập nghịch cảnh → cắt cận vật thể gây sốc → cắt reaction nhân vật → cắt insert chi tiết đắt. Kết hook nên là 1 beat treo (câu hỏi/tương phản) để giữ người xem.
3. **Khai thác beat từ narration**: mỗi clip lột tả đúng diễn biến tại giây đó (đọc SRT), chọn hình MẠNH NHẤT — không mô tả chung chung bối cảnh. Narration "14 năm rác chất cao 6 feet" → clip là bức tường rác đen sốc, không phải "người đàn ông ngồi" lần nữa.
4. **Reaction & insert là vũ khí cảm xúc**: ưu tiên xen clip reaction (gương mặt, bàn tay siết) và clip insert (vật thể đắt giá: tập hồ sơ, tấm ảnh cũ) — dùng ảnh phụ cho mỗi cú cắt.
5. **Gate + QC**: gate chặn 2 clip cùng scene trùng lặp từ vựng cao (similarity ≥75%); vì giờ mỗi clip là cú cắt sang hình khác, độ trùng tự nhiên thấp. QC định tính kiểm "mỗi clip 1 cảnh khác + escalation cảm xúc" trên toàn hook ~1 phút.
