# KAIZEN — Nhật ký lỗi & cải tiến

Mục đích: mọi bug phát hiện được (do user, gate, hay QC) PHẢI ghi vào đây để không lặp lại. Quy tắc: mô tả ngắn — gốc rễ — cách phòng ngừa đã đưa vào hệ thống (rule/gate nào). Bug chưa có phòng ngừa tự động = việc còn nợ.

**Template entry:**

```
## [YYYY-MM-DD] Tên bug ngắn gọn
- **Hiện tượng:** ...
- **Gốc rễ:** ...
- **Phòng ngừa:** Rule X.Y + gate `lệnh` (hoặc "CHƯA CÓ — cần bổ sung")
```

---

## [2026-07-08] Gate shot_cat đếm sai nhóm shot: mood "extreme close-up" + cụm "establishing shot" làm QC5 báo nhầm
- **Hiện tượng:** sau khi gộp 7 batch Bước 3, kiểm phân bố shot (Rule 4.2) thấy `--qc` QC5b sẽ báo 16 cửa sổ thiếu — một phần do ĐO SAI: mọi scene mood `shock` (mood_map = "dramatic side lighting, shallow DOF, extreme close-up") bị `shot_cat` đếm là `closeup` dù shot thật là wide/medium; và prompt viết `extreme wide ESTABLISHING shot` trả `None` (7 scene) vì không khớp chuỗi "extreme wide shot".
- **Gốc rễ:** `shot_cat` dò theo CỤM SCALE ("extreme close-up", "wide shot"...) trên body CÓ CẢ mood keywords → cụm "extreme close-up" trong mood shock trùng cụm shot; và chèn "establishing" vào giữa làm vỡ khớp chuỗi.
- **Phòng ngừa:** viết lại `shot_cat` dò theo LENS trước (Rule 4.8: 24mm/`35mm lens`→wide, 50mm/`85mm lens`→medium, `85mm portrait`/`100mm macro`→closeup) + từ khóa góc máy (over-shoulder/low/high angle→angle); chỉ fallback cụm scale khi thiếu lens. Lens là tín hiệu deterministic, không trùng mood. Sau sửa: 0 scene `None`, đo đúng. Ngoài ra phân bố THẬT vẫn lệch (over-shoulder/angle ít, closeup nhiều) ở 16 cửa sổ → rebalance bằng solver. **BÀI HỌC (phát hiện muộn ở Bước 5):** solver ban đầu chỉ ràng buộc theo `beat` đã WIDEN nhầm ~11 scene "object-insert" (macro giấy tờ/tài liệu/bàn tay trên vật thể: sổ đỏ 1892, kính lúp trên chữ nhỏ, ký tắt mực xanh, sổ tay cân) thành wide/medium/angle → ảnh vô nghĩa (wide shot của chữ 8pt). Gốc: `beat` không phân biệt close-up VẬT THỂ với close-up MẶT NGƯỜI. Đã sửa solver: KHÓA (giữ close-up) cả hook 1-6 LẪN mọi object-insert (nhận diện: Part-1 của prompt KHÔNG mở đầu bằng nano_name → chủ thể là vật thể) + cấm widen emotional_peak sang wide; chỉ cho phép move an toàn (dialogue→over-shoulder, establishing/room→wide, mặt người→medium). Kết quả: 16→4 cửa sổ thiếu + 2 streak, đều nằm trong chuỗi đọc/khám phá hợp đồng (61-70 toàn macro tài liệu) — CHẤP NHẬN vì ép variety ở đó sẽ phá close-up vật thể. Bước 5 `--unix-export`: 50 scene không có setting tag đều hợp lệ (hook intro + close-up vật thể + 3 exterior toà nhà 1 lần).

