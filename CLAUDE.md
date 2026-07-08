# WMG Storyboard Prompt Generator

Quy trình chuyển đổi Script + SRT thành bộ prompt ảnh AI cho Nano Banana, phục vụ sản xuất video storytelling dạng slideshow.

## Mục tiêu

Từ input (script, SRT, config) → tạo ra:
1. **Scene Breakdown** — bảng phân tích nhịp dựng (beat analysis)
2. **Prompt Set** — bộ prompt ảnh cho Nano Banana
3. **metadata.json** — file kết nối ảnh với timeline video

## Đối tượng khán giả mục tiêu

Video nhắm đến người xem 65+ tuổi → ảnh cần rõ ràng, nhịp chậm hơn phim ảnh, chuyển cảnh nhẹ nhàng, không gây rối mắt.

## Nguyên tắc hành vi chung (áp dụng cho AI ở mọi bước)

Các Rule trong `.claude/rules/` quy định NỘI DUNG đúng là gì (character nào, style nào, duration bao nhiêu...). Mục này quy định CÁCH LÀM VIỆC để tạo ra nội dung đó — áp dụng xuyên suốt Bước 1-6 và cả khi sửa lỗi ngoài pipeline.

**Đánh đổi:** các nguyên tắc dưới đây ưu tiên chính xác và nhất quán hơn tốc độ. Với việc thật sự nhỏ (sửa 1 từ, 1 lỗi chính tả trong 1 dòng), dùng phán đoán — không cần áp dụng máy móc toàn bộ quy trình hỏi–xác nhận bên dưới.

### 1. Suy nghĩ trước khi tạo

**Đừng suy đoán ngầm. Đừng giấu sự mơ hồ. Nêu rõ đánh đổi.**

Trước khi cắt scene, chọn variant, hoặc gán mood:
- Nếu config có nhiều variant tuổi/thời kỳ của cùng 1 nhân vật, PHẢI hỏi rõ user variant nào là "timeline chính" của toàn video ngay ở Bước 1 — không suy đoán qua quy ước đặt tên ID. *Lỗi thường gặp: coi mọi ID có dấu `_` (vd `jonah_1987`) là "variant quá khứ cần flashback_style", trong khi đó chính là nhân vật chính xuyên suốt timeline hiện tại của video.*
- Nếu 1 đoạn SRT có thể cắt scene theo ≥2 cách hợp lý (Rule 3.5) và 2 cách lệch nhau nhiều về nhịp phim, nêu ngắn gọn lựa chọn còn lại lúc review thay vì tự chọn 1 cách rồi im lặng.
- Nếu mood/beat_type của 1 đoạn narration không rõ ràng, chọn mood trung tính gần nhất trong `mood_map` — không bịa 1 mood mạnh cho "an toàn" hoặc "kịch tính hơn".
- Nếu SRT/script nhắc tới nhân vật/địa điểm chưa có trong `config.json`, dừng lại và hỏi user bổ sung — không tự tạo character/setting mới giữa chừng Bước 2 hoặc 3.

### 2. Tối giản, bám sát nguồn

**Nội dung tối thiểu đúng với nguồn. Không suy diễn thêm.**

- Không tự thêm chi tiết ngoại hình, vật thể, thời tiết, hành động không có trong description/script (nguyên tắc gốc của Rule 1.1 và 4.3 — áp dụng khi viết cả scene-breakdown lẫn prompt).
- Không tự thêm character/setting/mood mới vào config nếu script không thật sự cần — mỗi entry thêm vào là 1 anchor phải giữ nhất quán suốt hàng trăm scene, thêm thừa là thêm rủi ro lệch.
- Không mở rộng cấu trúc `config.json` (thêm field, block mới) khi project không thực sự cần — ví dụ không tạo khối `era` nếu bối cảnh không thuộc thời kỳ cụ thể.
- Prompt dừng ở khoảng 35-55 từ khuyến nghị (Rule 4.4) — đủ 5 phần là đủ, không nhồi thêm mô tả "cho chắc".
- Khi sửa rule hoặc `export.py` để phòng ngừa 1 bug (Kaizen), chỉ sửa đúng phần liên quan — không nhân tiện viết lại cả rule file.

### 3. Sửa đúng chỗ

**Chỉ chạm đúng chỗ cần sửa. Chỉ dọn rác do chính mình tạo ra.**

