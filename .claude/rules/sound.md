# Rule: Sound Extraction (Bước 3)

Quy tắc trích keyword hiệu ứng âm thanh (SFX) cho editor tìm sound lúc dựng. Đây là bước RIÊNG, chạy SAU Beat Analysis (Bước 2) và TRƯỚC Prompt Generation (Bước 4).

**Bản chất:** SFX KHÔNG phải phân tích waveform của file audio. Đây là AI đọc `description`/bối cảnh của từng scene trong `scene-breakdown.md` rồi **suy ra âm thanh nhìn-thấy-được đáng lẽ phải có** trong cảnh đó, viết thành keyword tiếng Anh để editor gõ vào thư viện sfx (Epidemic, Artlist...) mà tìm. Nguồn dữ liệu duy nhất = `scene-breakdown.md`. Không đọc lại prompts.md (chưa có ở bước này).

## 8.1 — Điều kiện tiên quyết: Beat phải xong

- Bước 3 chỉ chạy khi `output/scene-breakdown.md` tồn tại VÀ `--step2` đã PASS.
- Thiếu scene-breakdown → **DỪNG, báo "THIẾU BEAT: chạy Bước 2 trước"**. Không tự bịa scene để gán âm thanh.
- Beat có nhưng `--step2` còn FAIL → sửa Bước 2 cho PASS rồi mới làm SFX (số scene/stt còn có thể đổi).

## 8.2 — Chỉ âm thanh DIEGETIC có thật

Chỉ ghi âm thanh **thực sự phát ra trong khung cảnh** đó, suy được từ narration/bối cảnh:

- ✅ Có trong cảnh: điện thoại reo, cửa đóng, mưa rơi, xe kéo nổ máy, phấn viết bảng, ve sầu, nước chảy, bước chân trên sỏi.
- ❌ CẤM nhạc nền / score / cảm xúc: `tense music`, `sad piano`, `dramatic score` — đó là việc của editor phối nhạc, không phải sfx của cảnh.
- ❌ CẤM bịa âm thanh không có căn cứ trong cảnh. Không suy diễn thêm (bám nguồn — cùng tinh thần Rule 4.3).
- Scene không có sự kiện âm thanh đáng ghi → `keywords: []` (mảng rỗng tường minh), KHÔNG bỏ trống entry. **Đây là trường hợp MẶC ĐỊNH của đa số scene** (Rule 8.9) — nhạc nền và không khí chung là việc của editor, không phải của sfx.json.
- Room tone/ambience (`courtroom murmur`, `quiet room ambience`...) CHỈ dùng khi cảnh thật sự cần một lớp nền đặc trưng khác biệt (phiên tòa ồn ào, hầm nhà thờ sau bữa tối...) — KHÔNG phải mặc định cho mọi scene tĩnh.

## 8.3 — Keyword phải "tìm được trên thư viện sfx"

- Dùng **cụm danh từ + hành động cụ thể** mà editor gõ là ra kết quả: `rotary phone dialing` ✅ chứ không phải `phone sound` ❌; `gravel footsteps approaching` ✅ chứ không `walking` ❌.
- Tiếng Anh, viết thường, 1-3 cụm/scene. Nhiều hơn 3 là nhồi — chọn âm thanh đặc trưng nhất.
- Vật liệu/hành động cụ thể cho tiếng chuẩn: `heavy wooden door slam` hơn `door`, `diesel tractor engine idling` hơn `engine`.

## 8.4 — Phủ đủ mọi scene (coverage)

- MỌI scene (theo stt trong scene-breakdown) PHẢI có 1 entry trong `sfx.json` — kể cả scene im lặng (`keywords: []`). Đây là bằng chứng AI đã cân nhắc từng scene, không bỏ sót.
- Gate `--step3` báo LỖI nếu: thiếu entry cho scene nào, entry trỏ stt không tồn tại, trùng stt, hoặc `keywords` không phải mảng.

## 8.5 — Output: `output/sfx.json`

AI-sinh (như scene-breakdown/prompts) → nằm ở `output/`, KHÔNG phải `input/`. Bước 5 (`export.py`) merge field `sfx` vào từng scene của `metadata.json` theo stt. Sửa âm thanh = sửa `output/sfx.json` rồi chạy lại Bước 5, KHÔNG sửa tay `metadata.json`.

Schema:

```json
{
  "sfx": [
    { "stt": 1, "keywords": ["rotary phone dialing", "phone cord stretch"] },
    { "stt": 2, "keywords": ["office room tone"] },
    { "stt": 3, "keywords": [] }
  ]
}
```

## 8.6 — Gate kết thúc Bước 3

```bash
python3 scripts/export.py --step3
```

