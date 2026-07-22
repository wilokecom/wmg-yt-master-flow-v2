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

Các Rule trong `.claude/rules/` quy định NỘI DUNG đúng là gì (character nào, style nào, duration bao nhiêu...). Các SKILL trong `.claude/skills/` quy định QUY TRÌNH từng bước. Mục này quy định CÁCH LÀM VIỆC chung — áp dụng xuyên suốt Bước 1-7 và cả khi sửa lỗi ngoài pipeline.

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

- `--qc` báo "Lỗi: 0" KHÔNG đồng nghĩa Bước 7 xong nếu còn cảnh báo chưa xử lý — mỗi cảnh báo phải được sửa hoặc ghi rõ lý do chấp nhận, không im lặng bỏ qua vì đã thấy PASS.
- Mục "QC định tính" cuối `qc-report.md` phải thực sự được điền (tick từng ý + verdict cụ thể) trước khi coi Bước 7 hoàn tất — checklist để trống = QC chưa xong, dù tầng máy đã PASS.
- Khi dùng batch/sub-agent song song (bắt buộc với >80 scene ở Bước 4, hoặc segment ở Bước 2), ràng buộc TOÀN CỤC xuyên suốt cả video (shot distribution Rule 4.2, rhythm Rule 3.2) phải được kiểm lại ở phiên chính sau khi gộp batch — không mặc định mỗi batch tự cân bằng cục bộ là đủ.
- Với việc lẻ ngoài pipeline (user báo bug, yêu cầu sửa nhỏ), nêu ngắn tiêu chí xong trước khi sửa (vd "xong ⟺ chạy lại `--qc`, cảnh báo liên quan biến mất"), rồi lặp đến khi đạt — cùng tinh thần với các lệnh gate chính.
- Không tự nhận "đã kiểm tra kỹ" nếu chưa chạy đúng lệnh gate tương ứng, kể cả khi thay đổi có vẻ nhỏ và an toàn.

---

**Các nguyên tắc này đang phát huy tác dụng nếu:** số cảnh báo trong `qc-report.md` giảm dần qua từng project (không chỉ số lỗi cứng); câu hỏi làm rõ (variant nào là timeline chính, mood nào phù hợp...) xuất hiện ở Bước 1-2 thay vì bị phát hiện muộn lúc QC; sửa lỗi chỉ đụng đúng scene/dòng liên quan; và `KAIZEN.md` không phải ghi lại 2 lần cùng 1 loại bug.

## Cấu trúc project

```
wmg-storyboard-prompt/
├── README.md                ← Hướng dẫn tổng quan cho NGƯỜI DÙNG (input/output/luồng chạy)
├── CLAUDE.md                ← Router + nguyên tắc chung cho AI (file này)
├── KAIZEN.md                ← Nhật ký bug & phòng ngừa (bắt buộc cập nhật khi có lỗi mới)
├── .claude/
│   ├── skills/              ← QUY TRÌNH từng bước — mỗi bước 1 skill đơn nhiệm
│   │   ├── step1-setup/     ← Bước 1: config.json + character-refs.md
│   │   ├── step2-beat/      ← Bước 2: cắt scene (có MỤC TIÊU SỐ chống cắt thô)
│   │   ├── step3-sound/     ← Bước 3: sfx.json
│   │   ├── step4-prompts/   ← Bước 4: prompts.md + video-prompts.md
│   │   ├── step5-export/    ← Bước 5: metadata.json (script làm)
│   │   ├── step6-unix/      ← Bước 6: unix-batch-NN.txt (script làm)
│   │   ├── step7-qc/        ← Bước 7: QC 2 tầng
│   │   └── pipeline/        ← Điều phối chạy tuần tự 1 → 7
│   └── rules/               ← NỘI DUNG đúng là gì (skill tham chiếu vào đây)
│       ├── character.md
│       ├── visual-style.md
│       ├── beat-analysis.md
│       ├── sound.md
│       ├── prompt-structure.md
│       ├── video-prompt.md
│       ├── metadata.md
│       └── qc.md
├── scripts/
│   └── export.py            ← Gates máy + export metadata/Uni-X (KHÔNG dùng AI)
├── input/
│   ├── config.example.json  ← TEMPLATE gốc do user quản — dự án mới copy thành config.json; pipeline CHỈ ĐỌC, không sửa
│   ├── config.json          ← Sinh từ config.example.json ở Bước 1, AI auto-fill từ SRT, user review + chốt
│   ├── script.txt           ← (Optional) Script gốc
│   ├── subtitle.srt         ← File SRT có timestamp — INPUT CHÍNH
│   └── typewriter.json      ← (Optional) Cue đánh máy — nguồn duy nhất, Bước 5 merge
└── output/
    ├── character-refs.md    ← Bước 1: prompt ảnh ref nhân vật + bối cảnh (format `### TAG` + code block)
    ├── character-refs-list.txt ← Bước 1: prompt ref đánh số để vẽ hàng loạt — `--refs-list`
    ├── character-refs-map.txt  ← Bước 1: map `N -> TAG.jpg` đổi tên ảnh sau khi vẽ — `--refs-list`
    ├── scene-breakdown.md   ← Bước 2: bảng phân cảnh
    ├── sfx.json             ← Bước 3: keyword âm thanh mỗi scene (nguồn AI-sinh)
    ├── sfx-timeline.json    ← Bước 3: MODULE SFX ĐỘC LẬP (timestamp+keywords+mood) — `--sfx-export`, mang đi dùng không cần Bước 4/5
    ├── prompts.md           ← Bước 4: bộ prompt ảnh
    ├── video-prompts.md     ← Bước 4: video prompt hook (nếu bật)
    ├── metadata.json        ← Bước 5: script sinh — CẤM sửa tay
    ├── typewriter-cues.md   ← Bước 5: script sinh — CẤM sửa tay
    ├── qc-report.md         ← Bước 7: report máy + verdict định tính
    ├── prompts-list.txt     ← Bước 6 (tùy chọn): --prompts-list
    └── unix-batch-NN.txt    ← Bước 6: --unix-export