- Gate hoặc user báo lỗi ở scene N → sửa đúng block scene N (Edit theo đoạn). Không Read rồi Write lại toàn bộ `scene-breakdown.md`/`prompts.md` để sửa 1 chỗ.
- Đổi 1 keyword setting/mood → chỉ áp dụng cho những scene đang dùng keyword đó. Không tiện tay chỉnh các scene khác đang đúng.
- Khi thêm rule mới do phát hiện bug (Kaizen mục 3), chỉ vá những scene ĐÃ SINH mà bug thực sự ảnh hưởng — không generate lại toàn bộ output "cho chắc ăn".
- Không tự ý sửa luôn các cảnh báo không liên quan trong cùng 1 lần sửa lỗi, trừ khi user yêu cầu dọn dẹp toàn bộ — mỗi lần sửa nên trace được về đúng 1 lỗi/yêu cầu cụ thể.
- Nếu lỗi nằm ở nền tảng và ảnh hưởng TOÀN BỘ output đã sinh (vd style anchor sai medium ngay từ Bước 1), báo user cân nhắc archive + chạy lại từ config đã sửa, thay vì patch tay hàng trăm prompt.

### 4. Làm đến khi máy xác nhận xong

**Định nghĩa tiêu chí xong. Lặp đến khi máy xác nhận.**

- `--qc` báo "Lỗi: 0" KHÔNG đồng nghĩa Bước 6 xong nếu còn cảnh báo chưa xử lý — mỗi cảnh báo phải được sửa hoặc ghi rõ lý do chấp nhận, không im lặng bỏ qua vì đã thấy PASS.
- Mục "QC định tính" cuối `qc-report.md` phải thực sự được điền (tick từng ý + verdict cụ thể) trước khi coi Bước 6 hoàn tất — checklist để trống = QC chưa xong, dù tầng máy đã PASS.
- Khi dùng batch/sub-agent song song (bắt buộc với >80 scene ở Bước 3, hoặc segment ở Bước 2), ràng buộc TOÀN CỤC xuyên suốt cả video (shot distribution Rule 4.2, rhythm Rule 3.2) phải được kiểm lại ở phiên chính sau khi gộp batch — không mặc định mỗi batch tự cân bằng cục bộ là đủ.
- Với việc lẻ ngoài pipeline (user báo bug, yêu cầu sửa nhỏ), nêu ngắn tiêu chí xong trước khi sửa (vd "xong ⟺ chạy lại `--qc`, cảnh báo liên quan biến mất"), rồi lặp đến khi đạt — cùng tinh thần với 4 lệnh gate chính.
- Không tự nhận "đã kiểm tra kỹ" nếu chưa chạy đúng lệnh gate tương ứng, kể cả khi thay đổi có vẻ nhỏ và an toàn.

---

**Các nguyên tắc này đang phát huy tác dụng nếu:** số cảnh báo trong `qc-report.md` giảm dần qua từng project (không chỉ số lỗi cứng); câu hỏi làm rõ (variant nào là timeline chính, mood nào phù hợp...) xuất hiện ở Bước 1-2 thay vì bị phát hiện muộn lúc QC; sửa lỗi chỉ đụng đúng scene/dòng liên quan; và `KAIZEN.md` không phải ghi lại 2 lần cùng 1 loại bug.

## Cấu trúc project

```
wmg-storyboard-prompt/
├── CLAUDE.md
├── KAIZEN.md                ← Nhật ký bug & phòng ngừa (bắt buộc cập nhật khi có lỗi mới)
├── .claude/rules/
│   ├── character.md
│   ├── visual-style.md
│   ├── beat-analysis.md
│   ├── prompt-structure.md
│   └── metadata.md
├── scripts/
│   └── export.py            ← Script Bước 4: gộp + validate metadata.json (KHÔNG dùng AI)
├── input/
│   ├── config.json          ← AI auto-fill từ SRT, user review + bổ sung
│   ├── script.txt           ← (Optional) Script gốc
│   └── subtitle.srt         ← File SRT có timestamp — INPUT CHÍNH
└── output/
    ├── character-refs.md    ← Prompt ảnh tham chiếu ASSET: nhân vật (Rule 1.4) + bối cảnh (Rule 2.3a) — Bước 1
    ├── scene-breakdown.md   ← Kết quả Bước 2 (bản đọc cho người)
    ├── prompts.md           ← Bộ prompt ảnh Bước 3 (TOÀN BỘ scene, kể cả hook)
    ├── video-prompts.md     ← Video prompt hook + copy image prompt (Bước 3, Rule 6.x)
    ├── metadata.json        ← File metadata cho ghép video (Bước 4 — do script sinh ra)
    ├── prompts-list.txt     ← (tùy chọn, Bước 5) prompt đánh số phẳng để copy chạy hàng loạt — `export.py --prompts-list`
    └── unix-batch-NN.txt    ← Bước 5: cú pháp Uni-X Studio, nhóm 100 ảnh/file — `export.py --unix-export`
```

