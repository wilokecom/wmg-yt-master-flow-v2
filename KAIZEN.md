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
