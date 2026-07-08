# Rule: Metadata Integrity

Quy tắc đảm bảo file metadata.json chính xác, máy đọc được, editor dùng được.

## 5.1 — No Gaps, No Overlaps

- `end` của scene N PHẢI bằng `start` của scene N+1.
- KHÔNG được có khoảng trống (gap) giữa 2 scene liên tiếp.
- KHÔNG được có chồng lấn (overlap) giữa 2 scene liên tiếp.
- Tổng `duration_s` của tất cả scene PHẢI bằng tổng thời lượng video (lấy từ SRT entry cuối cùng).

Ví dụ đúng:
```
Scene 1: start=00:00:00, end=00:00:18
Scene 2: start=00:00:18, end=00:00:32  ← start = end của scene trước
Scene 3: start=00:00:32, end=00:00:57
```

Ví dụ SAI:
```
Scene 1: end=00:00:18
Scene 2: start=00:00:20  ← GAP 2 giây!
```

## 5.2 — Sequential Numbering

- `stt` PHẢI là số nguyên liên tục bắt đầu từ 1.
- KHÔNG được nhảy số, lặp số, hoặc bắt đầu từ 0.

## 5.3 — Character Validation

- Mọi character ID trong `scenes[].characters` PHẢI tồn tại trong `project.characters[]`.
- KHÔNG được dùng character ID chưa được define.
- Nếu scene không có nhân vật cụ thể (ví dụ: cảnh bối cảnh thuần), `characters` là mảng rỗng `[]`.

## 5.4 — File Naming

- `image_file` đặt theo số thứ tự, đuôi `.jpg`.
- Format: `[stt].jpg`
- Ví dụ: `1.jpg`, `2.jpg`, `3.jpg`
- `image_file` PHẢI khớp với `stt` (scene stt=5 → image_file="5.jpg").

## 5.5 — Duration Calculation

- `duration_s` PHẢI được tính chính xác từ `start` và `end`.
- Công thức: `duration_s = end_seconds - start_seconds`
- KHÔNG được nhập tay — phải tính từ timestamp.

## 5.6 — Timestamp Format

- Format: `HH:MM:SS` (giờ:phút:giây, không có milliseconds).
- Ví dụ: `00:00:00`, `00:01:30`, `01:05:22`
- KHÔNG dùng format khác (không dùng giây thuần, không dùng MM:SS).

## 5.7 — Required Fields

Mỗi scene trong `scenes[]` PHẢI có đủ các field sau, KHÔNG được thiếu:

| Field | Type | Mô tả |
|---|---|---|
| `stt` | number | Số thứ tự liên tục từ 1 |
| `start` | string | Timestamp bắt đầu HH:MM:SS |
| `end` | string | Timestamp kết thúc HH:MM:SS |
| `duration_s` | number | Thời lượng tính bằng giây |
| `beat_type` | string | 1 trong 6 beat types đã define |
| `mood` | string | Mood của scene |
| `description` | string | Mô tả ngắn gọn nội dung scene (tiếng Việt) |
| `characters` | array | Danh sách character ID xuất hiện |
| `prompt` | string | Prompt ảnh hoàn chỉnh (tiếng Anh) |
| `image_file` | string | Tên file ảnh |

Field tùy chọn (có thể là mảng rỗng, không bắt buộc):

| Field | Type | Mô tả |
|---|---|---|
| `sfx` | array | Keyword hiệu ứng âm thanh (tiếng Anh) cho editor tìm sfx theo phân cảnh — sinh từ cột SFX của scene-breakdown.md, chỉ gồm âm thanh có thật trong narration/bối cảnh |
| `typewriter` | object | Cue hiệu ứng đánh máy (editor overlay lúc dựng): `{id, at, type, text, sync}` — merge từ `input/typewriter.json` khi chạy Bước 4; chỉ scene có cue mới mang field này. KHÔNG sửa tay trong metadata — sửa file nguồn rồi chạy lại export. Script validate: `stt` tồn tại (lỗi), `text` không rỗng (lỗi), `at` nằm trong khoảng scene (cảnh báo) |

## 5.8 — JSON Validity

- File metadata.json PHẢI là valid JSON.
- Encoding: UTF-8.
- KHÔNG có trailing comma.
- KHÔNG có comment trong JSON.