## Cách sử dụng

1. Đặt file `subtitle.srt` vào `input/` (bắt buộc). Nếu có `script.txt` thì bỏ vào luôn.
2. Nói "chạy bước 1" → AI tự tạo `config.json` từ SRT (nano_name tự đặt theo tên nhân vật), bạn review + chốt `style`.
3. Nói "chạy bước 2", "chạy bước 3", "chạy bước 4", "chạy bước 5" lần lượt.
4. Hoặc nói "chạy toàn bộ pipeline" để chạy liên tục từ bước 1 → 5.
5. Output nằm trong `output/`.

---

## Pipeline — 6 Bước

### Bước 1: Project Setup

**Trigger:** "chạy bước 1", "setup project", "tạo config"

**Input:** `input/subtitle.srt` (bắt buộc), `input/script.txt` (optional)
**Output:** `input/config.json`

Quy trình:
1. Kiểm tra `input/subtitle.srt` tồn tại và đúng format. Thiếu → dừng, báo user.
2. Parse SRT → trích xuất: danh sách nhân vật (tên, tuổi, vai trò, ngoại hình), variant nhân vật (flashback), danh sách locations + keywords, timeline, tổng thời lượng.
3. Auto-fill `input/config.json` theo cấu trúc:

```json
{
  "project": {
    "title": "", "description": "", "total_duration": 0, "target_audience": "65+"
  },
  "style": "",
  "flashback_style": "soft warm vignette, slightly faded colors, dreamy atmosphere",
  "video_hook": {
    "enabled": false,
    "duration_s": 60,
    "max_clip_s": 8,
    "video_style": "photorealistic cinematic footage, 35mm film look, natural motion, smooth stabilized camera"
  },
  "era": {
    "name": "", "keywords": "", "wardrobe": "", "forbidden": []
  },
  "characters": [
    { "id": "", "name": "", "nano_name": "", "description": "" }
  ],
  "settings": [
    { "id": "", "name": "", "keywords": "" }
  ],
  "mood_map": {
    "nostalgic": "soft golden light, warm palette, slight gaussian blur",
    "tense": "cool blue-gray tones, hard shadows, tight framing",
    "hopeful": "morning light, open composition, warm highlights",
    "shock": "dramatic side lighting, shallow DOF, extreme close-up",
    "calm": "even soft lighting, neutral tones, balanced composition",
    "sad": "muted desaturated palette, overcast lighting, empty space",
    "determined": "strong directional light, firm posture, clear focus",
    "dismissive": "cold office light, distant framing, clinical atmosphere"
  }
}
```

4. Hỏi user review: xác nhận nhân vật, chọn `style` string, xác nhận locations, thêm/sửa mood nếu cần.
   - **`nano_name` tự đặt = chính tên nhân vật** (tên gọi ngắn trong truyện, vd "Jonah", "Clare"; variant quá khứ = "Young Jonah"). Đây là tên dùng trong mọi prompt ảnh/video khi nhân vật hoặc nhóm nhân vật đó xuất hiện — không cần user bổ sung tay.
   - **`description` mỗi nhân vật PHẢI mở đầu bằng danh từ giới tính + tuổi** (`[tuổi]-year-old man/woman/boy/girl`) trước nghề nghiệp/đặc điểm (Rule 1.1c) — thiếu danh từ giới tính thì ảnh ingredient dễ bị vẽ sai giới (vd nghề "mechanic" bị vẽ thành nữ). Gate `--step2` cảnh báo nếu thiếu.
   - **Chọn style BẮT BUỘC dứt khoát 1 medium** (Rule 2.1a): đưa user chọn giữa 2 preset — ảnh thật (`photorealistic cinematic film still, 35mm film look, natural skin texture, soft depth of field` — KHÔNG chứa lighting, lighting do mood_map quyết) hoặc tranh vẽ (`painterly digital illustration, cinematic composition, ...`). CẤM style trộn 2 medium kiểu `realistic illustration` — gây lỗi ảnh lúc thật lúc hư cấu.
   - Nhắc user: ảnh tham chiếu nhân vật (ingredients trong Flow) phải cùng medium với style đã chọn.
   - Nếu bối cảnh có thời kỳ cụ thể → điền khối `era` (Rule 2.5): style anchor kèm era aesthetic, character descriptions mặc đồ đúng thời kỳ, settings có marker niên đại, danh sách `forbidden` chống đồ vật hiện đại lọt vào prompt.