## [2026-07-08] Gate --step2 không tự kiểm Rule 3.3 (chuyển beat cấm) & 3.6 (nghỉ mắt) → lỗi cấu trúc lọt khi gộp segment
- **Hiện tượng:** Bước 2 chia 5 sub-agent theo segment; gate `--step2` PASS nhưng khi rà tay toàn cục phát hiện 2 chuyển beat cấm (Rule 3.3): scene 124 `resolution`→`tension` ngay ranh giới seg3/seg4, scene 197 `establishing`→`emotional_peak`. Nếu không rà tay thì 2 lỗi cấu trúc này ship luôn.
- **Gốc rễ:** `gate_step2()` chỉ kiểm coverage/gap/Dur/beat hợp lệ/duration bounds/4+ streak — KHÔNG kiểm Rule 3.3 và 3.6. Hai rule này CLAUDE.md giao cho "rà tay ở phiên chính sau khi gộp batch" → phụ thuộc con người nhớ làm; sub-agent mỗi segment tự cân bằng cục bộ nên chuyển beat cấm dễ sinh ĐÚNG tại ranh giới giữa 2 segment (không segment nào nhìn thấy cả 2 phía).
- **Phòng ngừa:** thêm vào `gate_step2()`: (1) check Rule 3.3 — cặp `(prev_beat, cur_beat)` thuộc `FORBIDDEN_TRANS` {tension→resolution, establishing→emotional_peak, resolution→tension} → cảnh báo; (2) check Rule 3.6 — đếm chuỗi scene liên tiếp không thuộc `REST_BEATS` {establishing, reflection}, chạm 8 → cảnh báo. Đã vá data project này: scene 124→`establishing` (beat chuyển-bối-cảnh sang Des Moines), scene 197→`reflection`. 3 cảnh báo 3.6 còn lại (scene 45/111/156) là 3 cao trào cố ý dồn dập, đã ghi rõ lý do chấp nhận trong mục QC Notes của `scene-breakdown.md`.

## [2026-07-07] Video hook nhạt: 1 scene tách nhiều clip gần giống nhau (tua chậm cùng khung)
- **Hiện tượng:** user thấy trong hook "1 phân cảnh nhưng nhiều prompt không thay đổi nhiều" — mỗi scene bị tách .1/.2 chỉ khác camera motion (wide rồi slow push-in cùng khung), cảm xúc phẳng. User muốn mỗi clip là 1 cảnh khác hẳn, dồn cảm xúc mạnh trong ~1 phút.
- **Gốc rễ:** Rule 6.2 cũ cho phép clip .k "Extend từ clip trước" (tua tiếp cùng góc) làm mặc định → 2 clip cùng scene gần giống nhau; `duration_s` mặc định 120 (2 phút) làm hook loãng. Rule 6.6 điểm 2/6 lại nhấn "subject hiện diện suốt clip / Extend giữ nguyên mô tả" khiến hiểu nhầm là phải giữ cùng chủ thể xuyên các clip.
- **Phòng ngừa:** Rule 6.1 đổi `duration_s` mặc định 120→**60** (hook ~1 phút, cảm xúc mạnh dồn). Rule 6.2 viết lại: **mỗi clip = 1 CÚ CẮT (hard cut) sang shot/chủ thể/scale mới, có ảnh riêng** (clip .1 = ảnh scene; clip .k = ảnh phụ `[stt]-[k].jpg`); CẤM Extend tua chậm trong hook. Rule 6.6/6.7 làm rõ: subject persistence áp TRONG 1 clip, cú cắt GIỮA các clip là bình thường; escalation toàn hook như trailer. Gate `check_video_hook` sửa: chỉ ép subject-anchor ở clip .1 (clip .k hard-cut được cắt sang insert vật thể/bối cảnh không cần gọi nhân vật). CLAUDE.md Bước 3 cập nhật. Đã viết lại video-prompts.md project này: 12 clip hard-cut, 0→1:08.

## [2026-07-07] Ảnh ingredient nhân vật bị vẽ SAI GIỚI TÍNH (Wade nam → ra nữ)
- **Hiện tượng:** user vẽ ảnh ingredient thấy Wade (thợ máy 25 tuổi) ra con gái, còn Young Wade (11-12) ra con trai đúng.
- **Gốc rễ:** `characters[].description` của Wade là `"25-year-old diesel mechanic, ...easy warm smile..."` — KHÔNG có danh từ giới tính tường minh (man/woman); nghề "diesel mechanic" + "warm smile" trung tính nên model image gen tự đoán → đoán ra nữ. Young Wade có chữ "boy" nên đúng. Rule 1.1/1.1b trước chỉ ép màu trang phục, không ép giới tính. Sai ở ảnh ingredient lan ra mọi scene tham chiếu.
- **Phòng ngừa:** Rule 1.1c mới — `description` PHẢI mở đầu bằng `[tuổi]-year-old man/woman/boy/girl` trước nghề nghiệp/đặc điểm; cấm dựa vào tín hiệu gián tiếp (nghề, stubble, đại từ ở field name). Gate `--step2` thêm check cảnh báo character thiếu token giới tính (`man/woman/boy/girl/male/female`). CLAUDE.md Bước 1 ghi rõ. Đã vá config project này: silas, silas_young, wade thêm danh từ giới tính + regenerate 3 ảnh ref tương ứng.

