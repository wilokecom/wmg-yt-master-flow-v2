#!/usr/bin/env python3
"""Generate prompts 54-196 and append to prompts.md"""

style = "photorealistic cinematic film still, 35mm film look, natural skin texture, soft depth of field, clean frame free of watermarks, logos, or AI icons"
flashback_style = ", soft warm vignette, slightly faded colors, dreamy atmosphere"

# Scene data from scene-breakdown.md
scenes = [
    # 54
    {"stt": 54, "beat": "establishing", "mood": "nostalgic", "chars": "george", "dur": 13, "desc": "Backstory - câu chuyện bắt đầu trước khi Carter sinh, 1971", "visual": "Wide establishing shot farm 1970s, vignette ấm", "sfx": "-"},
    # 55-60
    {"stt": 55, "beat": "reflection", "mood": "nostalgic", "chars": "george", "dur": 7, "desc": "George Garrett ký hợp đồng liên quan đến đất gia đình", "visual": "Medium shot George tại bàn, ký giấy", "sfx": "-"},
    {"stt": 56, "beat": "reflection", "mood": "nostalgic", "chars": "george", "dur": 5, "desc": "George không bỏ qua fine print", "visual": "Close-up George đọc văn bản nhỏ", "sfx": "-"},
    {"stt": 57, "beat": "reflection", "mood": "nostalgic", "chars": "george", "dur": 7, "desc": "Điều khoản: nếu đất được bank review, 7% giá trị tương lai", "visual": "Medium shot George đọc điều khoản", "sfx": "-"},
    {"stt": 58, "beat": "establishing", "mood": "nostalgic", "chars": "george, harold", "dur": 6, "desc": "George có 3 con trai, Harold là út, 19 tuổi khi nhận chìa", "visual": "Medium shot George đưa chìa cho Harold", "sfx": "-"},
    {"stt": 59, "beat": "reflection", "mood": "nostalgic", "chars": "george", "dur": 7, "desc": "George nói 3 điều: giữ chìa, trả phí, không mở tủ cho đến khi bank cố chiếm", "visual": "Close-up George nói với Harold", "sfx": "-"},
    {"stt": 60, "beat": "reflection", "mood": "sad", "chars": "george", "dur": 4, "desc": "George chết 6 tháng sau", "visual": "Wide shot nông trại, cờ thấp", "sfx": "wind through trees"},
    # 61-66
    {"stt": 61, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Harold trả 40 đô mỗi năm, không bao giờ mở tủ", "visual": "Medium shot Harold tại bank, trả tiền", "sfx": "-"},
    {"stt": 62, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 7, "desc": "Chìa trên tủ đầu giường cạnh ảnh George", "visual": "Close-up chìa khóa và ảnh cũ", "sfx": "-"},
    {"stt": 63, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 5, "desc": "Harold đôi khi nhìn chìa và thắc mắc", "visual": "Close-up Harold nhìn chìa", "sfx": "-"},
    {"stt": 64, "beat": "establishing", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Năm trôi qua - Harold kết hôn, có con, thành góa, David lớn lên", "visual": "Wide shot farm qua các năm", "sfx": "-"},
    {"stt": 65, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 7, "desc": "Harold ở lại farm, trồng ngô, sửa hàng rào, thắc mắc", "visual": "Medium shot Harold làm việc trên farm", "sfx": "-"},
    {"stt": 66, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Tại sao trả cho hộp không bao giờ mở", "visual": "Close-up Harold trầm ngâm", "sfx": "-"},
    # 67-72
    {"stt": 67, "beat": "establishing", "mood": "tense", "chars": "-", "dur": 6, "desc": "Bốn tháng trước, mọi thứ thay đổi - ngân hàng bán ra state", "visual": "Wide shot bank lobby, bảng hiệu mới", "sfx": "-"},
    {"stt": 68, "beat": "establishing", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Carter Blake đến", "visual": "Medium shot Carter tại bàn", "sfx": "-"},
    {"stt": 69, "beat": "establishing", "mood": "tense", "chars": "-", "dur": 6, "desc": "Hai tuần trước, review đất của Harold", "visual": "Medium shot Harold đọc notice", "sfx": "-"},
    {"stt": 70, "beat": "reflection", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Điều khoản 7% thức dậy", "visual": "Close-up Harold hiểu", "sfx": "-"},
    {"stt": 71, "beat": "reflection", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Ngân hàng tự kích hoạt điều khoản, không biết", "visual": "Medium shot Harold, điềm tĩnh", "sfx": "-"},
    {"stt": 72, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold lái đến thị trấn, trả 40 đô, chờ", "visual": "Wide shot Harold lái xe đến bank", "sfx": "truck engine"},
    # 73-78
    {"stt": 73, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Chia đã chết, nhưng vẫn đặt bẫy", "visual": "Medium shot Harold nhìn lên bầu trời", "sfx": "-"},
    {"stt": 74, "beat": "dialogue", "mood": "calm", "chars": "harold", "dur": 7, "desc": "Harold gọi David ở Nashville", "visual": "Medium shot Harold nói điện thoại", "sfx": "phone dial tone"},
    {"stt": 75, "beat": "dialogue", "mood": "calm", "chars": "david", "dur": 6, "desc": "David nghe không ngắt, hỏi: 'Dad, do you understand what this means?'", "visual": "Medium shot David trên điện thoại", "sfx": "-"},
    {"stt": 76, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold giải thích điều khoản 7% được kích hoạt", "visual": "Medium shot Harold nói điềm tĩnh", "sfx": "-"},
    {"stt": 77, "beat": "dialogue", "mood": "hopeful", "chars": "david", "dur": 6, "desc": "David: 'How much are we talking?'", "visual": "Close-up David, tò mò", "sfx": "-"},
    {"stt": 78, "beat": "emotional_peak", "mood": "shock", "chars": "harold", "dur": 6, "desc": "Harold: 'Seven percent of four point two million'", "visual": "Close-up Harold nói số", "sfx": "-"},
    # 79-84
    {"stt": 79, "beat": "emotional_peak", "mood": "shock", "chars": "david", "dur": 6, "desc": "David: 'Dad, that's nearly three hundred thousand dollars'", "visual": "Close-up David, kinh ngạc", "sfx": "-"},
    {"stt": 80, "beat": "dialogue", "mood": "shock", "chars": "david", "dur": 6, "desc": "David: 'And the bank has no idea?'", "visual": "Medium shot David trên điện thoại", "sfx": "-"},
    {"stt": 81, "beat": "dialogue", "mood": "hopeful", "chars": "david", "dur": 6, "desc": "David mỉm cười, Harold nghe được qua điện thoại", "visual": "Close-up David mỉm cười nhẹ", "sfx": "-"},
    {"stt": 82, "beat": "dialogue", "mood": "hopeful", "chars": "david", "dur": 6, "desc": "David: 'Dad, what now?'", "visual": "Medium shot David, tò mò", "sfx": "-"},
    {"stt": 83, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold nhìn chìa khóa: 'I waited fifty-three years. I can wait thirty more days'", "visual": "Close-up Harold và chìa khóa trên bàn", "sfx": "-"},
    {"stt": 84, "beat": "establishing", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Ba ngày sau, Harold quay lại ngân hàng với phong bì", "visual": "Wide shot Harold bước vào ngân hàng", "sfx": "door chime"},
    # 85-90
    {"stt": 85, "beat": "dialogue", "mood": "dismissive", "chars": "carter, harold", "dur": 6, "desc": "Carter nhìn lên, vẻ gần không remember tủ 107", "visual": "Medium shot Carter tại bàn", "sfx": "-"},
    {"stt": 86, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 5, "desc": "Harold ngồi, đặt phong bì trước Carter", "visual": "Medium shot Harold ngồi, đặt phong bì", "sfx": "paper thud"},
    {"stt": 87, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 5, "desc": "Harold: 'I'd like to file a formal claim'", "visual": "Close-up Harold, kiên định", "sfx": "-"},
    {"stt": 88, "beat": "dialogue", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Carter mở phong bì, gần cười lại", "visual": "Medium shot Carter mở phong bì", "sfx": "envelope rustle"},
    {"stt": 89, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold đẩy giấy thứ hai - federal records letter", "visual": "Close-up giấy với dấu đỏ", "sfx": "-"},
    {"stt": 90, "beat": "dialogue", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Carter cầm lên, đọc - thư federal records với dấu đỏ", "visual": "Medium shot Carter đọc thư, vẻ thay đổi", "sfx": "-"},
    # 91-96
    {"stt": 91, "beat": "reflection", "mood": "determined", "chars": "-", "dur": 6, "desc": "Thư nói: agreement 1971 còn hiệu lực, binding và enforceable", "visual": "Close-up nội dung thư", "sfx": "-"},
    {"stt": 92, "beat": "reflection", "mood": "determined", "chars": "-", "dur": 7, "desc": "Điều khoản tiếp tục qua mọi người kế thừa", "visual": "Close-up tiếp tục nội dung", "sfx": "-"},
    {"stt": 93, "beat": "tension", "mood": "shock", "chars": "carter", "dur": 3, "desc": "Carter đọc một lần, rồi lần nữa", "visual": "Close-up Carter đọc, lo lắng", "sfx": "-"},
    {"stt": 94, "beat": "tension", "mood": "shock", "chars": "carter", "dur": 2, "desc": "Cười biến mất khỏi mặt Carter", "visual": "Medium shot Carter, vẻ nghiêm túc", "sfx": "-"},
    {"stt": 95, "beat": "dialogue", "mood": "dismissive", "chars": "carter", "dur": 4, "desc": "Carter: 'I'll need legal to review this'", "visual": "Close-up Carter, lo lắng", "sfx": "-"},
    {"stt": 96, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold: 'I expected that' - đứng dậy, cài áo", "visual": "Medium shot Harold đứng dậy", "sfx": "-"},
    # 97-102
    {"stt": 97, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold: 'You have thirty days. After that, I file in federal court'", "visual": "Close-up Harold, kiên định", "sfx": "-"},
    {"stt": 98, "beat": "dialogue", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Carter: 'This bank is not paying money over some old paper'", "visual": "Medium shot Carter, sắc bén", "sfx": "-"},
    {"stt": 99, "beat": "dialogue", "mood": "determined", "chars": "harold", "dur": 6, "desc": "Harold: 'Thirty days, Mr. Blake' - cầm phong bì đi", "visual": "Medium shot Harold đi ra", "sfx": "footsteps"},
    {"stt": 100, "beat": "reflection", "mood": "nostalgic", "chars": "-", "dur": 6, "desc": "Hai teller nhìn, nhớ Carter cười trong vault", "visual": "Medium shot teller nhìn Harold đi ra", "sfx": "-"},
    {"stt": 101, "beat": "establishing", "mood": "tense", "chars": "carter", "dur": 5, "desc": "Carter gọi legal chiều hôm đó", "visual": "Medium shot Carter trên điện thoại", "sfx": "phone dialing"},
    {"stt": 102, "beat": "establishing", "mood": "tense", "chars": "-", "dur": 5, "desc": "Legal gọi lại sáng hôm sau", "visual": "Medium shot điện thoại ngân hàng", "sfx": "phone ringing"},
    # 103-108
    {"stt": 103, "beat": "tension", "mood": "shock", "chars": "carter", "dur": 5, "desc": "Lần đầu Carter ngừng cười từ khi đến First Valley", "visual": "Medium shot Carter, vẻ suy nghĩ", "sfx": "-"},
    {"stt": 104, "beat": "establishing", "mood": "tense", "chars": "-", "dur": 6, "desc": "Phiên tòa sáng thứ Ba tại Nashville", "visual": "Wide establishing shot courtroom", "sfx": "-"},
    {"stt": 105, "beat": "establishing", "mood": "tense", "chars": "-", "dur": 6, "desc": "Phòng tường gỗ, cờ cũ, sự im lặng làm mọi tiếng động lớn hơn", "visual": "Wide shot courtroom, im lặng", "sfx": "-"},
    {"stt": 106, "beat": "establishing", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Carter đến với hai luật sư trẻ, hồ sơ da, giọng êm", "visual": "Medium shot Carter và luật sư", "sfx": "-"},
    {"stt": 107, "beat": "dialogue", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Luật sư tránh nhìn Harold khi ông vào", "visual": "Medium shot Harold bước vào, luật sư nhìn đi", "sfx": "footsteps"},
    {"stt": 108, "beat": "establishing", "mood": "calm", "chars": "harold", "dur": 6, "desc": "Harold đi một mình, không vội, không biểu cảm", "visual": "Medium shot Harold bước đi", "sfx": "-"},
    # 109-114
    {"stt": 109, "beat": "establishing", "mood": "calm", "chars": "harold, frank", "dur": 6, "desc": "Harold ngồi cạnh Frank Solis, luật sư bất động sản 60 tuổi", "visual": "Medium shot Harold và Frank", "sfx": "-"},
    {"stt": 110, "beat": "establishing", "mood": "calm", "chars": "frank", "dur": 6, "desc": "Frank không thích diễn thuyết, chỉ thắng bằng lập luận", "visual": "Medium shot Frank chỉnh kính", "sfx": "-"},
    {"stt": 111, "beat": "establishing", "mood": "tense", "chars": "judge_chan", "dur": 6, "desc": "Judge Margaret Chan đến đúng giờ, đã đọc mọi trang đêm trước", "visual": "Medium shot thẩm phán bước vào", "sfx": "gavel tap"},
    {"stt": 112, "beat": "dialogue", "mood": "dismissive", "chars": "-", "dur": 6, "desc": "Luật sư ngân hàng đứng, tranh 17 phút về agreement 1971", "visual": "Medium shot luật sư ngân hàng nói", "sfx": "-"},
    {"stt": 113, "beat": "dialogue", "mood": "dismissive", "chars": "-", "dur": 6, "desc": "Luật sư nói: ngôn ngữ không rõ, quá nhiều thời gian, không khiếu nại", "visual": "Medium shot luật sư tiếp tục", "sfx": "-"},
    {"stt": 114, "beat": "dialogue", "mood": "dismissive", "chars": "-", "dur": 6, "desc": "Laches doctrine, statute of limitations đã hết, văn bản là cổ vật", "visual": "Medium shot luật sư kết thúc", "sfx": "-"},
    # 115-120
    {"stt": 115, "beat": "tension", "mood": "tense", "chars": "-", "dur": 3, "desc": "Luật sư ngồi", "visual": "Medium shot luật sư ngồi", "sfx": "-"},
    {"stt": 116, "beat": "dialogue", "mood": "calm", "chars": "judge_chan", "dur": 4, "desc": "Thẩm phán quay Frank: 'Mr. Solis?'", "visual": "Medium shot thẩm phán nhìn Frank", "sfx": "-"},
    {"stt": 117, "beat": "dialogue", "mood": "determined", "chars": "frank", "dur": 6, "desc": "Frank đứng, chỉnh kính, nói 3 câu", "visual": "Medium shot Frank đứng", "sfx": "-"},
    {"stt": 118, "beat": "dialogue", "mood": "determined", "chars": "frank", "dur": 6, "desc": "Frank: 'Agreement valid. Activation clause valid. Bank triggered both.'", "visual": "Close-up Frank nói ngắn gọn", "sfx": "-"},
    {"stt": 119, "beat": "dialogue", "mood": "calm", "chars": "frank", "dur": 3, "desc": "Frank ngồi xuống", "visual": "Medium shot Frank ngồi", "sfx": "-"},
    {"stt": 120, "beat": "reflection", "mood": "calm", "chars": "judge_chan", "dur": 6, "desc": "Thẩm phán đọc giấy 1971, review ngân hàng, thư federal", "visual": "Close-up thẩm phán đọc tài liệu", "sfx": "paper rustling"},
    # 121-126
    {"stt": 121, "beat": "reflection", "mood": "calm", "chars": "judge_chan", "dur": 6, "desc": "Đặt ba giấy cạnh nhau trên bàn", "visual": "Medium shot thẩm phán đặt giấy", "sfx": "-"},
    {"stt": 122, "beat": "tension", "mood": "tense", "chars": "-", "dur": 6, "desc": "Phòng im lặng đến độ nghe thở", "visual": "Wide shot courtroom im lặng", "sfx": "-"},
    {"stt": 123, "beat": "dialogue", "mood": "tense", "chars": "judge_chan", "dur": 6, "desc": "Thẩm phán nhìn luật sư: 'Your client filed voluntarily, correct?'", "visual": "Medium shot thẩm phán hỏi luật sư", "sfx": "-"},
    {"stt": 124, "beat": "dialogue", "mood": "dismissive", "chars": "-", "dur": 3, "desc": "Luật sư: 'Yes, your honor, but intent...'", "visual": "Close-up luật sư bối rối", "sfx": "-"},
    {"stt": 125, "beat": "dialogue", "mood": "tense", "chars": "judge_chan", "dur": 3, "desc": "Thẩm phán: 'Garrett property identified specifically?'", "visual": "Medium shot thẩm phán hỏi tiếp", "sfx": "-"},
    {"stt": 126, "beat": "dialogue", "mood": "dismissive", "chars": "-", "dur": 3, "desc": "Luật sư: 'Yes, but intent...'", "visual": "Close-up luật sư bối rối hơn", "sfx": "-"},
    # 127-132
    {"stt": 127, "beat": "emotional_peak", "mood": "determined", "chars": "judge_chan", "dur": 6, "desc": "Thẩm phán: 'Intent does not rewrite signed language' - nhìn Carter", "visual": "Medium shot thẩm phán nhìn trực tiếp Carter", "sfx": "-"},
    {"stt": 128, "beat": "emotional_peak", "mood": "determined", "chars": "judge_chan", "dur": 3, "desc": "Thẩm phán: 'Mr. Blake'", "visual": "Close-up thẩm phán gọi tên", "sfx": "-"},
    {"stt": 129, "beat": "tension", "mood": "tense", "chars": "carter", "dur": 3, "desc": "Carter ngồi dậy, căng thẳng", "visual": "Medium shot Carter đứng dậy", "sfx": "-"},
    {"stt": 130, "beat": "emotional_peak", "mood": "determined", "chars": "judge_chan", "dur": 6, "desc": "Thẩm phán: 'On the day Mr. Garrett opened his locker, you laughed'", "visual": "Medium shot thẩm phán nói", "sfx": "-"},
    {"stt": 131, "beat": "tension", "mood": "tense", "chars": "carter", "dur": 3, "desc": "Carter im lặng", "visual": "Close-up Carter cúi đầu", "sfx": "-"},
    {"stt": 132, "beat": "emotional_peak", "mood": "determined", "chars": "judge_chan", "dur": 6, "desc": "Thẩm phán: 'Do you understand what this document means?'", "visual": "Medium shot thẩm phán hỏi", "sfx": "-"},
    # 133-138
    {"stt": 133, "beat": "emotional_peak", "mood": "shock", "chars": "carter", "dur": 3, "desc": "Carter: 'I understand it now, your honor'", "visual": "Close-up Carter, khiêm tốn", "sfx": "-"},
    {"stt": 134, "beat": "resolution", "mood": "determined", "chars": "judge_chan", "dur": 6, "desc": "Thẩm phán gật đầu: 'Agreement enforceable. Bank triggered clause.'", "visual": "Medium shot thẩm phán phán quyết", "sfx": "gavel tap"},
    {"stt": 135, "beat": "resolution", "mood": "determined", "chars": "judge_chan", "dur": 6, "desc": "'294,000 dollars consistent with seven percent provision'", "visual": "Medium shot thẩm phán tiếp tục", "sfx": "-"},
    {"stt": 136, "beat": "resolution", "mood": "determined", "chars": "judge_chan", "dur": 3, "desc": "Thẩm phán cầm bút: 'Judgment for the plaintiff'", "visual": "Close-up bút thẩm phán trên giấy", "sfx": "gavel strike"},
    {"stt": 137, "beat": "tension", "mood": "shock", "chars": "-", "dur": 3, "desc": "Không ai di chuyển", "visual": "Wide shot courtroom tĩnh", "sfx": "-"},
    {"stt": 138, "beat": "resolution", "mood": "calm", "chars": "frank, harold", "dur": 6, "desc": "Frank đặt tay nhẹ lên tay Harold, Harold gật đầu", "visual": "Medium close-up Frank và Harold", "sfx": "-"},
    # 139-144
    {"stt": 139, "beat": "establishing", "mood": "dismissive", "chars": "carter", "dur": 6, "desc": "Carter từ chức 11 ngày sau", "visual": "Medium shot Carter đóng hộp", "sfx": "-"},
    {"stt": 140, "beat": "resolution", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Ngân hàng trả Harold 294,000 đô đầy đủ trong 30 ngày", "visual": "Medium shot Harold tại quầy ngân hàng", "sfx": "-"},
    {"stt": 141, "beat": "resolution", "mood": "hopeful", "chars": "harold", "dur": 7, "desc": "Sau phí và thuế, nhiều tiền hơn Harold từng nắm", "visual": "Close-up Harold cầm séc", "sfx": "-"},
    {"stt": 142, "beat": "reflection", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Nhưng đó không phải điều người nhớ", "visual": "Medium shot Harold nhìn séc", "sfx": "-"},
    {"stt": 143, "beat": "establishing", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Điều người nhớ: Federal land officials review các hồ sơ tương tự", "visual": "Wide shot văn phòng liên bang", "sfx": "papers shuffling"},
    {"stt": 144, "beat": "establishing", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "17 gia đình nông thôn khác được thông báo về agreement cũ", "visual": "Medium shot thư gửi đi", "sfx": "-"},
    # 145-150
    {"stt": 145, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Nông dân bán cổ phần khoáng sản 1960s-70s có điều khoản tương tự", "visual": "Medium shot nông dân đọc thư", "sfx": "-"},
    {"stt": 146, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Ngân hàng review phát triển mà không hiểu điều khoản trong deed", "visual": "Wide shot văn phòng ngân hàng", "sfx": "-"},
    {"stt": 147, "beat": "reflection", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Một người mở tủ, mở cửa cho người khác", "visual": "Medium shot Harold, hài lòng", "sfx": "-"},
    {"stt": 148, "beat": "establishing", "mood": "hopeful", "chars": "frank", "dur": 6, "desc": "Frank nhận 4 cuộc gọi tuần đó", "visual": "Medium shot Frank trên điện thoại", "sfx": "phone ringing"},
    {"stt": 149, "beat": "establishing", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Harold lái về nhà một mình", "visual": "Wide shot Harold lái xe trên đường quen", "sfx": "truck engine"},
    {"stt": 150, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Đường giống nhau, cánh đồng giống nhau, hàng rào giống nhau", "visual": "Medium shot xe qua cánh đồng", "sfx": "-"},
    # 151-156
    {"stt": 151, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Xe dừng ngoài farmhouse, Harold ngồi trong xe một lúc", "visual": "Medium shot Harold trong xe, nhìn ra ngoài", "sfx": "engine cooling"},
    {"stt": 152, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Mùi đất vẫn còn trên tay Harold", "visual": "Close-up bàn tay Harold", "sfx": "-"},
    {"stt": 153, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Harold lấy giấy từ túi áo, đọc, gấp lại như cha từng làm", "visual": "Close-up Harold đọc giấy, gấp cẩn thận", "sfx": "paper folding"},
    {"stt": 154, "beat": "establishing", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Gần hoàng hôn, Harold đi đến đồng bắc", "visual": "Wide shot Harold đi qua cánh đồng lúc chiều", "sfx": "footsteps on dirt"},
    {"stt": 155, "beat": "establishing", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Không khí lạnh, trời chuyển xanh sang cam, qua hàng rào", "visual": "Medium shot Harold đi qua hàng rào gỗ", "sfx": "wind through trees"},
    {"stt": 156, "beat": "establishing", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Đến cây sồi nơi cha chôn dưới đá mộ đơn giản", "visual": "Medium shot Harold đứng dưới cây sồi lớn", "sfx": "wind rustling"},
    # 157-162
    {"stt": 157, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Harold đứng trong gió lâu, nghe gió qua lá sồi", "visual": "Close-up Harold, điềm tĩnh", "sfx": "wind through oak leaves"},
    {"stt": 158, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Nhìn ánh sáng tàn từ nhánh cây", "visual": "Medium close-up Harold nhìn lên", "sfx": "-"},
    {"stt": 159, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Đặt tay trên vỏ cây sồi, cảm nhận gỗ mạnh mẽ", "visual": "Close-up tay Harold trên vỏ cây", "sfx": "-"},
    {"stt": 160, "beat": "emotional_peak", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Harold nói những từ duy nhất quan trọng", "visual": "Medium shot Harold, nghiêm túc", "sfx": "-"},
    {"stt": 161, "beat": "emotional_peak", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "'You were right, Dad. Some men never live to see what they build'", "visual": "Close-up Harold nói với mộ", "sfx": "-"},
    {"stt": 162, "beat": "emotional_peak", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "'They plant trees they will never sit under. Protect futures they'll never touch'", "visual": "Close-up Harold tiếp tục", "sfx": "-"},
    # 163-168
    {"stt": 163, "beat": "emotional_peak", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "'George Garrett never entered a courtroom, never filed a claim, never asked for praise'", "visual": "Medium shot Harold nói tiếp", "sfx": "-"},
    {"stt": 164, "beat": "emotional_peak", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "'He simply made sure his son would be ready when the day came'", "visual": "Close-up Harold, cảm động", "sfx": "-"},
    {"stt": 165, "beat": "emotional_peak", "mood": "nostalgic", "chars": "harold", "dur": 3, "desc": "'That is what real legacy looks like'", "visual": "Medium shot Harold nói câu cuối", "sfx": "-"},
    {"stt": 166, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Gió mang lời Harold qua đồng", "visual": "Wide shot Harold dưới cây sồi, gió thổi", "sfx": "wind through fields"},
    {"stt": 167, "beat": "reflection", "mood": "nostalgic", "chars": "harold", "dur": 6, "desc": "Harold đứng đó đến khi ánh sáng tàn, không khí lạnh", "visual": "Medium shot Harold đứng, chiều tàn", "sfx": "-"},
    {"stt": 168, "beat": "resolution", "mood": "calm", "chars": "harold", "dur": 6, "desc": "Harold đi về farmhouse", "visual": "Medium shot Harold đi về", "sfx": "footsteps"},
    # 169-174
    {"stt": 169, "beat": "resolution", "mood": "calm", "chars": "harold", "dur": 6, "desc": "Đi giống nhau mọi tối trong 53 năm", "visual": "Wide shot Harold đi về nhà", "sfx": "-"},
    {"stt": 170, "beat": "resolution", "mood": "calm", "chars": "harold", "dur": 6, "desc": "Chìa về tủ đầu giường", "visual": "Close-up chìa khóa trên tủ", "sfx": "-"},
    {"stt": 171, "beat": "resolution", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Giấy vào hộp tủ sắt", "visual": "Close-up giấy vào hộp", "sfx": "-"},
    {"stt": 172, "beat": "resolution", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Farm an toàn, đất George bảo vệ từ mộ sẽ ở lại với gia đình", "visual": "Medium shot Harold nhìn farm", "sfx": "-"},
    {"stt": 173, "beat": "resolution", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Đã làm việc 3 thế hệ", "visual": "Medium shot Harold nhìn cánh đồng", "sfx": "-"},
    {"stt": 174, "beat": "resolution", "mood": "calm", "chars": "harold", "dur": 6, "desc": "Mở cửa farmhouse, bước vào", "visual": "Medium shot Harold mở cửa nhà", "sfx": "door creak"},
    # 175-180
    {"stt": 175, "beat": "resolution", "mood": "calm", "chars": "harold", "dur": 6, "desc": "Im lặng chào", "visual": "Medium shot Harold trong nhà", "sfx": "-"},
    {"stt": 176, "beat": "resolution", "mood": "hopeful", "chars": "harold", "dur": 6, "desc": "Sẽ gọi David sáng mai, bàn bạc tiền, tối nay nghỉ", "visual": "Close-up Harold, hài lòng", "sfx": "-"},
    {"stt": 177, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 11, "desc": "Legacy hoàn thành, bẫy bật, Harold thắng", "visual": "Wide shot farm lúc hoàng hôn", "sfx": "birds chirping"},
    {"stt": 178, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "'That is what real legacy looks like'", "visual": "Wide shot Harold nhìn ra ngoài", "sfx": "-"},
    {"stt": 179, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Nếu từng bị gọi ngu vì giữ thứ người coi vô giá trị", "visual": "Medium shot người xem,共鸣", "sfx": "-"},
    {"stt": 180, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Bạn đã hiểu tại sao người đàn ông quay lại", "visual": "Medium shot người xem, gật đầu", "sfx": "-"},
    # 181-186
    {"stt": 181, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Câu chuyện đánh với 5,300 người", "visual": "Medium shot comment trên màn hình", "sfx": "-"},
    {"stt": 182, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Người gọi câu chuyện quan trọng nhất", "visual": "Medium shot người đọc bình luận", "sfx": "-"},
    {"stt": 183, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Cảm nhận lỗ hổng, được đánh giá thấp", "visual": "Close-up người xem, gật đầu", "sfx": "-"},
    {"stt": 184, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Comments nói lỗ hổng lặng đặn", "visual": "Medium shot comments trên màn hình", "sfx": "-"},
    {"stt": 185, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Không cô đơn", "visual": "Close-up Harold, mỉm cười nhẹ", "sfx": "-"},
    {"stt": 186, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Subscribe nếu muốn thêm câu chuyện như thế này", "visual": "Wide shot Harold đứng trên farm", "sfx": "-"},
    # 187-192
    {"stt": 187, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Bà 79 tuổi Georgia đi vào tòa một mình với deed không ai tin", "visual": "Medium shot bà 79 tuổi bên tòa", "sfx": "footsteps"},
    {"stt": 188, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Deed không ai tin", "visual": "Close-up deed cũ", "sfx": "-"},
    {"stt": 189, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Có thể cần biết George Garrett đúng", "visual": "Medium shot bà kiên định", "sfx": "-"},
    {"stt": 190, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "George Garrett đã đúng", "visual": "Medium shot Harold dưới cây sồi", "sfx": "-"},
    {"stt": 191, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Mở rộng câu chuyện - bà Georgia", "visual": "Wide shot courtroom với bà già", "sfx": "-"},
    {"stt": 192, "beat": "reflection", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Deed không ai tin", "visual": "Close-up deed cũ", "sfx": "-"},
    # 193-196
    {"stt": 193, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 5, "desc": "Kết thúc - bà 79 tuổi biết George đúng", "visual": "Wide shot farm hoàng hôn, chữ 'George was right'", "sfx": "wind through trees"},
    {"stt": 194, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "George Garrett was right - kết thúc", "visual": "Wide shot farm hoàng hôn, Harold đứng", "sfx": "wind through trees"},
    {"stt": 195, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 6, "desc": "Mở rộng câu chuyện", "visual": "Medium shot Harold nhìn camera, gật đầu", "sfx": "-"},
    {"stt": 196, "beat": "resolution", "mood": "hopeful", "chars": "-", "dur": 5, "desc": "Subscribe", "visual": "Medium shot Harold trên farm, caption", "sfx": "-"},
]

# Character nano_names
char_map = {
    "harold": "Harold",
    "carter": "Carter",
    "george": "Young George",
    "david": "David",
    "frank": "Frank",
    "judge_chan": "Judge Chan",
}

# Setting keywords
settings_map = {
    "bank_lobby": "modern bank lobby",
    "vault_room": "small steel vault room",
    "harold_farm": "rural Tennessee farmland",
    "farmhouse": "weathered clapboard farmhouse",
    "north_field": "open field near sunset",
    "courtroom": "wood-paneled courtroom",
}

# Mood keywords
mood_map = {
    "nostalgic": "soft golden light warm palette slight gaussian blur",
    "tense": "cool blue-gray tones hard shadows tight framing",
    "hopeful": "morning light open composition warm highlights",
    "shock": "dramatic side lighting shallow DOF extreme close-up",
    "calm": "even soft lighting neutral tones balanced composition",
    "sad": "muted desaturated palette overcast lighting empty space",
    "determined": "strong directional light firm posture clear focus",
    "dismissive": "cold office light distant framing clinical atmosphere",
}

# Shot type mapping based on visual notes
def get_shot_type(visual, beat):
    visual = visual.lower()
    if "wide" in visual and "establishing" in visual:
        return "wide establishing shot, 24mm wide-angle lens"
    elif "wide shot" in visual:
        return "wide shot, 35mm lens"
    elif "close-up" in visual:
        return "close-up, 85mm portrait lens full head within frame"
    elif "medium close-up" in visual:
        return "medium close-up, 85mm portrait lens full head within frame"
    elif "medium shot" in visual:
        return "medium shot, 50mm lens"
    elif "extreme close-up" in visual:
        return "extreme close-up, 100mm macro lens"
    else:
        # Default based on beat
        if beat == "establishing":
            return "wide establishing shot, 24mm wide-angle lens"
        elif beat == "emotional_peak":
            return "close-up, 85mm portrait lens full head within frame"
        else:
            return "medium shot, 50mm lens"

# Generate prompts
output = []
for s in scenes:
    stt = s["stt"]
    beat = s["beat"]
    mood = s["mood"]
    dur = s["dur"]
    chars_raw = s["chars"]

    # Parse characters
    if chars_raw == "-":
        chars = "-"
        chars_list = []
    else:
        chars_list = [char_map[c.strip()] for c in chars_raw.split(",")]
        chars = ", ".join(chars_list)

    # Determine setting
    setting = "empty space"
    if "courtroom" in s["visual"].lower() or "thẩm phán" in s["visual"] or "luật sư" in s["visual"]:
        setting = settings_map["courtroom"]
    elif "vault" in s["visual"].lower() or "tủ" in s["visual"]:
        setting = settings_map["vault_room"]
    elif "bank" in s["visual"].lower() or "ngân hàng" in s["visual"] or "quầy" in s["visual"]:
        setting = settings_map["bank_lobby"]
    elif "farm" in s["visual"].lower() or "cánh đồng" in s["visual"]:
        setting = settings_map["harold_farm"]
    elif "farmhouse" in s["visual"].lower() or "nhà" in s["visual"] and "farm" not in s["visual"]:
        setting = settings_map["farmhouse"]
    elif "sồi" in s["visual"].lower() or "mộ" in s["visual"]:
        setting = settings_map["north_field"]
    elif "văn phòng" in s["visual"].lower():
        setting = "federal office interior"
    elif "màn hình" in s["visual"].lower():
        setting = "computer screen"
    elif "tòa" in s["visual"].lower():
        setting = settings_map["courtroom"]

    # Part 1: Characters + action
    if chars == "-":
        # No characters - describe setting action
        if "courtroom" in s["visual"].lower():
            part1 = "Empty courtroom with quiet atmosphere"
        elif "bank" in s["visual"].lower() or "ngân hàng" in s["visual"]:
            part1 = "Empty bank lobby with quiet atmosphere"
        elif "farm" in s["visual"].lower():
            part1 = "Empty farm landscape stretching to horizon"
        elif "thư" in s["visual"].lower():
            part1 = "Paper documents on desk"
        elif "séc" in s["visual"].lower():
            part1 = "Check document in hand"
        elif "deed" in s["visual"].lower():
            part1 = "Old paper deed document"
        elif "màn hình" in s["visual"].lower():
            part1 = "Computer screen displaying content"
        elif "chìa" in s["visual"].lower():
            part1 = "Old brass key resting on surface"
        elif "bút" in s["visual"].lower():
            part1 = "Pen resting on paper document"
        elif "tủ" in s["visual"].lower():
            part1 = "Box on shelf or table"
        else:
            part1 = "Scene with quiet atmosphere"
    elif len(chars_list) == 1:
        char = chars_list[0]
        if "ky" in s["visual"].lower() or "sign" in s["visual"].lower():
            part1 = f"{char} signing paper document"
        elif "đọc" in s["visual"].lower() or "read" in s["visual"].lower():
            part1 = f"{char} reading paper document"
        elif "nói" in s["visual"].lower() or "speak" in s["visual"].lower():
            part1 = f"{char} speaking with serious expression"
        elif "ngồi" in s["visual"].lower():
            part1 = f"{char} sitting at desk"
        elif "đứng" in s["visual"].lower():
            part1 = f"{char} standing with steady posture"
        elif "nhìn" in s["visual"].lower():
            part1 = f"{char} looking outward"
        elif "lái" in s["visual"].lower() or "xe" in s["visual"].lower():
            part1 = f"{char} driving pickup truck"
        elif "cầm" in s["visual"].lower():
            part1 = f"{char} holding document"
        elif "đi" in s["visual"].lower():
            part1 = f"{char} walking steadily"
        elif "đặt tay" in s["visual"].lower():
            part1 = f"{char} placing hand gently"
        elif "mỉm cười" in s["visual"].lower():
            part1 = f"{char} smiling softly"
        elif "cúi" in s["visual"].lower():
            part1 = f"{char} looking down"
        else:
            part1 = f"{char} standing in scene"
    else:
        # Multiple characters
        part1 = f"{chars[0]} and {chars[1]} in scene"

    # Shot type
    shot = get_shot_type(s["visual"], beat)

    # Mood keywords
    mood_kw = mood_map[mood]

    # Style anchor (add flashback for George)
    style_anchor = style
    if "george" in chars_raw:
        style_anchor = style + flashback_style

    # Build prompt
    prompt = f"{part1}, {setting}, {shot}, {mood_kw}, {style_anchor}"

    # Append to output
    output.append(f"""---
## {stt}
**Beat:** {beat} | **Mood:** {mood} | **Duration:** {dur}s
**Characters:** {chars}
**Prompt:**
{prompt}
""")

# Write to file
with open("d:/wmg-yt-master-flow-v2/output/prompts.md", "a", encoding="utf-8") as f:
    f.write("".join(output))

print(f"Appended {len(output)} prompts to prompts.md")