5. Lưu `input/config.json`.
6. Sau khi user chốt config: sinh **prompt ảnh tham chiếu (ingredient)** cho MỌI asset — lưu `output/character-refs.md`:
   - từng **nhân vật** (kể cả variant) theo template Rule 1.4;
   - từng **bối cảnh** trong `settings[]` theo template Rule 2.3a (ảnh nền trống, không người) — vì Bước 5 gắn asset tag cho cả setting (`[COURTROOM]`...), user cần ảnh bối cảnh để upload lên Uni-X.
   User dùng các prompt này tạo ảnh ingredient trong Flow/Uni-X TRƯỚC khi generate scene. Đặt tên ảnh đúng asset tag (nhân vật = nano_name, bối cảnh = `id` viết hoa).

**Validation:** config là valid JSON, có ≥1 character đủ 4 field, `style` không rỗng, có ≥1 setting đủ 3 field, `mood_map` có đủ mood cơ bản, `total_duration` khớp SRT.

---

### Bước 2: Beat Analysis

**Trigger:** "chạy bước 2", "phân tích nhịp dựng", "cắt scene"

**Input:** `input/subtitle.srt`, `input/config.json` (đã xác nhận)
**Output:** `output/scene-breakdown.md`

Quy trình:
1. Parse SRT → narrative liền mạch, giữ timestamp.
2. Phân tích macro structure (ACT, turning point, CTA) và micro structure (ranh giới đoạn, dialogue vs narration, cảm xúc mạnh).
3. Cắt scene theo Scene Splitting Criteria (Rule 3.5): thay đổi location, thời gian, nhân vật focus, mood, dialogue turn, hoặc vượt max duration.
4. Gán beat_type cho mỗi scene (Rule 3.1): establishing / dialogue / emotional_peak / tension / reflection / resolution.
5. Gán mood từ `config.json > mood_map`.
6. Trích xuất visual elements: characters (ID từ config), setting (ID từ config), key visual, gợi ý shot type.
6b. Điền cột `SFX`: 1-3 cụm keyword hiệu ứng âm thanh tiếng Anh cho editor tìm sfx (vd `rotary phone dialing, phone cord stretch`) — chỉ bám âm thanh CÓ THẬT trong narration/bối cảnh (nước chảy, ve sầu, máy kéo, phấn viết bảng...), không bịa; scene không có âm thanh đặc trưng → `-`. Cột này đi vào field `sfx` của metadata.json ở Bước 4.
7. Validate: duration trong min-max, không 4+ cùng beat type liên tiếp, không transition bị cấm, cắt tại ranh giới câu, không gap/overlap, mỗi 5-7 scene có ≥1 establishing/reflection.

**Quy tắc chống tràn context (BẮT BUỘC với video >20 phút):**
- Chia SRT thành **segment ~10 phút**, xử lý từng segment: đọc segment → cắt scene → **append ngay các dòng vào bảng trong `scene-breakdown.md`** → mới đọc segment tiếp theo. KHÔNG giữ toàn bộ bảng trong đầu rồi viết 1 lần.
- KHÔNG scene nào có `Dur(s) = 0`. Nếu 1 câu quá ngắn để đứng riêng → gộp vào scene liền kề.
- Trong cell `Description` và `Visual Notes` KHÔNG dùng ký tự `|` (phá vỡ bảng markdown, script không parse được).

**GATE kết thúc bước 2 (BẮT BUỘC — máy kiểm, không tự đánh giá):**

```bash
python3 scripts/export.py --step2
```