## [2026-07-07] Setting là asset trong Uni-X nhưng KHÔNG có ảnh ingredient để vẽ
- **Hiện tượng:** prompt Uni-X có tag `[COURTROOM]` (và các setting khác) nhưng `character-refs.md` chỉ sinh ảnh ref cho nhân vật → user không có ảnh bối cảnh COURTROOM nào để upload làm ingredient.
- **Gốc rễ:** `--unix-export` gắn asset tag cho CẢ nhân vật lẫn bối cảnh (setting `id` viết hoa), coi setting là ingredient reference; nhưng Bước 1 (Rule 1.4) chỉ sinh ref prompt cho nhân vật. Thiếu bước sinh ref cho setting.
- **Phòng ngừa:** Rule 2.3a mới — Bước 1 sinh ảnh ref cho TỪNG setting (template ảnh nền trống, không người, medium trung tính) vào chung `character-refs.md` mục "Bối cảnh / Setting Assets"; CLAUDE.md Bước 1 step 6 + sơ đồ cấu trúc cập nhật. Đã bổ sung 13 setting ref vào character-refs.md của project này.

## [2026-07-07] Uni-X mất tag bối cảnh do khớp case-sensitive + cụm định danh quá dài
- **Hiện tượng:** `--unix-export` báo 45 scene không xác định setting; trong đó scene 3, 66 (toàn/cực rộng bức tường rác) bị trượt dù prompt chứa ĐÚNG cụm định danh — chỉ khác ở chữ đầu VIẾT HOA ("Long wall..." vì cụm đứng đầu prompt Phần 2); scene 30, 188 trượt vì cụm định danh `east_fence_wall` dài ("...six feet high along a wire fence line") nên prompt viết bản rút gọn không khớp verbatim.
- **Gốc rễ:** (1) `find_setting_id` khớp `probe in prompt_text` phân biệt hoa-thường → cụm đứng đầu prompt (viết hoa) không khớp keyword (viết thường). (2) Cụm định danh đầu tiên của `settings[].keywords` quá dài, agent hay lược bớt phần đuôi → không còn khớp verbatim. Cùng họ lỗi với KAIZEN 2026-07-06 (cụm định danh phải ngắn + ổn định).
- **Phòng ngừa:** `export.py` sửa `find_setting_id` + chèn tag sang khớp KHÔNG phân biệt hoa-thường (`re.IGNORECASE`); rút gọn cụm định danh `east_fence_wall` để cụm đầu (trước dấu phẩy) là chuỗi ngắn ổn định "long wall of dark black-brown slum gum residue" (phần "six feet high..." chuyển ra sau phẩy). Quy ước bổ sung cho Rule 4.1 Phần 2: **cụm định danh nên NGẮN** (một danh ngữ lõi), tránh nhồi kích thước/vị trí vào cụm đầu. Sau vá: 45→40 scene, 40 còn lại đều là cận cảnh vật thể / không gian phụ 1 lần (chấp nhận).

## [2026-07-01] Tràn context bước 2 → thiếu 15,5 phút cuối video
- **Hiện tượng:** scene-breakdown dừng ở 00:32:29 trong khi SRT dài 00:48:01; 4 scene Dur=0; metadata.json viết tay khai tổng 2881s nhưng cộng thực 1949s — lỗi bị che, không ai biết.
- **Gốc rễ:** AI giữ toàn bộ bảng trong đầu rồi viết 1 lần; AI tự tuyên bố "xong" không máy kiểm; metadata viết tay nên số tổng bịa được.
- **Phòng ngừa:** quy tắc segment ~10 phút + append ngay (CLAUDE.md bước 2); gate coverage `export.py --step2`; bước 4 do script sinh, cấm viết tay.