```

## Pipeline — 7 Bước (chi tiết nằm trong SKILL, không làm từ trí nhớ)

**Mỗi bước là 1 skill đơn nhiệm.** Khi user gọi 1 bước, PHẢI mở skill tương ứng (Skill tool / đọc `.claude/skills/<tên>/SKILL.md`) và làm theo đúng nội dung — KHÔNG tự làm theo trí nhớ hay đọc lướt. Skill nhận input từ file do bước trước sinh ra, trả kết quả ra file — không phụ thuộc lịch sử hội thoại.

| Bước | Trigger của user | Skill | Input → Output | Gate xác nhận xong |
|---|---|---|---|---|
| 1. Setup | "chạy bước 1", "tạo config" | `step1-setup` | subtitle.srt → config.json + character-refs.md + refs-list/map | `--step1` PASS + `--refs-list` OK + user chốt config |
| 2. Beat | "chạy bước 2", "cắt scene" | `step2-beat` | subtitle.srt + config → scene-breakdown.md | `--step2` PASS |
| 3. Sound | "chạy bước 3", "trích sfx" | `step3-sound` | scene-breakdown → sfx.json + sfx-timeline.json | `--step3` PASS + `--sfx-export` OK |
| 4. Prompts | "chạy bước 4", "tạo prompt" | `step4-prompts` | scene-breakdown + config → prompts.md (+ video-prompts.md) | `--step4` PASS |
| 5. Export | "chạy bước 5", "export" | `step5-export` | các file trên → metadata.json | `export.py` PASS |
| 6. Uni-X | "chạy bước 6", "xuất unix" | `step6-unix` | metadata.json → unix-batch-NN.txt | `--unix-export` OK + rà scene không-tag |
| 7. QC | "chạy QC" | `step7-qc` | toàn bộ output → qc-report.md | `--qc` PASS + verdict định tính |
| Toàn bộ | "chạy toàn bộ pipeline" | `pipeline` | chạy tuần tự 1 → 7 | từng gate theo thứ tự |

### LOOP ENGINE — giao ước chung của mọi skill (chống bỏ bước, làm thiếu, tự tuyên bố xong)

Mọi skill đều theo cùng 1 khung, bất kể model nào thực thi:

1. **Pre-flight**: kiểm input của bước tồn tại + gate bước trước PASS. Thiếu → DỪNG, báo user (không tự bịa dữ liệu).
2. **Mục tiêu số**: tính con số kiểm chứng được TRƯỚC khi làm (vd Bước 2: số scene tối thiểu = ⌈SRT/25⌉, kỳ vọng ≈ SRT/12) và in ra cho user.
3. **Làm việc** theo thuật toán trong SKILL.md (segment/batch khi video dài).
4. **Gate**: chạy lệnh gate của bước → FAIL: đọc từng dòng lỗi, sửa đúng chỗ trong file NGUỒN, chạy lại. PASS còn cảnh báo: xử lý từng cảnh báo hoặc ghi lý do chấp nhận. Lặp đến khi sạch.
5. **Ngắt an toàn**: sau 5 vòng cùng 1 lỗi không giảm → DỪNG, báo user kèm danh sách lỗi. CẤM: nới/tắt check trong `export.py`, sửa file output do script sinh, sinh nội dung bằng vòng lặp script thay vì làm thật — chỉ để gate xanh.
6. **Trả kết quả**: báo user con số thực tế vs mục tiêu + dòng PASS của gate + bước tiếp theo.

## Cách sử dụng

1. Đặt `subtitle.srt` vào `input/` (bắt buộc; tên khác → đổi thành `subtitle.srt`). Có `script.txt` thì bỏ vào luôn.
2. Nói "chạy bước 1" → AI theo skill `step1-setup`: archive config cũ (nếu là project trước) → copy `config.example.json` → `config.json` → auto-fill từ SRT → bạn review + chốt `style`. Template `config.example.json` không bao giờ bị pipeline sửa.
3. Nói "chạy bước 2" → 3 → 4 → 5 → 6 → "chạy QC" lần lượt (mỗi bước 1 phiên mới với video dài).
4. Hoặc nói "chạy toàn bộ pipeline" → AI theo skill `pipeline`.
5. Output nằm trong `output/`. CHỈ đem prompt đi vẽ hàng loạt sau khi Bước 7 QC PASS.
6. **Chế độ SFX-only** (chỉ cần âm thanh cho 1 kịch bản, không làm ảnh): Bước 1 (chốt config, BỎ QUA character-refs) → Bước 2 → Bước 3 → cầm `output/sfx-timeline.json` đi dùng. File tự đủ (timestamp cùng timeline SRT/voiceover), thả vào folder dựng video khác là khớp — không cần Bước 4-7.

**Khuyến nghị phân vai model:** bước 2-4 (sản xuất) chạy model nhỏ để tiết kiệm; QC định tính (Bước 7) chạy model mạnh hoặc phiên riêng. Gate máy + skill đơn nhiệm được thiết kế để model nào cũng ra cùng chuẩn — model yếu cắt sai độ hạt sẽ bị `--step2` chặn LỖI CỨNG (GRANULARITY, KAIZEN 2026-07-22).

## Quy tắc Kaizen (BẮT BUỘC — chống lặp lỗi)

Bất cứ khi nào phát hiện 1 bug — do user báo, gate FAIL vì lỗi loại mới, hay QC định tính tìm ra — AI PHẢI TỰ ĐỘNG (không cần user nhắc):

1. **Ghi ngay vào `KAIZEN.md`** theo template trong file: hiện tượng → gốc rễ → phòng ngừa.
2. **Codify phòng ngừa vào hệ thống:** sửa/thêm rule trong `.claude/rules/`, cập nhật skill trong `.claude/skills/` nếu quy trình đổi, và (nếu máy kiểm được) thêm check vào `scripts/export.py`. Entry kaizen phải ghi rõ rule/gate/skill nào phòng ngừa; nếu chưa tự động hóa được → ghi "CHƯA CÓ — cần bổ sung".
3. **Vá dữ liệu hiện tại** của project đang chạy nếu bug ảnh hưởng output đã sinh.

Khi bắt đầu debug bất kỳ lỗi nào: đọc `KAIZEN.md` TRƯỚC — nếu lỗi đã có entry thì áp dụng phòng ngừa sẵn có thay vì tìm lại từ đầu.

## Quy tắc phiên làm việc & bộ nhớ (context)

1. **Mỗi bước 1 phiên chat mới.** Toàn bộ dữ liệu giữa các bước nằm trong file — không cần lịch sử hội thoại. Chạy xong 1 bước với video dài → khuyên user mở phiên mới cho bước tiếp.
2. **Không đọc lại file output đã viết** để "kiểm tra" — dùng script/lệnh đếm (grep, wc, export.py) thay vì nạp cả file vào context.
3. **Khi "chạy toàn bộ pipeline"** với video >20 phút: vẫn chạy tuần tự nhưng áp dụng nghiêm quy tắc segment/batch trong skill bước 2 và 4; nếu context gần đầy → dừng ở ranh giới bước, báo user mở phiên mới (dữ liệu đã an toàn trong file).
4. **Dấu hiệu đã từng tràn context:** scene-breakdown dừng giữa chừng (End cuối bảng < duration SRT), scene Dur=0, tổng duration khai báo ≠ tổng cộng thực. `export.py` sẽ bắt các lỗi này.
5. **Nguyên tắc gate:** AI KHÔNG tự tuyên bố "bước X đã xong". Chỉ các lệnh sau mới quyết định:
   - Bước 1 xong ⟺ user chốt `config.json` + `python3 scripts/export.py --step1` → PASS (đủ ref asset) + `--refs-list` OK (list vẽ hàng loạt khớp số asset)
   - Bước 2 xong ⟺ `python3 scripts/export.py --step2` → PASS
   - Bước 3 xong ⟺ `python3 scripts/export.py --step3` → PASS (SFX phủ đủ scene; cần beat xong trước)
   - Bước 4 xong ⟺ `python3 scripts/export.py --step4` → PASS
   - Bước 5 xong ⟺ `python3 scripts/export.py` → PASS
   - Bước 6 xong ⟺ `python3 scripts/export.py --unix-export` chạy thành công + danh sách "scene không xác định được setting" (nếu có) đã được rà và chấp nhận/sửa
   - Bước 7 xong ⟺ `python3 scripts/export.py --qc` → PASS + verdict định tính PASS trong qc-report.md
   Nếu phiên bị ngắt/tràn giữa chừng, phiên mới chỉ cần chạy các lệnh trên là biết chính xác đang dở ở đâu và thiếu gì.