Gate kiểm: coverage đủ đến hết SRT, không Dur=0, không gap/overlap, beat_type hợp lệ, character ID có trong config, duration bounds, 4+ beat liên tiếp. **In ra FAIL → bước 2 CHƯA XONG**, phải sửa và chạy lại gate đến khi PASS. Không được chuyển sang bước 3 khi gate còn FAIL.

**Format output `scene-breakdown.md`:**

```markdown
# Scene Breakdown: [Title]
Total scenes: [N] | Total duration: [HH:MM:SS]

| STT | Start | End | Dur(s) | Beat Type | Mood | Characters | Description | Visual Notes | SFX |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 00:00:00 | 00:00:18 | 18 | dialogue | dismissive | marin, lydia | Lydia đưa hồ sơ cho Marin | Medium shot, bàn CEO | papers on desk, office room tone |

## Beat Distribution
- establishing: X (Y%)
- dialogue: X (Y%)
...
```

---

### Bước 3: Prompt Generation

**Trigger:** "chạy bước 3", "tạo prompt", "generate prompt"

**Input:** `input/config.json`, `output/scene-breakdown.md`
**Output:** `output/prompts.md` + (nếu `video_hook.enabled`) `output/video-prompts.md`

Quy trình:
1. Load từ config: style, flashback_style, characters[], settings[], mood_map.
2. Duyệt từng scene → compose prompt theo template 5 phần (Rule 4.1):
   ```
   [Characters + action], [Setting], [Shot type], [Mood keywords], [Style anchor]
   ```
   - Phần 1: dùng `nano_name` từ config, action từ description.
   - Phần 2: dùng `keywords` từ settings[] trong config.
   - Phần 3: chọn shot type + lens theo bảng Rule 4.8 (vd `medium shot, 50mm lens`), kiểm tra distribution (Rule 4.2); close-up có mặt người → thêm `full head within frame`.
   - Phần 4: tra `mood_map` → lấy visual keywords.
   - Phần 5: copy nguyên văn `style`. Flashback → append `flashback_style`.
3. Validate từng prompt: đúng 5 phần, 20-75 từ, không text/chữ, không mâu thuẫn narration, đúng nano_name, ≤3 nhân vật, đúng setting keywords, đúng mood keywords, style nguyên vẹn.
4. Kiểm tra shot type distribution trong mỗi cụm 10 scene (Rule 4.2).

**Video Hook (khi `video_hook.enabled = true`):** sau khi xong prompts.md, sinh thêm `output/video-prompts.md` theo Rule 6.1→6.7 (file `.claude/rules/video-prompt.md`). Mục tiêu: hook ~1 phút (`duration_s` mặc định 60) cảm xúc CỰC MẠNH, **mỗi clip là 1 CÚ CẮT sang cảnh khác (hard cut, ảnh riêng)** — clip .1 dùng ảnh scene (copy nguyên văn image prompt), mỗi clip .k là 1 ảnh phụ `[stt]-[k].jpg` cắt sang shot/chủ thể/scale mới; CẤM Extend tua chậm cùng khung. Chuỗi clip leo thang như trailer. Video prompt mô tả camera motion + 1 chuyển động, KHÔNG dialogue.

**Quy tắc chống tràn context (BẮT BUỘC với >40 scenes):**
- Tạo prompt theo **batch 25-30 scenes**: đọc đúng đoạn tương ứng trong `scene-breakdown.md` → viết prompts → **append ngay vào `prompts.md`** → mới sang batch tiếp.
- Với >80 scenes: dùng **sub-agent song song**, mỗi sub-agent nhận 1 batch + config + đoạn scene-breakdown tương ứng, ghi ra file tạm `output/prompts-batch-N.md`; phiên chính chỉ nối các file lại (dùng lệnh `cat`, không đọc nội dung vào context).
**GATE kết thúc bước 3 (BẮT BUỘC — máy kiểm, không tự đánh giá):**

```bash
python3 scripts/export.py --step3
```

Gate kiểm: đủ prompt cho mọi scene (không thiếu, không thừa), style anchor nguyên văn trong từng prompt, độ dài 20-75 từ. **In ra FAIL → bước 3 CHƯA XONG**, sửa và chạy lại đến khi PASS.

**Format output `prompts.md`:**

```markdown
# Prompt Set: [Title]
Style: [style string] | Total prompts: [N]

---
## 1
**Beat:** dialogue | **Mood:** dismissive | **Duration:** 18s
**Characters:** Marin, Lydia
**Prompt:**
Marin sitting behind a large mahogany desk, Lydia standing opposite...
```