## [2026-07-02] Ảnh lúc người thật lúc tranh vẽ
- **Hiện tượng:** cùng 1 bộ prompt, ảnh render lúc photorealistic lúc illustration.
- **Gốc rễ:** style anchor trộn 2 medium (`cinematic realistic illustration`) — mỗi lần generate model tự chọn 1 hướng.
- **Phòng ngừa:** Rule 2.1a (style dứt khoát 1 medium, 2 preset chuẩn); gate `--step3` chặn style trộn medium; ảnh ref nhân vật phải cùng medium.

## [2026-07-02] Hòm "chứa bí mật" → ảnh vẽ hòm mở
- **Hiện tượng:** narration nói hòm khó mở chứa bí mật, ảnh ra hòm đang mở.
- **Gốc rễ:** prompt mô tả ý nghĩa cốt truyện thay vì trạng thái thị giác; model không hiểu cốt truyện; từ phủ định/âm thanh model không vẽ được.
- **Phòng ngừa:** Rule 4.6 Visual State (trạng thái tường minh: closed/locked; cấm secret/hidden/no/not/without/từ âm thanh); gate `--step3` quét tự động.

## [2026-07-02] Lighting trong style anchor đè mood từng scene
- **Hiện tượng:** scene tense (tông lạnh) vẫn ám vàng ấm.
- **Gốc rễ:** style anchor chứa `warm golden lighting` được append vào mọi prompt, đánh nhau với mood keywords.
- **Phòng ngừa:** Rule 2.1a bổ sung — style anchor KHÔNG chứa lighting; lighting chỉ nằm ở Phần 4 (mood_map).

## [2026-07-02] Ảnh không đồng bộ ống kính + cắt cụt đầu ở close-up
- **Hiện tượng:** cùng loại shot nhưng ảnh khác chất; close-up hay bị crop mất đỉnh đầu.
- **Gốc rễ:** prompt thiếu tên lens; thiếu chỉ dẫn an toàn khung hình.
- **Phòng ngừa:** Rule 4.8 (bảng lens cố định theo shot type, `full head within frame` cho close-up); gate `--step3` warn shot thiếu lens.

## [2026-07-03] Video hook phẳng — 3 clip cùng scene gần giống nhau
- **Hiện tượng:** trong 1 scene đấu giá, clip 1/2/3 đều là "Jonah ngồi trong phòng" chỉ khác camera motion — không lột tả diễn biến narration, không tạo cảm xúc, không giữ chân người xem.
- **Gốc rễ:** quy tắc chia clip cũ chia ĐỀU theo thời gian, không theo beat nội dung; video prompt viết từ Description chung của scene thay vì đọc SRT tại từng khoảng giây; thiếu ngôn ngữ dựng phim (escalation wide→medium→close-up, reaction shot).
- **Phòng ngừa:** Rule 6.2 sửa (chia clip theo beat narration, cho phép ảnh phụ `[stt]-[k].jpg` khi cần cú cắt) + Rule 6.7 (mỗi clip 1 beat thị giác mới, escalation, reaction shot); gate `--step3` chặn 2 clip cùng scene trùng lặp ≥75% từ vựng, cảnh báo ≥55%.

## [2026-07-03] Nhân vật biến mất rồi hiện lại giữa video clip
- **Hiện tượng:** video Veo tạo ra ok nhưng người đột ngột biến mất rồi hiện lên lại.
- **Gốc rễ:** video prompt chứa từ đứt gãy thời gian ("revealing" — Clip 1.3); subject không được neo bằng nano_name + đặc điểm nhận diện; camera/hành động không giữ subject trong khung liên tục.
- **Phòng ngừa:** Rule 6.6 Subject Persistence; gate `--step3` chặn từ đứt gãy (suddenly/appears/disappears/reveals/transforms...) + chặn video prompt thiếu nano_name; QC checklist mục Subject Persistence.

## [2026-07-05] Nhân vật đổi màu trang phục giữa các scene khi generate footage
- **Hiện tượng:** cùng 1 nhân vật (vd Clare) mặc áo trắng ở scene này, áo đỏ ở scene liền kề — không nhất quán khi Flow generate ảnh/clip.
- **Gốc rễ:** character description trong `config.json` chỉ ghi loại trang phục ("sharp tailored blazer") mà không ghi MÀU cụ thể — anchor không khóa đủ nên mỗi lần generate model tự chọn màu ngẫu nhiên khác nhau. 7/8 nhân vật của project này mắc lỗi (chỉ Owen bản lao công có màu sẵn).
- **Phòng ngừa:** Rule 1.1 bổ sung — mọi trang phục trong character description PHẢI kèm màu cụ thể, không chỉ tên loại trang phục; đã vá lại config.json + character-refs.md + prompts.md + video-prompts.md của project hiện tại. Gate tự động cho việc này: CHƯA CÓ — cần bổ sung (khó quét máy vì "màu thiếu" đòi hỏi hiểu ngữ nghĩa danh từ trang phục, không đơn thuần word-match).