Gate kiểm: beat đã PASS (else THIẾU BEAT), `sfx.json` tồn tại + JSON hợp lệ, phủ đủ mọi scene, không stt lạ/trùng, `keywords` là mảng, KHÔNG âm đánh chữ/gõ phím ngoài cảnh diegetic (8.7 — LỖI), không 1 keyword phủ áp đảo/lặp liên tiếp (8.8), mật độ điểm nhấn ~15-40% — >75% scene có keyword là LỖI FULL-COVERAGE (8.9). **FAIL → Bước 3 CHƯA XONG.** Không chuyển sang Bước 4 khi gate còn FAIL.

## 8.7 — CẤM âm đánh chữ/gõ phím trong sfx (âm đó thuộc hiệu ứng typewriter) — QUAN TRỌNG

Bug thực tế 2026-07-22: video dựng ra toàn tiếng gõ phím — vang cả ở đoạn không có chữ, lệch thời gian với chữ đang gõ.

- Âm gõ phím của hiệu ứng đánh chữ là tài sản của **CUE typewriter** (`input/typewriter.json` → `typewriter-cues.md`): editor đặt âm bắt đầu tại đúng `at` của cue, dừng sau `type_s` giây (script tính từ độ dài text) — **1 nguồn thời gian duy nhất nên chữ và âm không thể lệch nhau**.
- `sfx.json` KHÔNG BAO GIỜ chứa `typewriter / typing / keyboard / keystroke / key clack` — kể cả ở scene CÓ cue typewriter (âm đã đi kèm cue, ghi thêm vào sfx là nhân đôi tiếng gõ).
- Ngoại lệ DUY NHẤT: trong CẢNH thật sự có máy đánh chữ/bàn phím đang được gõ (description scene nói rõ) — khi đó là âm diegetic bình thường.
- Gate `--step3` quét và báo LỖI cứng; `typewriter-cues.md` sinh ra kèm khối "QUY TẮC ÂM THANH ĐÁNH CHỮ" cho editor.

## 8.8 — Đa dạng + hợp mood

- KHÔNG để 1 keyword phủ áp đảo toàn video. Gate `--step3`: 1 keyword ở >25% scene có âm → cảnh báo; >50% → LỖI; lặp 4+ scene liên tiếp → cảnh báo. Room tone phải đổi theo location (`farm store room tone` ≠ `quiet kitchen room tone` ≠ `courtroom murmur`).
- Hợp mood — vẫn PHẢI là âm diegetic có thật trong cảnh (8.2); mood chỉ quyết định **chọn âm nào** trong số âm hợp lệ và **chất âm** khi mô tả:

| Mood của scene | Thiên về chọn âm trong cảnh |
|---|---|
| tense / shock | âm gọn, sắc, đơn lẻ: heavy door slam, hurried footsteps, paper crumple |
| sad / nostalgic | âm mềm, thưa, xa: soft rain on window, distant wind, slow clock ticking |
| calm / hopeful | ambience mềm liên tục: morning birdsong, gentle breeze through leaves |
| determined | âm lao động chắc nhịp: mallet striking stake, spade cutting soil |

- Không bịa âm để "cho hợp mood" — cảnh không có căn cứ trong narration/description thì để `[]`.

## 8.9 — SFX là ĐIỂM NHẤN đặt đúng chỗ, KHÔNG phải lớp phủ toàn video (QUAN TRỌNG)

Bug thực tế 2026-07-22: Bước 3 tạo keyword cho **186/186 scene** — full coverage. Mục đích thật của sfx là **tăng cảm xúc tại đúng khoảnh khắc**: nội dung có tiếng gió thì có sfx gió, có chuông thì có tiếng chuông — với tỉ lệ vừa phải. Rải âm mọi scene làm editor ngập trong keyword và video ồn như phim tài liệu tự nhiên, trong khi đây là video kể chuyện có narration + nhạc nền phủ suốt.

- **Tỉ lệ kỳ vọng: ~15–40% scene có keyword** (video 33 phút / ~186 scene → khoảng 30–75 điểm nhấn, tức 1–2 điểm nhấn/phút). Gate `--step3`: >50% → cảnh báo; **>75% → LỖI FULL-COVERAGE**.
- **Tiêu chí CHỌN scene điểm nhấn** (thỏa ≥1):
  1. Narration/description có **sự kiện âm thanh cụ thể** (búa gõ, cổng mở, chuông, mưa, đàn thú tràn xuống, điện thoại, phong bì xé) — đặc biệt khi narration TỰ nhắc tới âm thanh.
  2. Khoảnh khắc **cảm xúc cần nhấn**: emotional_peak, cú mở hook, chuyển hồi/chuyển mùa.
  3. **Motif âm thanh lặp của truyện** (vd chiếc chuông đồng) — giữ trọn chuỗi để editor dùng cùng 1 file âm.
- Scene chỉ "có thể có tiếng nền chung chung" → `[]`. Số đông entry là `[]` là dấu hiệu làm ĐÚNG, không phải thiếu sót.
- Âm gõ chữ vẫn theo cơ chế riêng: đi kèm cue typewriter tại `at` + `type_s` (Rule 8.7) — tự động "có chữ thì có tiếng gõ, không chữ thì không".