---

### Bước 4: Export (CHẠY SCRIPT — AI KHÔNG viết metadata.json tay)

**Trigger:** "chạy bước 4", "export", "xuất metadata"

**Input:** `input/config.json`, `output/scene-breakdown.md`, `output/prompts.md`
**Output:** `output/metadata.json`

Quy trình:
1. Chạy lệnh duy nhất:

```bash
python3 scripts/export.py
```

Script tự động: parse scene-breakdown + prompts + config → sinh `output/metadata.json` → validate toàn bộ Rules 5.1→5.8 (stt liên tục, no gap/overlap, duration_s tính từ timestamp, timestamp HH:MM:SS, character IDs tồn tại trong config, image_file khớp stt, đủ required fields, valid JSON) → in báo cáo beat distribution + PASS/FAIL. Mỗi scene trong metadata kèm field `sfx` (mảng keyword, đọc từ cột SFX của scene-breakdown) để editor tìm hiệu ứng âm thanh cho phân cảnh.

2. Script báo LỖI → AI đọc danh sách lỗi, sửa file nguồn tương ứng (`scene-breakdown.md` hoặc `prompts.md`), chạy lại script. LẶP đến khi PASS. TUYỆT ĐỐI KHÔNG sửa trực tiếp `metadata.json` — nó là file sinh ra, sửa nguồn.
3. Script PASS → AI chỉ review checklist định tính: character consistency, visual consistency, rhythm quality, prompt quality.
4. Chế độ kiểm tra nhanh không ghi file: `python3 scripts/export.py --validate`

**Lý do:** metadata.json ~100KB+; để AI viết tay từng ký tự vừa chậm (hàng chục nghìn token), vừa dễ sai số học, vừa ngốn context. Script chạy ~1 giây và bắt được lỗi mà mắt người bỏ sót.

---

### Bước 5: Xuất Uni-X Prompts (CHẠY SCRIPT — AI không viết tay)

**Trigger:** "chạy bước 5", "xuất unix", "xuất Uni-X prompts"

**Input:** `output/metadata.json` (Bước 4 đã PASS) | **Output:** `output/unix-batch-NN.txt` (+ tùy chọn `output/prompts-list.txt`)

Quy trình:
1. Chạy `python3 scripts/export.py --unix-export` → sinh `unix-batch-NN.txt` theo cú pháp Uni-X Studio: mỗi ảnh gồm header `(Image Prompt i/n)`, dòng `Assets: TAG1, TAG2`, dòng `Prompt: ...` có gắn `[TAG]` tại đúng vị trí nhân vật/bối cảnh. Tự chia nhóm tối đa 100 ảnh/file theo giới hạn 1 lượt vẽ của Uni-X.
2. Asset tag = `nano_name`/setting `id` viết hoa, khoảng trắng thành `_` (vd `Owen Consultant` → `OWEN_CONSULTANT`, setting `conference_room_7f` → `CONFERENCE_ROOM_7F`) — khi upload ảnh ingredient lên Uni-X, đặt tên đúng theo quy ước này.
3. Script cảnh báo "N scene không xác định được setting" → PHẢI rà danh sách: cận cảnh chi tiết hoặc không gian phụ xuất hiện 1 lần (không có entry trong settings[]) là chấp nhận được; nhưng scene toàn/trung cảnh ở location đã define mà thiếu tag nghĩa là cụm bối cảnh trong prompt lệch với cụm đầu của `settings[].keywords` — sửa config hoặc prompt cho khớp (xem KAIZEN 2026-07-06 và Rule 4.1 Phần 2).
4. Tùy chọn: `python3 scripts/export.py --prompts-list` → `output/prompts-list.txt`: toàn bộ prompt đánh số `1. ...` `2. ...`, cách nhau 1 dòng trống, không kèm metadata — copy thẳng để chạy hàng loạt ở công cụ khác.

Cả hai đều đọc từ `metadata.json` đã validate — chạy lại bất cứ lúc nào; nếu nguồn thay đổi (prompts/scene-breakdown/config) thì chạy lại Bước 4 rồi Bước 5. CHỈ đem file đi vẽ hàng loạt sau khi Bước 6 QC PASS.

---