## [2026-07-06] Uni-X export không gắn được asset bối cảnh vì prompt dùng cụm rút gọn khác keywords config
- **Hiện tượng:** `--unix-export` cảnh báo 130/178 scene "không xác định được setting" — Assets chỉ có nhân vật, thiếu tag bối cảnh (FARM_KITCHEN...).
- **Gốc rễ:** `find_setting_id` khớp bằng cụm ĐẦU TIÊN (trước dấu phẩy) của `settings[].keywords`; ở Bước 3 các batch dùng cụm bối cảnh chuẩn hóa RÚT GỌN (cho vừa ngân sách 75 từ) khác với cụm đầu trong config → không khớp chuỗi.
- **Phòng ngừa:** quy ước mới — cụm đầu tiên của `settings[].keywords` CHÍNH LÀ cụm bối cảnh dùng nguyên văn trong prompt (một nguồn duy nhất, Bước 3 copy từ đó); đã căn lại 11 setting trong config project này cho khớp 178 prompt đã sinh. Gate: `--unix-export` sẵn có cảnh báo liệt kê scene không khớp — sau khi căn, 30 scene còn lại là cận cảnh chi tiết/không gian phụ không có setting entry (chấp nhận, không cần asset bối cảnh cho close-up).

## [2026-07-06] QC3 coi mọi character ID có "_" là variant quá khứ → đòi flashback_style sai
- **Hiện tượng:** project Harlan Boone có các variant tiến triển theo timeline chính (`eli_9`, `eli_12`, `kessler_1978`, `kessler_sunday`, `eli_pajamas`) — QC3 sẽ cảnh báo "thiếu flashback_style" cho ~25 scene dù các scene này KHÔNG phải hồi tưởng; trong khi nhân vật flashback thật (`annie`, không có "_") lại không được QC3 kiểm.
- **Gốc rễ:** gate QC3 dùng heuristic `"_" in id` để đoán "variant quá khứ" — đúng cái bẫy đã ghi ở CLAUDE.md (không suy đoán variant qua quy ước đặt tên ID). Naming format Rule 1.2 (`[id]_[context]`) dùng "_" cho MỌI loại variant, không riêng flashback.
- **Phòng ngừa:** config thêm field tường minh `flashback_variants` (danh sách character ID mà mọi scene chứa nó phải kèm flashback_style); `export.py --qc` ưu tiên field này, chỉ fallback heuristic "_" khi config không khai báo. Project hiện tại: `"flashback_variants": ["annie"]`.

## [2026-07-05] Dùng "Name's" (sở hữu cách dính liền tên) làm hỏng tham chiếu ảnh nhân vật
- **Hiện tượng:** prompt viết dạng "Dalton's blank puzzled expression..." — gắn 's ngay sau nano_name. User báo đây là lỗi nghiêm trọng: Flow tham chiếu ảnh ingredient bằng cách khớp đúng chuỗi nano_name, ký tự dính liền ngay sau tên (như 's) phá vỡ khớp lệnh tham chiếu.
- **Gốc rễ:** Rule 1.1 (Character Lock) trước đây chỉ yêu cầu nano_name "xuất hiện" trong prompt mà không quy định RÕ nano_name phải xuất hiện ở dạng nguyên vẹn (không gắn liền ký tự khác ngay sau). Hệ quả phụ: gate QC1 hiện tại kiểm bằng substring (`nn.lower() in body`) nên "dalton's" vẫn được tính là "có nano_name" — không bắt được lỗi này, gây lọt lưới.
- **Phòng ngừa:** Rule 1.1 bổ sung mục cấm sở hữu cách dính liền nano_name + hướng dẫn diễn đạt lại; gate `--step3`/`--qc` thêm check riêng quét pattern `{nano_name}'s` (word boundary) — LỖI cứng, không phải cảnh báo, vì đây là hỏng chức năng tham chiếu thật chứ không phải vấn đề văn phong.