### Bước 6: QC (BẮT BUỘC trước khi giao prompt sang Flow/Uni-X)

**Trigger:** "chạy QC", "QC", "kiểm định chất lượng"

**Input:** toàn bộ output các bước trước | **Output:** `output/qc-report.md`

Quy trình (chi tiết trong `.claude/rules/qc.md`):
1. **Tầng máy:** `python3 scripts/export.py --qc` — gộp mọi gate + kiểm character lock (nano_name), mood keywords verbatim, flashback style, chống trùng lặp prompt, shot variety mỗi 10 scene. LỖI → sửa nguồn → chạy lại đến PASS.
2. **Tầng định tính:** AI đọc theo checklist trong qc-report.md — đọc TOÀN BỘ hook (image + video prompt, đối chiếu SRT), mood arc toàn bảng, sample ≥10 scene giữa bài kiểm khớp narration + visual state + era. Ghi verdict vào cuối qc-report.md.
3. QC xong ⟺ tầng máy PASS + verdict định tính PASS.

**Khuyến nghị phân vai model:** bước 2-3 (sản xuất) chạy model nhỏ để tiết kiệm; bước QC định tính chạy model mạnh hoặc phiên riêng — người review chỉ cần đọc `qc-report.md`.

---

## Quy tắc Kaizen (BẮT BUỘC — chống lặp lỗi)

Bất cứ khi nào phát hiện 1 bug — do user báo, gate FAIL vì lỗi loại mới, hay QC định tính tìm ra — AI PHẢI TỰ ĐỘNG (không cần user nhắc):

1. **Ghi ngay vào `KAIZEN.md`** theo template trong file: hiện tượng → gốc rễ → phòng ngừa.
2. **Codify phòng ngừa vào hệ thống:** sửa/thêm rule trong `.claude/rules/` và (nếu máy kiểm được) thêm check vào `scripts/export.py`. Entry kaizen phải ghi rõ rule/gate nào phòng ngừa; nếu chưa tự động hóa được → ghi "CHƯA CÓ — cần bổ sung".
3. **Vá dữ liệu hiện tại** của project đang chạy nếu bug ảnh hưởng output đã sinh.

Khi bắt đầu debug bất kỳ lỗi nào: đọc `KAIZEN.md` TRƯỚC — nếu lỗi đã có entry thì áp dụng phòng ngừa sẵn có thay vì tìm lại từ đầu.

---

## Quy tắc phiên làm việc & bộ nhớ (context)

1. **Mỗi bước 1 phiên chat mới.** Toàn bộ dữ liệu giữa các bước nằm trong file — không cần lịch sử hội thoại. Chạy xong 1 bước với video dài → khuyên user mở phiên mới cho bước tiếp.
2. **Không đọc lại file output đã viết** để "kiểm tra" — dùng script/lệnh đếm (grep, wc, export.py) thay vì nạp cả file vào context.
3. **Khi "chạy toàn bộ pipeline"** với video >20 phút: vẫn chạy tuần tự nhưng áp dụng nghiêm các quy tắc segment/batch ở bước 2-3; nếu context gần đầy → dừng ở ranh giới bước, báo user mở phiên mới (dữ liệu đã an toàn trong file).
4. **Dấu hiệu đã từng tràn context:** scene-breakdown dừng giữa chừng (End cuối bảng < duration SRT), scene Dur=0, tổng duration khai báo ≠ tổng cộng thực. `export.py` sẽ bắt các lỗi này.
5. **Nguyên tắc gate:** AI KHÔNG tự tuyên bố "bước X đã xong". Chỉ có 5 lệnh sau mới quyết định:
   - Bước 2 xong ⟺ `python3 scripts/export.py --step2` → PASS
   - Bước 3 xong ⟺ `python3 scripts/export.py --step3` → PASS
   - Bước 4 xong ⟺ `python3 scripts/export.py` → PASS
   - Bước 5 xong ⟺ `python3 scripts/export.py --unix-export` chạy thành công + danh sách "scene không xác định được setting" (nếu có) đã được rà và chấp nhận/sửa
   - Bước 6 xong ⟺ `python3 scripts/export.py --qc` → PASS + verdict định tính PASS trong qc-report.md
   Nếu phiên bị ngắt/tràn giữa chừng, phiên mới chỉ cần chạy các lệnh trên là biết chính xác đang dở ở đâu và thiếu gì.
