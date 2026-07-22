#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder: sinh output/scene-breakdown.md từ SRT + SCENES plan.

Mỗi scene chỉ khai `f` = entry SRT bắt đầu; builder tự tính span = [f .. next.f-1],
timestamp lấy từ SRT → continuity end==start tự đảm bảo, không gap/overlap.
Nội dung (beat/mood/characters/description/visual notes) do người viết cho TỪNG scene —
builder chỉ làm số học + định dạng, KHÔNG sinh nội dung.

Project: The Kudzu Place (DLS_31) — Gilmer County, Georgia.
Lens đúng bảng Rule 4.8 (KAIZEN 2026-07-21: phải có chữ `lens`).
Quota mỗi thập kỷ (Rule 4.2): ≥2 wide, ≥3 medium, ≥2 close-up THẬT, ≥1 angle.

Chạy:  python3 scripts/build_breakdown.py          # ghi output/scene-breakdown.md
       python3 scripts/build_breakdown.py --check  # chỉ báo duration/beat/shot, không ghi file
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRT = ROOT / "input" / "subtitle.srt"
OUT = ROOT / "output" / "scene-breakdown.md"
TITLE = "The Kudzu Place — Corinne Ashbury's Four Growing Seasons"

BOUNDS = {"establishing": (10, 18), "dialogue": (6, 12), "emotional_peak": (10, 18),
          "tension": (5, 10), "reflection": (10, 18), "resolution": (12, 25)}


def parse_srt():
    t = SRT.read_text(encoding="utf-8")
    ent = {}
    for b in re.split(r"\n\s*\n", t.strip()):
        ls = b.strip().split("\n")
        if len(ls) < 2:
            continue
        m = re.search(r"(\d\d):(\d\d):(\d\d),\d\d\d\s*-->\s*(\d\d):(\d\d):(\d\d),(\d\d\d)", ls[1])
        if not m:
            continue
        ent[int(ls[0])] = (int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]),
                           int(m[4]) * 3600 + int(m[5]) * 60 + int(m[6]) + (1 if int(m[7]) >= 500 else 0))
    return ent


def fmt(s):
    return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}"


def shot_cat(v):
    v = v.lower()
    if re.search(r"over-shoulder|low angle|high angle", v):
        return "angle"
    if "24mm" in v or "35mm lens" in v:
        return "wide"
    if "100mm macro" in v or "85mm portrait" in v:
        return "closeup"
    if "85mm lens" in v or "50mm lens" in v:
        return "medium"
    return "?"


# f=entry SRT bắt đầu, b=beat, m=mood, c=character ids, d=description (VN), v=visual notes
SCENES = [
# ===== HOOK / COLD OPEN (0:00 - 1:38) =====
{"f":1,"b":"establishing","m":"dismissive","c":[],"d":"Hạt rao bán cùng một thửa 104 mẫu ba lần; ba lần bậc thềm tòa án lặng đi khi người điều phối hỏi giá mở đầu","v":"extreme wide shot, 24mm wide-angle lens, bậc thềm tòa án đá xám với nhóm đàn ông đứng im không ai giơ tay"},
{"f":3,"b":"dialogue","m":"determined","c":["corinne"],"d":"Đến phiên thứ tư vào tháng Ba, một góa phụ ba mươi tám tuổi tên Corinne Ashbury giơ thẻ và nói chín mươi mốt nghìn bốn trăm đô","v":"medium shot, 50mm lens, Corinne đứng giữa đám đàn ông trên bậc thềm, tay giơ tấm thẻ đấu giá"},
{"f":5,"b":"tension","m":"sad","c":[],"d":"Con số đó gần bằng từng xu tiền bảo hiểm nhân thọ của chồng bà từng trả cho bà","v":"extreme close-up, 100mm macro lens, tấm séc bảo hiểm cũ nhàu nằm trên mặt bàn gỗ"},
{"f":7,"b":"establishing","m":"sad","c":[],"d":"Suốt hai mươi hai năm kudzu đã nuốt dần mảnh đất theo cách nước tù nuốt một cánh đồng trũng - đầu tiên là hàng rào, rồi nhà kho cỏ, rồi cả hình dáng những ngọn đồi","v":"extreme wide shot, 24mm wide-angle lens, sườn đồi phủ kín dây kudzu thành một làn sóng xanh liền mạch trùm qua hàng rào và mái kho"},
{"f":9,"b":"reflection","m":"sad","c":[],"d":"Cho tới khi cả thửa đất nhìn từ đường cao tốc chỉ còn là một làn sóng xanh dài đổi màu theo mùa mà không bao giờ đổi hình","v":"wide shot, 35mm lens, làn sóng kudzu xanh trải dọc theo đường cao tốc dưới trời cuối đông"},
{"f":11,"b":"reflection","m":"dismissive","c":[],"d":"Ai đó phía sau bật cười, rồi thêm hai người nữa; mọi người đàn ông trên bậc thềm đều từng đánh nhau với dây leo trên đất mình và biết câu chuyện đó kết thúc ra sao - thứ ngoài kia đã thôi là chuyện cỏ dại từ lâu, nó đã thành một vùng địa hình","v":"over-shoulder shot, 50mm lens, qua vai một người đàn ông nhìn nhóm người cười trên bậc thềm tòa án"},
{"f":14,"b":"emotional_peak","m":"shock","c":[],"d":"Không một ai trong phòng biết rằng dưới lớp dây leo còn chín cái cây đang sống, kể cả người phụ nữ vừa trả tiền mua chúng; ba tuần sau bà lùa tám mươi ba con dê xuống sườn đồi","v":"extreme close-up, 100mm macro lens, thân cây hồ đào nhợt lộ ra trong khoảng tối dưới tán dây leo dày"},
{"f":17,"b":"reflection","m":"hopeful","c":[],"d":"Trong sách Luca chương mười ba, chính Chúa kể về một cái cây ba năm không ra trái, và về người đã xin thêm một mùa nữa trước khi nó bị đốn hạ","v":"medium close-up, 85mm lens, bàn tay già lật một trang Kinh Thánh mỏng trên bàn gỗ"},
{"f":19,"b":"dialogue","m":"hopeful","c":[],"d":"Hãy để yên nó năm nay nữa, cho tới khi tôi xới quanh gốc và bón cho nó","v":"medium shot, 50mm lens, cuốn Kinh Thánh cũ mở trên bàn bếp cạnh cây đèn, một chiếc ghế trống bên cạnh"},
{"f":21,"b":"tension","m":"tense","c":["corinne"],"d":"Corinne Ashbury có ba mùa sinh trưởng - liệu chừng đó có đủ không; các phiên bán đất siết thuế ở Georgia vẫn diễn ra vào thứ Ba đầu tháng ngay trên bậc thềm tòa án","v":"close-up, 85mm portrait lens, gương mặt Corinne nhìn thẳng ra sườn đồi xanh, full head within frame"},
# ===== ACT 1 — Phiên đấu giá & người đàn bà định giá mất mát (1:43 - 5:14) =====
{"f":23,"b":"establishing","m":"calm","c":[],"d":"Thứ Ba tháng Ba năm đó gió thổi dọc con phố trước tòa án hạt Gilmer lạnh tới mức người điều phối phải dựng cổ áo lên mà đọc mô tả thửa đất","v":"wide shot, 35mm lens, quảng trường tòa án hạt gió lạnh tháng Ba với vài người đứng co ro"},
{"f":25,"b":"reflection","m":"dismissive","c":[],"d":"Những người đàn ông đứng đó cứ đút tay trong túi, mà đó cũng là một kiểu ra giá; tất cả đều biết thửa đất ấy và họ gọi nó là mảnh đất kudzu","v":"low angle shot, 50mm lens, nhìn chếch lên hàng người đàn ông đứng đút tay túi áo khoác trên bậc thềm"},
{"f":28,"b":"reflection","m":"sad","c":["corinne"],"d":"Corinne Ashbury đã có mười hai năm làm nhân viên định giá bồi thường ở Atlanta; công việc của bà là đứng trên lối vào nhà người khác sau tuần tệ nhất đời họ và viết xuống một con số cho những gì họ đã mất","v":"medium shot, 50mm lens, Corinne đứng trên lối xe vào một ngôi nhà lạ, kẹp hồ sơ và ghi chép"},
{"f":31,"b":"tension","m":"sad","c":["corinne"],"d":"Ba năm góa bụa; bà ghi lại mọi thứ và ít nói, còn người ta thường nhầm điều thứ hai thành điều thứ nhất","v":"medium close-up, 85mm lens, Corinne cúi ghi vào sổ tay, gương mặt kín tiếng"},
{"f":33,"b":"emotional_peak","m":"sad","c":["corinne"],"d":"Nolan Ashbury làm chồng bà mười một năm; ông mất vào một sáng tháng Giêng vì tim, trước khi xe cứu thương kịp lên tới đầu phố nhà họ","v":"close-up, 85mm portrait lens, gương mặt Corinne bất động dưới ánh sáng cửa sổ lạnh, full head within frame"},
{"f":35,"b":"tension","m":"sad","c":[],"d":"Và đó là tất cả, bởi bà chưa bao giờ kể câu chuyện ấy dài hơn thế với bất kỳ ai; thứ ông để lại là một đứa con trai và một tấm séc","v":"extreme close-up, 100mm macro lens, một tấm séc ngân hàng nằm cạnh chiếc nhẫn cưới bạc trên mặt bàn"},
{"f":37,"b":"reflection","m":"calm","c":["otis"],"d":"Đứa bé là Otis, tám tuổi, ngồi tránh gió ngoài hành lang tòa án với hộp bút chì đặt phẳng trên đầu gối, đang đếm ô trần nhà; cậu đếm mọi thứ theo cách những đứa trẻ khác ngân nga","v":"wide shot, 35mm lens, hành lang tòa án dài với một cậu bé nhỏ ngồi trên băng ghế gỗ, đầu ngẩng nhìn trần"},
{"f":40,"b":"establishing","m":"calm","c":[],"d":"Thửa đất là một trăm lẻ bốn mẫu phía đông ranh giới hạt, hồ sơ ghi không có công năng sản xuất; một thế hệ trước ai đó đã trồng kudzu trên bờ đường để giữ đất, việc mà người ta từng được khuyên phải làm","v":"extreme wide shot, 24mm wide-angle lens, bờ đường đất phủ dây kudzu chạy dài dọc con đường sỏi vắng"},
{"f":43,"b":"tension","m":"shock","c":[],"d":"Còn dây leo thì làm đúng điều người ta nhờ nó làm rồi cứ thế đi tiếp - hai mươi hai năm","v":"extreme close-up, 100mm macro lens, ngọn dây kudzu non bò vắt qua sợi dây thép gai gỉ"},
{"f":44,"b":"emotional_peak","m":"determined","c":["corinne"],"d":"Khi người điều phối hỏi giá mở đầu lần thứ tư, bà nói con số đó mà không cao giọng, và búa gõ xuống ở chín mươi mốt nghìn bốn trăm đô","v":"medium shot, 50mm lens, Corinne đứng thẳng giữa đám đông thưa trên bậc thềm với tấm thẻ đấu giá trong tay - replay scene 2"},
{"f":47,"b":"reflection","m":"reflection","c":["corinne"],"d":"Bà không mua nó để canh tác; suốt hai năm tháng nào bà cũng lái xe ngang bức tường dây leo ấy trên đường tới văn phòng bồi thường ở Ellijay","v":"over-shoulder shot, 50mm lens, qua vai Corinne đang lái xe, bức tường xanh trôi qua ngoài cửa kính"},
{"f":49,"b":"reflection","m":"determined","c":["corinne"],"d":"Rồi một thứ bị định giá bằng không bắt đầu trông giống một thứ chưa ai từng thật sự nhìn; đó không phải là nông nghiệp mà là một người đàn bà cả đời định giá mất mát, đi mua lấy mất mát lớn nhất hạt","v":"medium close-up, 85mm lens, Corinne ngồi trong cabin xe nhìn ra bức tường dây leo qua kính chắn gió"},
{"f":52,"b":"emotional_peak","m":"determined","c":[],"d":"Thứ bà có ngoài tờ chủ quyền là một tập giấy vàng lấy từ văn phòng bồi thường, một cột con số chạy dọc mép và chữ dê viết ngang đầu trang, gạch chân hai lần","v":"extreme close-up, 100mm macro lens, tập giấy vàng kẻ dòng với nét mực viết tay mờ và hai đường gạch chân đậm"},
{"f":54,"b":"tension","m":"determined","c":[],"d":"Dê ăn kudzu; dê còn thích ăn nó hơn thứ khác","v":"close-up, 85mm portrait lens, mõm một con dê đang kéo đứt chùm lá kudzu"},
{"f":55,"b":"reflection","m":"tense","c":["corinne"],"d":"Có một điều kiện, và bà hiểu rõ nó trước khi đặt bút ký: mảnh đất nằm dưới một giao ước sử dụng bảo tồn, thứ cho phép đất đang canh tác được đánh thuế như đất canh tác","v":"medium close-up, 85mm lens, bàn tay Corinne đặt trên xấp giấy tờ chuyển nhượng trên quầy gỗ"},
{"f":57,"b":"tension","m":"tense","c":[],"d":"Để giữ được nó bà phải chứng minh có canh tác nông nghiệp thật, và một thẩm định viên của hạt sẽ tự mình đi bộ khắp đám kudzu vào mùa xuân năm thứ tư - ba mùa sinh trưởng","v":"high angle shot, 50mm lens, nhìn xuống một đôi ủng cao su đứng trên thảm dây leo dày"},
{"f":59,"b":"tension","m":"tense","c":["corinne"],"d":"Nếu giao ước đứt, thuế truy thu và tiền phạt sẽ đến cùng một lúc, và không phiên bản nào trong phép tính của bà sống nổi qua chuyện đó","v":"close-up, 85mm portrait lens, gương mặt Corinne cúi đọc dòng điều khoản trong hợp đồng, full head within frame"},
{"f":61,"b":"reflection","m":"sad","c":[],"d":"Sau chín mươi mốt nghìn bốn trăm đô, sau các khoản phí và sang tên, phần còn lại chỉ đủ mua một rơ moóc chở gia súc cũ, một đôi giày đi học vào tháng Chín, và chưa tới một nửa số dê ghi trên tập giấy vàng","v":"wide shot, 35mm lens, một rơ moóc chở gia súc cũ đậu trong sân sỏi trống"},
{"f":64,"b":"emotional_peak","m":"determined","c":["corinne"],"d":"Bà ký tên mình, nhận chìa khóa một cánh cổng không ai mở suốt hai mươi hai năm, rồi lái xe về phía thứ duy nhất mà đường cao tốc cho bà thấy, đó là một màu duy nhất","v":"extreme wide shot, 24mm wide-angle lens, đồi kudzu một màu xanh trải kín tầm mắt nhìn từ mặt đường"},
{"f":67,"b":"tension","m":"sad","c":["corinne"],"d":"Nếu bạn từng bị người ta nói rằng thứ bạn muốn cứu không đáng để cứu, thì bạn đã biết chính xác bà cảm thấy thế nào khi ngồi trong chiếc xe tải đã tắt máy","v":"medium shot, 50mm lens, Corinne ngồi im sau vô lăng chiếc xe bán tải tắt máy trước cổng"},
# ===== ACT 2 — Đi vào dưới tán & đàn dê đầu tiên (5:14 - 8:00) =====
{"f":70,"b":"establishing","m":"determined","c":["corinne","otis"],"d":"Lần đi vào đầu tiên chỉ được bốn trăm thước trong cả một buổi chiều; dây leo đã trùm qua hàng rào và biến hàng rào thành một bức tường, nên bà chui vào đúng chỗ một con nai vẫn chui","v":"wide shot, 35mm lens, bức tường dây kudzu cao trùm kín hàng rào với một lỗ hổng thấp do thú rừng tạo"},
{"f":72,"b":"reflection","m":"calm","c":["corinne","otis"],"d":"Bà bò bằng tay và đầu gối, Otis theo sau; dưới lớp lá trời mát và tối, một trần xanh cao sáu mét ở nhiều chỗ giữ hết ánh sáng lại bên ngoài","v":"medium shot, 50mm lens, hai mẹ con bò dưới vòm dây leo tối với vài tia sáng lọt qua"},
{"f":74,"b":"tension","m":"nostalgic","c":[],"d":"Không khí có mùi lá ướt và mùi mục, và một lần, mùi khô ngọt như vỏ hạt hồ đào sau cơn mưa","v":"extreme close-up, 100mm macro lens, vỏ hạt hồ đào nứt đôi nằm trên nền lá mục ẩm"},
{"f":76,"b":"dialogue","m":"calm","c":["corinne","otis"],"d":"Bà tìm ra nhà kho cỏ bằng cách đi thẳng vào nó; Otis tìm được mười một cọc rào và báo lại con số","v":"medium close-up, 85mm lens, Otis đứng cạnh một cọc rào gỗ vừa lộ ra dưới đám dây leo bị vén"},
{"f":78,"b":"establishing","m":"sad","c":["corinne"],"d":"Từ đỉnh dốc cả mảnh đất hiện ra cùng một lúc, và chính đó là vấn đề: một trăm lẻ bốn mẫu kudzu đọc ra như một vật thể duy nhất, mà trên một vật thể duy nhất thì không có chỗ nào để bắt đầu","v":"extreme wide shot, 24mm wide-angle lens, toàn cảnh đồi kudzu nhìn từ đỉnh dốc, một khối xanh liền không đường nét"},
{"f":81,"b":"establishing","m":"calm","c":["burl"],"d":"Burl Tannehill bảy mươi mốt tuổi, đã nuôi dê trên dải đồi đó từ đời ông nội ông, và là người duy nhất trong hạt không cười","v":"medium close-up, 85mm lens, Burl đứng bên hàng rào dây thép, mũ lưỡi trai bạc màu và áo khoác vải bạt"},
{"f":83,"b":"dialogue","m":"calm","c":["burl","corinne"],"d":"Ông kể cho bà nghe dê làm gì, là gặm ngước lên và ra ngoài, ăn lá ăn dây ăn cả vỏ, và dê không làm gì, là bất cứ điều gì mà người ta trông cậy vào","v":"over-shoulder shot, 50mm lens, qua vai Corinne nhìn Burl đang nói bên hàng rào"},
{"f":85,"b":"dialogue","m":"determined","c":["burl","corinne"],"d":"Ông bán cho bà tám mươi ba con với cái giá công bằng cho cả hai và hào phóng với không bên nào; ông cũng đưa bà một chiếc chuông đồng buộc trên dây da đã mòn","v":"extreme close-up, 100mm macro lens, chiếc chuông đồng cũ trên dây da mòn nằm trong lòng hai bàn tay"},
{"f":87,"b":"dialogue","m":"hopeful","c":["burl","pepper"],"d":"Con dê đầu đàn là Pepper, mõm đã xám, bước xuống khỏi rơ moóc như thể nó sở hữu chỗ đó và cả đàn đi theo; trong sương mù, Burl nói, mắt chẳng giúp được ai, nhưng tai thì vẫn còn dùng được","v":"medium shot, 50mm lens, Pepper bước xuống cầu rơ moóc kim loại, đàn dê chen theo phía sau"},
{"f":90,"b":"reflection","m":"determined","c":["burl","corinne"],"d":"Họ căng lưới điện và chia sườn đồi gần thành các paddock bốn mẫu; tám tới mười con dê một mẫu, ông nói, và chuyển chúng đi trước khi chúng thấy chán","v":"high angle shot, 50mm lens, nhìn xuống các ô lưới điện chia sườn đồi thành từng mảng vuông"},
{"f":92,"b":"emotional_peak","m":"hopeful","c":["corinne","pepper"],"d":"Tuần cuối tháng Ba bà mở cổng và tám mươi ba con dê tràn xuống đám dây leo; âm thanh không giống thứ bà tưởng tượng, nó đều, khô và khổng lồ","v":"wide shot, 35mm lens, đàn dê tràn xuống sườn đồi phủ kudzu qua cánh cổng mở"},
{"f":94,"b":"tension","m":"calm","c":["pepper"],"d":"Hàng trăm chiếc lá cùng lúc, và đâu đó bên trong tiếng động ấy, đang di chuyển, là tiếng chuông","v":"extreme close-up, 100mm macro lens, chiếc chuông đồng lắc trên cổ một con dê giữa đám lá kudzu"},
{"f":95,"b":"establishing","m":"dismissive","c":["merle"],"d":"Merle Yates canh tác hai trăm mẫu dọc ranh phía tây đất bà, năm mươi sáu tuổi, ồn ào, không phải người ác; ông tin vào những gì chính mắt mình đã thấy","v":"medium shot, 50mm lens, Merle đứng cạnh chiếc xe bán tải bên vệ đường, mũ hạt giống xanh trên đầu"},
{"f":97,"b":"dialogue","m":"dismissive","c":["merle"],"d":"Và thứ ông đã thấy là kudzu sống dai hơn một máy phát cỏ, một máy ủi và hai công ty hóa chất","v":"over-shoulder shot, 50mm lens, qua vai Merle nhìn qua cánh cổng vào đàn dê đang gặm trên sườn đồi"},
{"f":98,"b":"dialogue","m":"dismissive","c":["merle","corinne"],"d":"Ông dừng xe ở cổng nhà bà và nhìn đàn dê một lúc lâu rồi hỏi con nào hết trước, đám kudzu đó hay tiền của cô","v":"close-up, 85mm portrait lens, gương mặt Merle nói qua khung cửa kính xe hạ xuống, full head within frame"},
# ===== ACT 2B — Rễ chưa chết, cái giếng, và chín thân cây (7:42 - 12:37) =====
{"f":100,"b":"reflection","m":"calm","c":["corinne"],"d":"Giữa tháng Tư bà đi vào một paddock mà đàn dê đã gặm trụi mười một ngày trước đó; mặt đất khi ấy đã lộ ra, chính bà đã nhìn thấy lớp đất trần","v":"wide shot, 35mm lens, một ô paddock trơ đất đỏ với gốc dây leo bị gặm sát và lưới điện vây quanh"},
{"f":102,"b":"tension","m":"shock","c":[],"d":"Giờ đây mọc xuyên lên qua lớp đất ấy, thành những hàng đều tăm tắp chạy xuống mặt dốc, là những chồi non cao tới mắt cá chân","v":"medium close-up, 85mm lens, những chồi kudzu non cao tới mắt cá mọc thành hàng đều trên mặt đất đỏ"},
{"f":103,"b":"emotional_peak","m":"shock","c":[],"d":"Kudzu chưa hề bị giết, nó chỉ bị cắt ngọn; dưới mỗi thân cây, bầu rễ nằm trong đất như một nắm tay siết chặt, hai mươi hai năm đường tích trữ","v":"extreme close-up, 100mm macro lens, bầu rễ kudzu phình to như nắm tay lộ ra trong hố đất mới đào"},
{"f":105,"b":"reflection","m":"determined","c":["corinne"],"d":"Còn đàn dê thì mới chỉ lấy phần ngọn; hai mùa, Burl nói qua điện thoại, có thể là ba - gặm nó, để nó mọc lại, rồi gặm nữa, cho tới khi bộ rễ tiêu hết thứ nó đã dành dụm","v":"medium close-up, 85mm lens, Corinne áp ống nghe điện thoại bàn bên khung cửa sổ bếp"},
{"f":108,"b":"emotional_peak","m":"shock","c":[],"d":"Chuyện kia xảy ra ngay trong tuần đó: có một cái giếng đào tay cũ dưới nhà kho, không nằm trên bản đồ thửa nào, và dây leo đã mọc thành một cái nắp ngang miệng giếng trông y hệt mặt đất - một con dê tơ lọt xuống","v":"high angle shot, 50mm lens, nhìn xuống miệng giếng đá thủng một lỗ tối giữa thảm dây leo"},
{"f":111,"b":"emotional_peak","m":"sad","c":["corinne","burl"],"d":"Họ làm việc tới quá tối với dây thừng và một chiếc đèn, Burl cũng tới, và vẫn không đủ, và gần nửa đêm ông đặt bàn tay lên chiếc tời rồi gọi tên bà một lần, rất khẽ","v":"medium shot, 50mm lens, hai người đứng bên miệng giếng dưới quầng đèn pin trong đêm tối"},
{"f":113,"b":"reflection","m":"sad","c":["corinne"],"d":"Sáng hôm sau họ lấp cái giếng bằng đá và đất sét; đêm đó bà ngồi ở bàn bếp với cuốn sổ cái từ công việc cũ, thứ sinh ra để ghi lại một mất mát đáng giá bao nhiêu, và lần này bà không biết viết gì vào cột bên phải","v":"medium close-up, 85mm lens, Corinne ngồi trước cuốn sổ mở dưới đèn bếp, cây bút dừng lại giữa chừng"},
{"f":117,"b":"tension","m":"hopeful","c":[],"d":"Tới tuần cuối tháng Mười, sườn phía đông đã bị ăn xuống tới đúng hình dáng của mặt đất bên dưới nó","v":"extreme wide shot, 24mm wide-angle lens, sườn đồi phía đông lộ nguyên hình đất dưới nắng cuối thu"},
{"f":119,"b":"establishing","m":"calm","c":[],"d":"Đàn dê đã làm sườn đồi đó theo vòng quay từ tháng Tám, bốn paddock, chuyển mỗi chín ngày, và thứ chúng để lại trông ít giống một đồng cỏ hơn là một căn phòng vừa bị bóc hết giấy dán tường","v":"wide shot, 35mm lens, sườn đồi trơ với các vệt paddock nối nhau xuống chân dốc"},
{"f":121,"b":"reflection","m":"calm","c":["corinne"],"d":"Corinne đi trên đó vào một sáng thứ Ba khi sương giá còn đọng lại ở các chỗ trũng; dây leo chết treo trên dây rào thành những sợi thừng xám khô","v":"close-up, 85mm portrait lens, gương mặt Corinne trong buổi sáng sương giá với hơi thở trắng, full head within frame"},
{"f":123,"b":"emotional_peak","m":"shock","c":["corinne"],"d":"Và mọc thẳng lên từ mặt đất bị gặm nát, nhợt màu, to hơn cả vòng tay bà ôm, là những thân cây; bà đã đi ngang chúng suốt cả mùa hè","v":"low angle shot, 50mm lens, nhìn ngước lên một thân cây hồ đào cao vút trên nền trời sáng"},
{"f":126,"b":"tension","m":"reflection","c":[],"d":"Dưới trần lá xanh chúng chỉ là những hình khối trong một bức tường lá, không khác gì chiếc máng lùa bò cũ, không khác gì cái giếng mà dây leo đã che kín cho tới khi một con dê tìm ra nó","v":"medium close-up, 85mm lens, hình khối mờ của thân cây chìm sau lớp lá dày"},
{"f":128,"b":"tension","m":"shock","c":["corinne"],"d":"Bà đếm chúng hai lần, lần thứ hai vừa đếm vừa đặt bàn tay lên từng thân cây - chín cây","v":"extreme close-up, 100mm macro lens, bàn tay áp lên lớp vỏ cây nhợt sần sùi"},
{"f":130,"b":"emotional_peak","m":"vindication","c":["burl","corinne"],"d":"Burl lên dốc chiều hôm đó, áp lòng bàn tay lên vỏ cây và nói ra cái tên trước khi bà kịp hỏi - hồ đào, mà không phải cây non; ông bước đo khoảng cách giữa hai cây đầu, bốn mươi bộ, rồi hai cây tiếp, lại bốn mươi bộ","v":"medium shot, 50mm lens, Burl bước sải đo khoảng cách giữa hai thân cây trên sườn đồi"},
{"f":133,"b":"reflection","m":"nostalgic","c":[],"d":"Và cái lưới ô vuông ấy chạy tiếp vào trong đám dây leo nơi khoảng quang dừng lại; ai đó đã trồng một vườn cây trên ngọn đồi này rồi bỏ đi, còn những cái cây thì cứ đứng trong bóng tối suốt hai mươi hai năm","v":"extreme wide shot, 24mm wide-angle lens, hàng thân cây thẳng lối chạy vào bức tường dây leo phía xa"},
{"f":136,"b":"reflection","m":"nostalgic","c":[],"d":"Bởi một cây hồ đào có thể sống quá trăm tuổi và chẳng bận tâm gì tới kế hoạch của kẻ đã đặt nó xuống đó; gió lên dốc mang theo mùi vỏ hạt","v":"wide shot, 35mm lens, tán cây hồ đào rộng vươn trên nền trời tháng Mười"},
{"f":139,"b":"emotional_peak","m":"tense","c":["burl"],"d":"Cái mùi vỏ xanh gắt ấy - đàn dê đã để lại những mảnh vỏ hồ đào nứt đúng chỗ chúng rơi; rồi Burl ngồi thụp xuống","v":"extreme close-up, 100mm macro lens, những mảnh vỏ hồ đào nứt đôi nằm trên mặt đất bị gặm trụi"},
{"f":142,"b":"emotional_peak","m":"shock","c":[],"d":"Quanh gốc cây gần nhất, ở khoảng chiều cao vai một con dê, lớp vỏ đã biến mất - không phải bị cào, mà bị lấy đi thành một vành sạch chạy trọn vòng quanh thân, xuống tới lớp gỗ ướt nhợt","v":"extreme close-up, 100mm macro lens, vành vỏ cây bị gặm trụi quanh thân để lộ lớp gỗ ướt nhợt"},
{"f":145,"b":"reflection","m":"tense","c":[],"d":"Một cái cây tự nuôi mình qua một lớp sống mỏng ngay dưới vỏ; cắt đứt vành đó trọn vòng thì không còn gì đi lại được giữa lá và rễ nữa, và cây vẫn đứng suốt mùa đông trông y như một cái cây","v":"medium close-up, 85mm lens, thân cây mất vành vỏ trong khi tán lá phía trên vẫn còn nguyên"},
{"f":148,"b":"tension","m":"sad","c":[],"d":"Nó thậm chí còn ra lá thêm một mùa xuân nữa bằng thứ đã tích trữ, rồi chết với cành đầy lá; ba trong chín cây bị khoanh gần trọn vòng, một cây bị khoanh trọn","v":"wide shot, 35mm lens, chín thân cây hồ đào đứng rải trên sườn đồi trơ dưới trời xám"},
{"f":150,"b":"dialogue","m":"sad","c":["burl"],"d":"Chúng không phân biệt được, Burl nói; một con dê không biết đâu là thứ người ta thả nó ra để ăn và đâu là thứ người ta đánh đổi mọi giá để giữ - với nó tất cả đều là vỏ cây","v":"over-shoulder shot, 50mm lens, qua vai Burl nhìn về phía đàn dê đang gặm phía dưới dốc"},
{"f":153,"b":"reflection","m":"determined","c":["corinne"],"d":"Sửa chuyện đó khiến bà tốn kém gấp đôi: những ống lưới thép hàn quây quanh cả chín thân cây, đóng cọc thật sâu, cao tới mức một con dê cái đứng bằng hai chân sau cũng không với qua nổi","v":"medium shot, 50mm lens, ống lưới thép hàn quây kín quanh một thân cây hồ đào, cọc đóng sâu xuống đất"},
{"f":155,"b":"tension","m":"tense","c":[],"d":"Và đó là khoản tiền đã hứa cho cỏ khô mùa đông; hàng rào cách ly quanh vườn cây kéo bốn mẫu ra khỏi vòng quay, mà đó đúng là bốn mẫu đàn dê đang dọn nhanh nhất","v":"high angle shot, 50mm lens, nhìn xuống hàng rào cách ly quây một khoảnh vườn cây tách khỏi các paddock"},
{"f":157,"b":"tension","m":"tense","c":[],"d":"Mỗi ngày đàn dê ở một chỗ khác là một ngày kudzu trên sườn đồi đó đứng dậy lại được","v":"extreme close-up, 100mm macro lens, những chồi kudzu mới bò trở lại trên nền đất trơ"},
{"f":159,"b":"emotional_peak","m":"determined","c":["corinne","otis"],"d":"Bà vẫn dựng nó, suốt tháng Mười Một, phần lớn là dưới mưa, với Otis đưa lên từng cái đinh bấm một","v":"medium shot, 50mm lens, hai mẹ con dựng hàng rào lưới trong mưa, cậu bé đưa đinh bấm lên"},
{"f":161,"b":"reflection","m":"hopeful","c":["otis"],"d":"Cậu đặt tên cho cây to nhất là Big Tuesday, vì thứ Ba là ngày họ tìm ra nó; mùa thu ấy cậu chín tuổi, và chừng đó là đủ lý do","v":"low angle shot, 50mm lens, Otis đứng nhỏ bé dưới tán cây hồ đào lớn nhất nhìn ngược lên"},
{"f":163,"b":"tension","m":"hopeful","c":["corinne"],"d":"Chín cái cây đó chưa cho bà một hạt nào; thứ chúng cho bà là một lý do để không bán mảnh đất vào mùa đông ấy","v":"close-up, 85mm portrait lens, gương mặt Corinne ngước nhìn lên tán cây, full head within frame"},
# ===== ACT 3 — Đất nói ra sự thật (12:46 - 15:12) =====
{"f":165,"b":"reflection","m":"reflection","c":[],"d":"Mảnh đất như thế - bị xóa sổ, bị phủ kín, ba lần rao bán mà không ai mua - nằm ở gần như mọi hạt trên đất nước này, và bất cứ thứ gì đang đứng dưới nó thì đã đứng đó một thời gian rồi","v":"extreme wide shot, 24mm wide-angle lens, đồi kudzu trải dài tới chân trời dưới ánh chiều"},
{"f":169,"b":"establishing","m":"calm","c":["nadine"],"d":"Tiến sĩ Nadine Croft lái xe ra vào thứ Năm thứ hai của tháng Giêng với một cây khoan lấy mẫu đất lạch cạch trong thùng xe; bà là cán bộ khuyến nông của hạt, ngoài bốn mươi","v":"medium shot, 50mm lens, cây khoan lấy mẫu đất dựng trong thùng chiếc xe bán tải đỗ trên đường sỏi mùa đông"},
{"f":172,"b":"reflection","m":"determined","c":["nadine","corinne"],"d":"Lớn lên ở một trang trại bò sữa cách một hạt về phía đông, công việc của bà là nói cho nông dân sự thật về lớp đất của họ dù họ có muốn nghe hay không; Corinne đã gọi hồi tháng Mười rồi tháng Mười Một mà không đi tới đâu, cho tới khi bà thôi xin một ý kiến và đặt mua một kết quả xét nghiệm","v":"medium shot, 50mm lens, Nadine và Corinne đứng nói chuyện bên thùng xe bán tải giữa đồng"},
{"f":175,"b":"dialogue","m":"determined","c":["nadine","corinne"],"d":"Giấy có tiêu đề là thứ ngôn ngữ duy nhất mà tòa án hạt từng biết nói; họ lấy mẫu lõi đất suốt cả buổi sáng","v":"extreme close-up, 100mm macro lens, ống khoan rút lên một lõi đất nguyên vẹn còn dính rễ"},
{"f":178,"b":"tension","m":"calm","c":["nadine","corinne"],"d":"Mười lăm mẫu lấy từ các paddock đàn dê đã gặm hai lượt, mười lăm mẫu từ một dải đất dọc hàng rào phía bắc vẫn còn bị nhốt dưới trần lá xanh; báo cáo đất về vào tuần đầu tháng Hai","v":"medium close-up, 85mm lens, hai hàng ống mẫu đất xếp ngay ngắn trên thành thùng xe"},
{"f":181,"b":"emotional_peak","m":"vindication","c":[],"d":"Chất hữu cơ trong paddock đã gặm đạt ba phẩy một phần trăm, còn ở dải đất chưa động tới là hai phẩy bốn; đạm nitrat trở về ở mức hai mươi sáu phần triệu so với mười tám","v":"extreme close-up, 100mm macro lens, hai nắm đất khác màu rõ rệt đặt cạnh nhau trên mặt bàn sáng"},
{"f":184,"b":"reflection","m":"vindication","c":[],"d":"Tám mươi hai con dê đi qua một sườn đồi suốt cả mùa hè đã trả lại cho lớp đất đó nhiều hơn thứ bà có thể chở tới bằng xe tải; phần đó thì bà đã hy vọng từ trước","v":"wide shot, 35mm lens, đàn dê rải rác gặm trên sườn đồi đã dọn quang dưới nắng"},
{"f":187,"b":"dialogue","m":"shock","c":["nadine","corinne"],"d":"Nadine lật mặt sau tờ giấy, đặt ngón tay lên cột đối chứng và nói đó mới là con số đáng nhìn - với lớp đất chưa hề có cày, có bò hay có phân bón từ trước khi Corinne lấy chồng, hàm lượng đạm không có lý do gì cao đến thế","v":"over-shoulder shot, 50mm lens, qua vai Corinne nhìn ngón tay Nadine chỉ xuống một cột trên tờ báo cáo"},
{"f":190,"b":"reflection","m":"vindication","c":[],"d":"Kudzu là cây họ đậu, cùng họ với đậu và đậu Hà Lan đồng; dưới rễ nó mang những nốt sần vi khuẩn kéo đạm từ không khí xuống và cố định vào trong đất","v":"extreme close-up, 100mm macro lens, chùm rễ kudzu với các nốt sần nhỏ bám dày dọc rễ"},
{"f":192,"b":"emotional_peak","m":"vindication","c":[],"d":"Và kudzu đã làm đúng việc đó trên khắp một trăm lẻ bốn mẫu, mỗi mùa, không ngừng nghỉ - hai mươi hai năm","v":"extreme wide shot, 24mm wide-angle lens, toàn cảnh thửa đất một trăm lẻ bốn mẫu nhìn từ trên cao"},
{"f":195,"b":"tension","m":"shock","c":["corinne"],"d":"Thứ đã làm cho mảnh đất trở nên vô giá trị hóa ra đã nuôi chính mảnh đất ấy suốt từng ấy thời gian","v":"close-up, 85mm portrait lens, gương mặt Corinne khi vừa nghe ra điều đó, full head within frame"},
{"f":198,"b":"reflection","m":"determined","c":["corinne"],"d":"Corinne bắt đầu một cuốn sổ cái đúng nghĩa vào mùa đông ấy - ngày tháng, số hiệu paddock, số ngày gặm, thứ đàn dê không chịu ăn; mười hai năm định giá mất mát của người khác đã khiến bà giỏi đúng một việc, và giờ thứ được đo đếm là của chính bà","v":"medium close-up, 85mm lens, Corinne viết vào cuốn sổ cái mới dưới ánh đèn bếp ấm"},
# ===== ACT 4 — Mùa đông cạn tiền & cuộc rút lui của dây leo (15:12 - 19:05) =====
{"f":201,"b":"reflection","m":"sad","c":["corinne"],"d":"Tiền cứ chảy ra mà không có gì chảy vào: sáu trăm đô tiền cỏ khô tháng Chạp, một cuộc gọi thú y lúc hai giờ sáng cho con dê cái bị viêm phổi","v":"medium shot, 50mm lens, Corinne trong chuồng ban đêm với đèn pin bên một con dê nằm bệt"},
{"f":203,"b":"reflection","m":"sad","c":[],"d":"Khoáng, dầu diesel, dây thép, một bộ kích điện hàng rào mới sau khi sét đánh hỏng cái cũ; Otis thì đã học đếm được tới tám mươi hai","v":"low angle shot, 50mm lens, cọc rào với bộ kích điện mới gắn, nhìn chếch lên nền trời mùa đông xám"},
{"f":205,"b":"tension","m":"sad","c":["otis"],"d":"Cậu đếm tới tám mươi hai rồi đếm ngược lại, đọc to ở cổng vào mỗi tối; cậu học con số ấy đúng vào tuần họ lấp cái giếng, và chưa một lần nào cậu đếm tới con số kia","v":"close-up, 85mm portrait lens, Otis đứng ở cổng đếm đàn dê trong ánh chiều, full head within frame"},
{"f":207,"b":"emotional_peak","m":"sad","c":["corinne"],"d":"Một buổi chiều trong nhà kho, khi đi tìm cái kìm rào, bà kéo tấm bạt ra và thấy hộp đồ nghề của Nolan - màu xanh, móp, một mảnh băng dính dán ngang nắp","v":"extreme close-up, 100mm macro lens, hộp đồ nghề kim loại xanh móp với mảnh băng dính bạc màu dán ngang nắp"},
{"f":209,"b":"emotional_peak","m":"sad","c":["corinne"],"d":"Những đầu khẩu vẫn nằm đúng thứ tự ông để lại; bà đóng nắp hộp, đặt nó trở lại lên kệ, rồi làm nốt hàng rào bằng cái kìm bà đang có","v":"medium close-up, 85mm lens, bàn tay đóng nắp hộp đồ nghề rồi đặt lên kệ gỗ trong nhà kho tối"},
{"f":211,"b":"reflection","m":"calm","c":["burl","corinne"],"d":"Cuối tháng Burl ghé qua với một bao khoáng mà ông bảo là mua nhầm; kẹp dưới nách ông là một cuốn Kinh Thánh đen, bìa đã mềm như vải","v":"wide shot, 35mm lens, Burl bước qua khung cửa bếp với bao khoáng trên vai và một cuốn sách kẹp dưới nách"},
{"f":213,"b":"reflection","m":"nostalgic","c":["burl","corinne"],"d":"Nó từng là của vợ ông; ông đặt nó lên bàn bếp, mở tới một trang bà ấy đã đánh dấu bằng bút chì nhiều năm trước, rồi cứ để nó mở ra như thế trong lúc nói chuyện giá cỏ khô","v":"high angle shot, 50mm lens, nhìn xuống cuốn Kinh Thánh cũ mở trên bàn bếp cạnh hai tách cà phê"},
{"f":215,"b":"dialogue","m":"hopeful","c":[],"d":"Ta sẽ đền bù cho các ngươi những năm mà cào cào đã ăn mất","v":"extreme close-up, 100mm macro lens, ngón tay già đặt trên mép một trang giấy mỏng có vệt chì mờ"},
{"f":217,"b":"reflection","m":"tense","c":["burl"],"d":"Ông cầm cái bao rỗng theo khi ra về; hạt sẽ tới đi bộ trên mảnh đất này vào mùa xuân năm sau nữa và ghi nó xuống là một nông trại đang hoạt động hoặc là không gì cả","v":"medium shot, 50mm lens, Burl đi ngang sân với chiếc bao rỗng trên tay, cổng trang trại phía sau"},
{"f":220,"b":"tension","m":"tense","c":[],"d":"Hai mùa sinh trưởng - đó là tất cả những gì bà đã mua; tới tháng Hai, thứ duy nhất trên mảnh đất chưa cạn kiệt là đám dây leo","v":"extreme wide shot, 24mm wide-angle lens, sườn đồi tháng Hai xám với những mảng kudzu khô còn bám lại"},
{"f":222,"b":"tension","m":"tense","c":["corinne"],"d":"Và thứ đang cạn nhanh hơn cả tiền của bà là các mùa; âm thanh lên tới sống đồi trước cả ánh sáng","v":"medium shot, 50mm lens, Corinne đứng ở đỉnh đường cắt phía đông khi trời còn chưa sáng hẳn"},
{"f":224,"b":"establishing","m":"hopeful","c":["corinne"],"d":"Tuần cuối tháng Sáu của mùa hè thứ hai, Corinne đứng trên đỉnh đường cắt phía đông và nghe cả đàn ăn; một đàn dê làm việc trên sườn kudzu tạo ra thứ gần giống tiếng mưa trên mái nhà cách đó hai cánh đồng","v":"extreme wide shot, 24mm wide-angle lens, đàn dê rải khắp sườn đồi kudzu trong ánh bình minh"},
{"f":227,"b":"reflection","m":"calm","c":[],"d":"Chỗ lá còn dày thì tiếng xé chạy liền vào nhau, chỗ dốc đang mở ra thì tiếng rời rạc; mùa hè đó là lượt gặm thứ ba trên đường cắt phía đông","v":"medium close-up, 85mm lens, lá kudzu bị kéo đứt trong miệng một con dê đang gặm"},
{"f":230,"b":"reflection","m":"determined","c":[],"d":"Và là lượt thứ tư trên sườn nhà kho; lượt gặm đầu lấy lá, lượt thứ hai lấy thứ cây đẩy lên để thay phần lá đã mất","v":"high angle shot, 50mm lens, nhìn xuống một mảng dốc nửa đã trơ nửa còn phủ lá"},
{"f":232,"b":"emotional_peak","m":"determined","c":[],"d":"Lượt thứ ba và thứ tư lấy đi thứ cây không thể để mất, bởi mỗi tán lá mới đều được trả bằng đường tích dưới lòng đất, mà cái túi đó chỉ sâu đến thế thôi","v":"extreme close-up, 100mm macro lens, bầu rễ kudzu teo lại lộ ra trong hố đất mới xắn"},
{"f":235,"b":"emotional_peak","m":"vindication","c":["burl"],"d":"Tới tháng Tám kudzu mọc lại muộn, thưa và thấp, còn trên sườn nhà kho nó không bao giờ khép kín được qua hàng rào nữa; Burl đặt ủng lên nền đất đỏ chưa từng thấy ánh sáng ban ngày suốt hai mươi hai năm","v":"extreme close-up, 100mm macro lens, chiếc ủng da đặt trên nền đất đỏ vừa lộ ra dưới lớp dây leo"},
{"f":237,"b":"dialogue","m":"determined","c":["burl","corinne"],"d":"Ông gọi đó là cuộc rút lui, và dặn bà đừng gọi nó bằng từ nào mạnh hơn thế","v":"medium shot, 50mm lens, Burl và Corinne đứng cạnh nhau trên mảng đất đỏ vừa lộ ra"},
{"f":239,"b":"reflection","m":"hopeful","c":[],"d":"Hợp tác xã điện có mười một mẫu hành lang tuyến bị kudzu và gai phủ kín, quá dốc cho máy phát cỏ và quá gần dây điện sống cho tổ phun thuốc; sáu trăm đô một mẫu","v":"wide shot, 35mm lens, hành lang tuyến điện dốc đứng phủ dây leo chạy dưới đường dây cao thế"},
{"f":241,"b":"tension","m":"vindication","c":[],"d":"Dê được chở tới và cho uống nước bằng chi phí của bà - sáu nghìn sáu trăm đô, và lũ vật nuôi đã ăn hết cái hóa đơn đó","v":"medium close-up, 85mm lens, đàn dê bước xuống khỏi rơ moóc dưới chân một cột điện thép"},
{"f":243,"b":"reflection","m":"hopeful","c":[],"d":"Tháng Chín một hội mai táng phía nam Ellijay trả bảy trăm năm mươi đô một mẫu cho bốn mẫu đất bia mộ; tháng Mười hội đồng trường trả hai nghìn hai trăm cho bờ dốc sau sân bóng trường tiểu học","v":"wide shot, 35mm lens, đàn dê gặm giữa những hàng bia mộ đá cũ trong nghĩa trang"},
{"f":245,"b":"tension","m":"hopeful","c":["merle"],"d":"Và cho lớp ba ra ngoài xem đàn dê làm việc; Merle Yates đã lái xe ngang hàng rào đó suốt hai mùa mà không dừng lại","v":"medium shot, 50mm lens, lũ trẻ đứng sau hàng rào nhìn đàn dê gặm bờ dốc sau sân bóng"},
{"f":247,"b":"dialogue","m":"dismissive","c":["merle","corinne"],"d":"Tháng Chín đó ông tấp xe vào lề đường và bước xuống - tôi đã cười cô, ông nói","v":"over-shoulder shot, 50mm lens, qua vai Corinne nhìn Merle bước xuống từ xe bán tải đậu bên lề"},
{"f":249,"b":"dialogue","m":"sad","c":["merle"],"d":"Mọi người đàn ông ở cửa hàng thức ăn gia súc đều cười, và tôi cười to nhất, mà đó không phải ác ý; tôi đã thấy hai người đàn ông nhận mảnh đất đó","v":"close-up, 85mm portrait lens, gương mặt Merle bỏ mũ xuống khi nói, full head within frame"},
{"f":251,"b":"dialogue","m":"sad","c":["merle"],"d":"Một người phát cỏ một mùa rồi bỏ; một người thế chấp cả nhà mình, phun thuốc hai mùa rồi nhìn nó mọc lại dày hơn vào mùa xuân thứ ba - một người từng thấy hai người chìm thì không vỗ tay cho người thứ ba lội xuống","v":"medium shot, 50mm lens, Merle đứng bên hàng rào nói chuyện, đàn dê gặm phía sau lưng"},
{"f":253,"b":"emotional_peak","m":"vindication","c":["merle","corinne"],"d":"Rồi ông hỏi bà tính bao nhiêu một mẫu cho đàn dê, và ghi con số đó lên mặt sau một tờ biên lai thức ăn gia súc","v":"extreme close-up, 100mm macro lens, đầu bút chì ghi lên mặt sau một tờ biên lai nhàu nát"},
# ===== ACT 5 — Sương mù, cái tên đúng, và vườn cây năm thứ ba (19:26 - 24:25) =====
{"f":256,"b":"establishing","m":"tense","c":["corinne"],"d":"Sương mù tới vào tuần thứ hai của tháng Chín; bà lên đồi lúc rạng đông để chuyển lưới và thấy paddock trống trơn, cánh cổng bị húc mở, trắng xóa mọi hướng","v":"extreme wide shot, 24mm wide-angle lens, sườn đồi chìm trong sương mù trắng dày với cánh cổng lưới mở toang"},
{"f":258,"b":"reflection","m":"tense","c":["corinne"],"d":"Bà gọi, và sương mù trả lại tiếng bà một cách phẳng lì; nên bà thôi gọi và đứng yên - phía dưới bà chếch về bên trái, xa hơn bà đoán nhiều, là tiếng chuông","v":"medium close-up, 85mm lens, Corinne đứng yên trong sương mù, nghiêng đầu lắng nghe"},
{"f":260,"b":"emotional_peak","m":"hopeful","c":["corinne","pepper"],"d":"Bà đi về phía tiếng chuông theo cách người ta đi về phía một ngọn đèn hiên, và tìm thấy Pepper trong lùm cây thù du với cả đàn dê nằm quây quanh nó","v":"medium shot, 50mm lens, Pepper nằm giữa lùm cây thù du với đàn dê quây quanh trong sương mù"},
{"f":263,"b":"dialogue","m":"calm","c":["corinne","otis"],"d":"Trên đường từ chỗ làm ở trường về nhà, Otis, mười tuổi mùa thu đó, hỏi bà ghi gì lên hóa đơn - dọn bụi rậm, bà nói","v":"over-shoulder shot, 50mm lens, qua vai Otis trong cabin xe nhìn ra con đường quê phía trước"},
{"f":266,"b":"dialogue","m":"hopeful","c":["otis"],"d":"Cậu nghĩ về điều đó gần hết một dặm đường rồi nói không đúng đâu mẹ, mình có lấy gì đi khỏi nó đâu, mình chỉ đang trả nó lại thôi","v":"close-up, 85mm portrait lens, gương mặt Otis nhìn ra ngoài cửa kính xe, full head within frame"},
{"f":268,"b":"emotional_peak","m":"vindication","c":["corinne"],"d":"Đêm đó bà mở cuốn sổ cái từ công việc cũ, cuốn bà đã điền suốt mười hai năm bằng mất mát của người khác; lần đầu tiên kể từ phiên đấu giá, con số ở cột bên phải không còn dấu trừ đằng trước","v":"medium close-up, 85mm lens, Corinne ngồi trước cuốn sổ mở dưới đèn bàn, bàn tay đặt phẳng trên trang giấy"},
{"f":271,"b":"reflection","m":"reflection","c":[],"d":"Phần lớn thứ được bán ra dưới danh nghĩa tiến bộ chỉ là một kẻ đang vội; ngọn đồi đó hạ xuống được vì một người đàn bà từ chối vội vàng, mỗi lần một lượt gặm, trong khi cả hạt ngồi chờ bà bỏ cuộc","v":"wide shot, 35mm lens, sườn đồi đã dọn quang nhìn từ xa trong ánh chiều muộn"},
{"f":273,"b":"dialogue","m":"hopeful","c":[],"d":"Có một kiểu người nghe câu đi nhanh lên thì lại cố tình đi chậm lại - kênh này dựng cho họ, hãy đăng ký và ở lại với câu chuyện này","v":"medium shot, 50mm lens, con đường sỏi dẫn lên đồi trong ánh hoàng hôn ấm"},
{"f":275,"b":"reflection","m":"determined","c":["corinne"],"d":"Tới tháng Tư năm thứ ba, đường cắt phía đông đã mở đủ để trồng, và bà trồng một dải rộng bốn mươi bộ dài một phần tư dặm - đúng bằng thứ bà có thể tưới và trả tiền nổi","v":"wide shot, 35mm lens, một dải đất mới trồng chạy dài xuống sườn đồi đã dọn quang"},
{"f":278,"b":"reflection","m":"hopeful","c":["corinne","otis"],"d":"Ba mươi tám cây hồ đào non được trồng bằng tay, Otis thả một lá cờ nhỏ ở mỗi cọc; bà không mua một vườn cây mà mua một dải, đặt nó áp vào hàng rào của chín cây già, và tự nhủ sườn tiếp theo sẽ tới vào mùa xuân sang năm nếu đàn dê kiếm đủ","v":"medium shot, 50mm lens, Otis cắm lá cờ nhỏ bên một cọc cây non trong khi mẹ cậu trồng phía sau"},
{"f":281,"b":"reflection","m":"determined","c":["nadine","corinne"],"d":"Nadine Croft đã chỉ bà cách ghép nêm trên một chiếc ghế dài trong nhà kho cho tới khi tay bà thôi run; tháng Ba, trước khi chồi cựa mình, bà lấy cành ghép từ chín cây già","v":"extreme close-up, 100mm macro lens, hai bàn tay ghép nêm một cành hồ đào bằng con dao ghép sắc"},
{"f":283,"b":"emotional_peak","m":"hopeful","c":["corinne"],"d":"Và giữ nó ẩm và lạnh cho tới tháng Năm khi vỏ cây tuột ra; mọi cái cây bà đặt xuống mùa xuân đó đều mang gỗ của một trong chín cây kia","v":"medium close-up, 85mm lens, mối ghép quấn băng chặt trên thân một cây hồ đào non"},
{"f":285,"b":"emotional_peak","m":"vindication","c":[],"d":"Hai mươi hai năm những cây già đứng phủ kín mà không có gì để trưng ra; giờ chúng có con cái trên sườn đồi ngay phía dưới","v":"extreme wide shot, 24mm wide-angle lens, chín cây già trên đỉnh dốc và các hàng cây non trải phía dưới"},
{"f":288,"b":"tension","m":"reflection","c":["otis"],"d":"Không thứ nào trong đó sẽ nuôi được ai sớm cả - một cây hồ đào ghép cần sáu tới mười năm mới cho một vụ đáng chở tới trạm thu mua; vườn cây trên đường cắt phía đông thuộc về Otis năm hai mươi tuổi, không phải Otis mười tuổi","v":"low angle shot, 50mm lens, Otis đứng cạnh một cây non chỉ cao ngang vai cậu, trời rộng phía sau"},
{"f":290,"b":"emotional_peak","m":"tense","c":["corinne"],"d":"Tuần cuối tháng Năm khô hạn và cứ thế khô mãi - ba mươi mốt ngày không mưa, và đầu dải phía sống đồi lại nằm trên lớp đất mỏng nhất mảnh đất; bà chở nước bằng bồn hai trăm ga lông, hai chuyến một ngày, rồi ba","v":"wide shot, 35mm lens, xe bán tải chở bồn nước lăn bánh trên dải đất khô nứt giữa hàng cây non"},
{"f":293,"b":"tension","m":"sad","c":[],"d":"Tới tháng Bảy, mười một trong ba mươi tám cây đã nâu tới tận mối ghép, và không ai cãi được với một cây hồ đào đã chết; bà trồng lại vào tháng Mười Một và nói rất ít về chuyện đó","v":"extreme close-up, 100mm macro lens, một cây non khô nâu với mối ghép nứt toác trên nền đất khô"},
{"f":295,"b":"establishing","m":"tense","c":["dean"],"d":"Tháng Mười một chiếc sedan trắng của hạt chạy chậm dọc con đường phía trên cổng, rồi chậm hơn nữa, rồi không dừng lại; Dean Whitcomb bốn mươi bốn tuổi, thẩm định viên của hạt Gilmer","v":"wide shot, 35mm lens, chiếc sedan trắng của hạt bò chậm trên con đường phía trên cổng trang trại"},
{"f":297,"b":"reflection","m":"tense","c":["dean"],"d":"Người mà chữ ký của ông quyết định một trăm lẻ bốn mẫu là một nông trại hay chỉ là đất, và quyết định Corinne giữ được mức thuế nông nghiệp bà đã ký hay nợ hạt phần chênh lệch","v":"medium close-up, 85mm lens, Dean ngồi trong xe ghi lên tấm kẹp hồ sơ tì trên vô lăng"},
{"f":299,"b":"tension","m":"dismissive","c":["dean"],"d":"Ông viết lên tấm kẹp hồ sơ tì vào vô lăng rồi lái đi mà không hạ cửa kính xuống","v":"close-up, 85mm portrait lens, ô cửa kính xe đóng kín phản chiếu hàng rào với gương mặt Dean phía sau"},
{"f":301,"b":"reflection","m":"determined","c":[],"d":"Đàn dê làm sườn phía bắc mùa thu đó và đi hợp đồng thêm hai lần nữa; dọc các hàng rào đã dọn, kudzu vẫn mọc lại mỗi tháng Sáu, mỏng hơn và muộn hơn qua từng năm","v":"medium shot, 50mm lens, đàn dê gặm trên sườn bắc với hàng rào đã dọn sạch phía sau"},
{"f":304,"b":"reflection","m":"sad","c":["burl","corinne"],"d":"Mùa đông đó Burl ít tới hơn - ông bảy mươi tư tuổi, cái lạnh đã ngấm vào hông, và ông ngồi trên thùng xe trong khi bà đi các paddock; tháng Ba ông lẽ ra đi cùng bà tới phiên bán dê đực ở Ball Ground","v":"medium shot, 50mm lens, Burl ngồi trên thùng xe hạ xuống nhìn ra dãy paddock mùa đông"},
{"f":307,"b":"tension","m":"sad","c":["burl","corinne"],"d":"Ông đưa bà tờ giấy gấp thay vì đi cùng - ghi chép của ông về bề ngang, về thăn và hình dáng bàn chân, ba đời phán đoán về dê viết bằng bút chì","v":"extreme close-up, 100mm macro lens, tờ giấy gấp tư với nét chì mờ nằm trong bàn tay già gân guốc"},
{"f":309,"b":"dialogue","m":"determined","c":["burl","corinne"],"d":"Cô biết mình đang nhìn cái gì, ông nói; tôi đã nói cho cô thứ tôi thấy, giờ đi và nói lại cho tôi thứ cô thấy","v":"over-shoulder shot, 50mm lens, qua vai Burl nhìn Corinne đang cầm tờ giấy gấp"},
{"f":311,"b":"dialogue","m":"hopeful","c":["burl","corinne"],"d":"Bà trở về với hai con dê đực; ông ngắm chúng thật lâu và không bao giờ nói bà chọn đúng hay sai, mà với Burl thì chính đó là câu trả lời","v":"medium shot, 50mm lens, Burl đứng ngắm hai con dê đực trong bãi quây gỗ"},
{"f":313,"b":"reflection","m":"determined","c":["corinne"],"d":"Mùa xuân đó bà mở sườn phía nam, trồng thêm sáu mươi cây hồ đào, và đặt những cây thay thế vào đúng chỗ hạn hán đã lấy đi lứa đầu","v":"extreme wide shot, 24mm wide-angle lens, sườn nam vừa mở với những hàng cọc trồng cây chạy theo đường đồng mức"},
{"f":315,"b":"reflection","m":"tense","c":["corinne"],"d":"Đó là mùa cuối cùng bà còn; hạt sẽ ra đi bộ trên mảnh đất và quyết định xem có phần nào trong đó từng là canh tác hay không","v":"close-up, 85mm portrait lens, gương mặt Corinne nhìn xuống vườn cây non trong mùa cuối cùng bà còn, full head within frame"},
{"f":318,"b":"tension","m":"vindication","c":["corinne"],"d":"Ba mùa trước, thứ duy nhất trên mảnh đất đó đáng đếm là đám dây leo; mùa xuân này bà đứng ở cổng phía trên vườn cây và đếm các hàng","v":"high angle shot, 50mm lens, nhìn xuống những hàng cây non thẳng lối từ phía cổng trên cao"},
# ===== ACT 6 — Kỳ thẩm định & phán quyết (24:25 - 27:04) =====
{"f":320,"b":"establishing","m":"tense","c":["corinne"],"d":"Chiếc xe của hạt rẽ vào cổng vào một buổi sáng tháng Tư, và Corinne nghe thấy nó trước khi nhìn thấy, bởi tấm lưới chắn gia súc ngoài đường kêu lên như một cái thang bị đánh rơi","v":"wide shot, 35mm lens, chiếc xe bán tải của hạt rẽ vào cổng qua tấm lưới chắn gia súc bằng thép"},
{"f":323,"b":"dialogue","m":"tense","c":["dean","otis_12"],"d":"Dean Whitcomb thay ủng cao su ngay trên thùng xe và nói ông định đi bộ hết cả mảnh đất; Otis, giờ mười một tuổi và đã cao hơn sợi dây rào trên cùng, xách túi máy ảnh mà không cần ai nhờ","v":"medium shot, 50mm lens, Dean xỏ ủng trên thùng xe hạ xuống trong khi Otis đứng cạnh xách túi máy ảnh"},
{"f":325,"b":"reflection","m":"calm","c":["dean","corinne"],"d":"Họ bắt đầu từ bờ đường và đi dần về phía đông; Whitcomb có một biểu mẫu trên tấm kẹp và một bánh xe đo, và cứ một lúc ông lại dừng, ghi một con số rồi chụp một tấm ảnh","v":"over-shoulder shot, 50mm lens, qua vai Dean nhìn bánh xe đo lăn dọc theo bờ đường đất"},
{"f":327,"b":"dialogue","m":"determined","c":["dean","corinne"],"d":"Ông hỏi mật độ thả và bà trả lời theo từng mùa, rồi hỏi về vòng quay: bốn mẫu một lần, chuyển đàn khi tới ngưỡng gặm","v":"medium shot, 50mm lens, hai người đứng giữa một paddock trong khi Dean ghi vào biểu mẫu"},
{"f":329,"b":"dialogue","m":"determined","c":["corinne"],"d":"Khi ông hỏi có thứ gì được ghi chép lại không, bà quay ra xe và mang về một cuốn bìa còng dày bằng bốn mùa","v":"extreme close-up, 100mm macro lens, cuốn bìa còng dày cộp đặt lên nắp thùng xe phủ bụi đường"},
{"f":331,"b":"reflection","m":"vindication","c":[],"d":"Đó chính là công việc cũ vẫn còn đang làm việc cho bà - ngày tháng, số đầu con, lượng mưa, giá cỏ khô, và một hợp đồng cho mỗi nơi đàn dê từng được thuê tới","v":"medium close-up, 85mm lens, các trang sổ ghi tay lật mở dưới nắng trên nắp thùng xe"},
{"f":333,"b":"tension","m":"hopeful","c":["dean","corinne"],"d":"Ông đọc trên thùng xe một lúc lâu rồi xin được xem những cái cây; chín cây nằm trên vai đồi phía đông, tán đã xòe rộng ra vì giờ chúng có ánh sáng","v":"wide shot, 35mm lens, chín cây hồ đào tán rộng đứng trên vai đồi phía đông dưới nắng tháng Tư"},
{"f":335,"b":"reflection","m":"hopeful","c":[],"d":"Những rọ lưới thép vẫn còn nguyên trên thân cây; phía dưới chúng các hàng cây non chạy theo đường đồng mức thành từng dải, ba trăm bốn mươi cây hồ đào, không cây nào còn cách dưới sáu năm nữa mới cho một hạt đáng đếm","v":"extreme wide shot, 24mm wide-angle lens, các dải cây non chạy theo đường đồng mức xuống khắp sườn đồi"},
{"f":337,"b":"reflection","m":"determined","c":["corinne","dean"],"d":"Trên ranh phía bắc, ở hai khe quá dốc để rào, phần kudzu còn lại vẫn bám trụ, và bà chỉ nó ra trước khi ông kịp tự tìm thấy","v":"high angle shot, 50mm lens, nhìn xuống hai khe dốc còn sót lại những mảng kudzu xanh"},
{"f":340,"b":"dialogue","m":"tense","c":["dean"],"d":"Trên đỉnh dốc ông đặt tấm kẹp hồ sơ xuống - hai mươi hai năm, ông nói, thế bộ rễ mất bao lâu","v":"close-up, 85mm portrait lens, gương mặt Dean quay sang hỏi trên đỉnh dốc lộng gió, full head within frame"},
{"f":342,"b":"dialogue","m":"determined","c":["corinne","dean"],"d":"Ba mùa, bà đáp, bốn mùa cho phần còn lại; ông ghi câu đó lại và nói lá thư sẽ được gửi từ văn phòng","v":"medium close-up, 85mm lens, Corinne đáp lời trong khi Dean ghi vào biểu mẫu bên cạnh"},
{"f":344,"b":"emotional_peak","m":"vindication","c":["corinne"],"d":"Thư về vào tháng Năm và chỉ dài ba dòng: toàn bộ một trăm lẻ bốn mẫu được xác định là đang sử dụng nông nghiệp thực chất, và giao ước vẫn còn hiệu lực","v":"extreme close-up, 100mm macro lens, một phong bì công vụ đã bóc nằm mở trên mặt bàn bếp"},
{"f":346,"b":"tension","m":"calm","c":["corinne"],"d":"Đó là điểm kết của một cái đồng hồ bà đã nghe tích tắc suốt bốn năm; bà đọc nó hai lần rồi đi ra chuyển hàng rào","v":"medium shot, 50mm lens, Corinne bước ra sân cầm cuộn dây rào, tờ thư nằm lại trên bàn bếp"},
# ===== ACT 7 — Định giá lại & vụ mùa đầu tiên (27:04 - 29:53) =====
{"f":348,"b":"reflection","m":"vindication","c":[],"d":"Chiếc phong bì kia tới vào cuối mùa hè đó: hạt đã định giá lại một trăm lẻ bốn mẫu - đồng cỏ đã dọn, vườn cây đã lập, nguồn nước hoạt động, mặt tiền đường","v":"wide shot, 35mm lens, toàn cảnh trang trại đã dọn quang với vườn cây và đồng cỏ dưới nắng cuối hè"},
{"f":350,"b":"emotional_peak","m":"shock","c":["corinne"],"d":"Giá trị thị trường hợp lý: bốn trăm sáu mươi hai nghìn tám trăm đô - chưa ai từng trả bà con số đó","v":"close-up, 85mm portrait lens, gương mặt Corinne khi đọc tờ thông báo định giá, full head within frame"},
{"f":352,"b":"reflection","m":"calm","c":[],"d":"Đó không phải một giá bán, và hơn ai hết bà biết một cuộc định giá là gì và không là gì; dưới giao ước, thuế của bà vẫn sẽ được tính theo mức sử dụng nông nghiệp","v":"medium close-up, 85mm lens, tờ thông báo định giá đặt cạnh cuốn sổ cái cũ trên mặt bàn bếp"},
{"f":354,"b":"emotional_peak","m":"vindication","c":[],"d":"Đó là ý kiến của hạt về thứ mà mảnh đất đã trở thành - chính mảnh đất từng đứng trên bậc thềm tòa án ba lần mà không nhận được một lời trả giá nào","v":"extreme wide shot, 24mm wide-angle lens, toàn cảnh thửa đất một trăm lẻ bốn mẫu đã dọn quang nhìn từ trên cao"},
{"f":357,"b":"reflection","m":"hopeful","c":["burl","otis_12"],"d":"Họ rung hạt chín cây vào tuần cuối tháng Mười, với bạt trải và sào sợi thủy tinh, còn Burl Tannehill ngồi ở mép chỗ đó trên một chiếc ghế xếp và bảo Otis rằng cậu đang làm sai","v":"medium shot, 50mm lens, Otis vung sào rung cành trên tấm bạt trải rộng, Burl ngồi ghế xếp bên cạnh"},
{"f":359,"b":"emotional_peak","m":"vindication","c":[],"d":"Những cây hồ đào già đã hai mươi hai năm không bị đòi hỏi thứ gì; cây lớn nhất cho hai trăm ba mươi mốt pound, cây nhỏ nhất sáu mươi tám","v":"extreme close-up, 100mm macro lens, hạt hồ đào chất thành đống dày trên tấm bạt trải"},
{"f":361,"b":"tension","m":"reflection","c":[],"d":"Tổng cộng một nghìn ba trăm bốn mươi mốt pound, mà ở trạm thu mua thì đó không phải một kế sinh nhai - nó là một tờ biên nhận mang tên bà, với chữ hồ đào nằm phía trên con số cân","v":"medium close-up, 85mm lens, những bao hạt hồ đào xếp trên chiếc cân sàn ở trạm thu mua"},
{"f":363,"b":"reflection","m":"reflection","c":["corinne"],"d":"Đêm đó bà đặt tờ thông báo định giá lên bàn bếp, bên cạnh cuốn sổ cái cũ từ Atlanta, cuốn bà đã mang ra khỏi một công việc chuyên định giá đổ vỡ của người khác","v":"high angle shot, 50mm lens, nhìn xuống mặt bàn bếp với tờ giấy và cuốn sổ đặt cạnh nhau dưới một quầng đèn"},
{"f":365,"b":"tension","m":"calm","c":["corinne"],"d":"Hai cách định giá cùng một mảnh đất, đặt cạnh nhau dưới cùng một thứ ánh sáng; bà nhìn chúng một lúc, rồi đi làm bữa tối","v":"close-up, 85mm portrait lens, gương mặt Corinne nhìn xuống hai tờ giấy dưới ánh đèn bếp, full head within frame"},
{"f":367,"b":"reflection","m":"calm","c":[],"d":"Bà không gọi cho ai cả; nhưng các bản định giá là công khai, và hạt Gilmer là một nơi nhỏ - người đứng cân ở cửa hàng thức ăn gia súc đã nhìn thấy con số cân","v":"medium shot, 50mm lens, gian cửa hàng thức ăn gia súc với chiếc cân sàn và vài người đứng nói chuyện"},
{"f":369,"b":"reflection","m":"vindication","c":[],"d":"Và vợ của ai đó đã nói gì đó dưới tầng hầm nhà thờ sau bữa tối thứ Tư; tới lễ Tạ ơn, mọi người đàn ông từng cười trên bậc thềm tòa án đều đã nghe con số ấy","v":"wide shot, 35mm lens, tầng hầm nhà thờ với những dãy bàn dài và người ngồi ăn tối"},
{"f":372,"b":"tension","m":"reflection","c":["merle"],"d":"Merle Yates nghe được ở hợp tác xã, và ông không nói gì cả; tháng Chạp bà ngồi xuống với một cây bút chì","v":"close-up, 85mm portrait lens, gương mặt Merle đứng lặng giữa kho hợp tác xã, full head within frame"},
# ===== ACT 8 — Bán bớt đàn dê & treo chuông (29:53 - 32:54) =====
{"f":374,"b":"tension","m":"tense","c":["corinne"],"d":"Và tính ra sẽ tốn bao nhiêu để nuôi cả đàn qua một mùa đông trên mảnh đất không còn gì để ăn; thứ để gặm đã hết sạch","v":"medium close-up, 85mm lens, Corinne tính toán bằng bút chì bên bàn bếp trong buổi tối mùa đông"},
{"f":376,"b":"reflection","m":"tense","c":[],"d":"Đó vốn là toàn bộ mục đích của đàn dê, và giờ chính nó lại là rắc rối với chúng; bị giữ ngoài các hàng cây và tránh xa những cây non, cả đàn chỉ còn mười một mẫu đồng cỏ đứng","v":"wide shot, 35mm lens, đàn dê dồn trong khoảnh đồng cỏ hẹp bên ngoài hàng rào vườn cây"},
{"f":378,"b":"tension","m":"sad","c":[],"d":"Và một hóa đơn cỏ khô vượt quá thứ việc cho thuê mang về; Burl đã nói với bà bốn mùa xuân trước rằng một con dê không phải cái máy cắt cỏ mà người ta đỗ lại được","v":"medium shot, 50mm lens, những kiện cỏ khô xếp cao trong kho với đàn dê chờ bên ngoài cửa"},
{"f":381,"b":"reflection","m":"determined","c":["corinne"],"d":"Bà không bán tống chúng đi vội - bà chưa từng làm việc gì theo cách đó; bà giữ lại hai mươi sáu con, những con cái tốt nhất và hai con đực","v":"high angle shot, 50mm lens, nhìn xuống bãi quây với đàn dê được chia thành hai nhóm rõ rệt"},
{"f":383,"b":"reflection","m":"calm","c":["corinne","pepper"],"d":"Trên giấy tờ thì đó là một dòng giống, mà thật ra là vì những đứa con gái của Pepper nằm trong số đó; bà giữ lại việc cho thuê, thứ tới lúc ấy mới thật sự sinh lời, còn lại bà bán từng một hai con cho những người hỏi han trước khi hỏi giá","v":"medium close-up, 85mm lens, Pepper đứng giữa mấy con dê cái trẻ trong bãi quây gỗ"},
{"f":386,"b":"tension","m":"calm","c":["merle"],"d":"Merle Yates tới vào tuần thứ hai của tháng Chạp và mua mười chín con; ông đứng ở hàng rào một lúc lâu trước khi nói điều gì","v":"wide shot, 35mm lens, Merle đứng bên hàng rào nhìn vào bãi quây dê buổi sáng tháng Chạp"},
{"f":388,"b":"reflection","m":"reflection","c":["merle","corinne"],"d":"Đúng theo cách ông từng ngồi ở cổng nhà bà mùa xuân đầu tiên với cửa kính hạ xuống; ông không xin lỗi - đàn ông như thế thì không xin lỗi, và bà cũng chẳng biết đặt lời xin lỗi ấy vào đâu","v":"over-shoulder shot, 50mm lens, qua vai Corinne nhìn Merle đứng lặng bên hàng rào"},
{"f":390,"b":"emotional_peak","m":"hopeful","c":["merle","corinne"],"d":"Ông bỏ mũ xuống, ngước nhìn các đường paddock, rồi hỏi câu mà một người đàn ông chỉ hỏi sau khi đã quyết trong lòng: nếu tôi muốn làm sườn sau nhà mình thì một người nên bắt đầu từ đâu","v":"close-up, 85mm portrait lens, Merle bỏ mũ cầm trên tay và ngước nhìn lên sườn đồi, full head within frame"},
{"f":394,"b":"dialogue","m":"determined","c":["corinne","merle"],"d":"Thế là bà nói cho ông nghe: mười chín con không đủ cho tám mẫu dây leo và ông nên tính chuyện mượn thêm trước tháng Bảy; lưới điện, bốn mẫu một lần","v":"medium shot, 50mm lens, Corinne chỉ tay về phía sườn đồi trong lúc nói chuyện với Merle bên hàng rào"},
{"f":396,"b":"dialogue","m":"determined","c":["corinne"],"d":"Chuyển chúng trước khi chúng thấy chán; và mùa thứ hai mới là mùa quật ngã ông, bà nói, bởi nó mọc lại trông y hệt một năm mà ông đã phí hoài","v":"medium close-up, 85mm lens, Corinne nói chuyện với ánh nắng chiều muộn trên gương mặt"},
{"f":398,"b":"dialogue","m":"hopeful","c":["merle"],"d":"Ông không ghi lại chữ nào; ông chỉ nhờ bà nói lại đoạn về mùa thứ hai một lần nữa","v":"close-up, 85mm portrait lens, gương mặt Merle chăm chú lắng nghe với chiếc mũ cầm trong tay, full head within frame"},
{"f":400,"b":"tension","m":"nostalgic","c":["corinne"],"d":"Đàn dê rời khỏi rơ moóc của bà đúng theo cách chúng từng bước xuống khỏi rơ moóc của Burl; bà nghĩ về điều đó trên đường lái xe về và không nhắc lại với ai","v":"medium shot, 50mm lens, đàn dê bước xuống cầu rơ moóc kim loại ở một trang trại khác"},
{"f":402,"b":"reflection","m":"nostalgic","c":["pepper"],"d":"Pepper khi đó đã mười một tuổi, xám tới tận vai, chậm chạp trên dốc mà vẫn là con đầu tiên qua bất cứ cánh cổng nào mở ra; nó không bị bán đi","v":"medium close-up, 85mm lens, Pepper mõm xám đứng ở khung cổng mở với đàn dê phía sau"},
{"f":404,"b":"emotional_peak","m":"nostalgic","c":["corinne","pepper"],"d":"Ngày Chủ nhật cuối cùng của năm, Corinne bắt nó lại trong bãi, tháo sợi dây da đã mòn và nhấc chiếc chuông đồng khỏi cổ nó lần đầu tiên kể từ khi Burl trao nó cho bà hồi tháng Ba năm ấy","v":"extreme close-up, 100mm macro lens, hai bàn tay tháo khóa dây da và nhấc chiếc chuông đồng khỏi cổ con dê"},
{"f":407,"b":"reflection","m":"hopeful","c":["corinne"],"d":"Bà mang nó lên vườn cây; cây to nhất trong chín cây, cái cây Otis đặt tên Big Tuesday hồi cậu chín tuổi, có một cành thấp vươn ra trên bãi cỏ đã xén ở khoảng ngang vai","v":"wide shot, 35mm lens, Corinne đi lên vườn cây với chiếc chuông trong tay, cây hồ đào lớn phía trước"},
{"f":409,"b":"emotional_peak","m":"hopeful","c":[],"d":"Bà treo chiếc chuông ở đó rồi buông tay; chiều hôm đó gió làm nó đung đưa, và sau đó nó tự đung đưa lấy, theo cách bất cứ thứ gì treo ngoài trời cũng sẽ đung đưa","v":"low angle shot, 50mm lens, chiếc chuông đồng treo trên cành thấp nhìn ngược lên tán cây và bầu trời"},
{"f":412,"b":"dialogue","m":"hopeful","c":["otis_12"],"d":"Otis đã mười hai tuổi; cậu đứng với hai tay đút túi áo khoác và lắng nghe một lúc lâu - giờ mẹ có thể tìm ra giữa vườn ngay trong bóng tối, cậu nói","v":"close-up, 85mm portrait lens, gương mặt Otis mười hai tuổi lắng nghe dưới tán cây, full head within frame"},
{"f":415,"b":"tension","m":"reflection","c":[],"d":"Bốn mùa xuân trước, hạt đã rao một trăm lẻ bốn mẫu ba lần mà không nhận được lời trả giá nào, bởi mọi người nhìn vào đều thấy một sườn đồi đã thôi làm đất và biến thành thời tiết","v":"extreme wide shot, 24mm wide-angle lens, sườn đồi phủ kín kudzu một màu nhìn từ mặt đường - replay scene 4"},
{"f":417,"b":"emotional_peak","m":"vindication","c":[],"d":"Nó chưa bao giờ là đất chết, nó là đất bị phủ - đó là một từ khác hẳn, và phải mất một người đàn bà với cuốn sổ cái, tám mươi ba con dê và bốn mùa sinh trưởng mới nói được sự khác biệt ấy ra thành lời","v":"wide shot, 35mm lens, đúng sườn đồi ấy giờ đã quang với những hàng cây non chạy xuống chân dốc"},
{"f":420,"b":"reflection","m":"reflection","c":["corinne"],"d":"Chín mươi mốt nghìn bốn trăm đô không phải là phần đắt đỏ; phần đắt đỏ là đứng ở một hàng rào suốt bốn mùa","v":"medium shot, 50mm lens, Corinne đứng một mình bên hàng rào nhìn ra sườn đồi lúc chiều xuống"},
{"f":422,"b":"resolution","m":"determined","c":["corinne"],"d":"Trong khi những người đàn ông bà phải gặp ở cửa hàng thức ăn mỗi tuần biến bà thành một câu chuyện cười, rồi sáng hôm sau vẫn đi ra chuyển lưới như thường","v":"medium close-up, 85mm lens, Corinne cúi xuống chuyển cọc lưới điện trong sương sớm"},
{"f":425,"b":"reflection","m":"calm","c":["corinne"],"d":"Giờ người ta lái xe lên tận cổng và hỏi bà lấy bao nhiêu cho mảnh đất; bà nói nó không bán, mời họ cà phê, và phần lớn ở lại đủ lâu để đi hết các hàng cây","v":"wide shot, 35mm lens, một chiếc xe lạ đỗ ở cổng và hai người đi bộ giữa các hàng cây non"},
{"f":428,"b":"reflection","m":"hopeful","c":[],"d":"Những cây non chưa đáng giá gì cả - ba trăm bốn mươi cây, trồng thành dải xuống một sườn đồi từng chỉ có một màu, và không cây nào cho một vụ thật trước khi Otis đủ tuổi đi bầu; bà đã biết điều đó ngay khi trồng chúng","v":"high angle shot, 50mm lens, nhìn xuống các dải cây non xếp thành hàng trên sườn đồi"},
{"f":430,"b":"reflection","m":"nostalgic","c":[],"d":"Chiếc chuông vẫn còn trên cành; vào một buổi sáng lặng gió nó không vang tới tận nhà, còn vào một ngày gió thì nó vang ra tới tận đường","v":"extreme close-up, 100mm macro lens, chiếc chuông đồng đung đưa trên cành cây trong nắng sớm"},
{"f":432,"b":"resolution","m":"hopeful","c":[],"d":"Hãy gửi câu chuyện này cho một người đang cố giữ lấy thứ mà tất cả mọi người bảo họ buông tay; và dưới phần bình luận, kể cho chúng tôi nghe về nơi bạn chỉ nhìn thấy cỏ dại, và người đã nhìn ra thứ đáng để giữ lại","v":"extreme wide shot, 24mm wide-angle lens, toàn cảnh trang trại lúc hoàng hôn với vườn cây và sườn đồi đã quang"},
]


def build():
    ent = parse_srt()
    srt_end = ent[max(ent)][1]
    rows, cats, beats, problems = [], [], {}, []
    for i, sc in enumerate(SCENES):
        start = ent[sc["f"]][0]
        end = ent[SCENES[i + 1]["f"]][0] if i + 1 < len(SCENES) else srt_end
        dur = end - start
        lo, hi = BOUNDS[sc["b"]]
        if dur > hi:
            problems.append(f"Scene {i+1} (f={sc['f']}): {sc['b']} {dur}s VƯỢT max {hi}s")
        elif dur < lo:
            problems.append(f"Scene {i+1} (f={sc['f']}): {sc['b']} {dur}s dưới min {lo}s")
        cats.append(shot_cat(sc["v"]))
        beats[sc["b"]] = beats.get(sc["b"], 0) + 1
        chars = ", ".join(sc["c"]) if sc["c"] else "—"
        rows.append(f"| {i+1} | {fmt(start)} | {fmt(end)} | {dur} | {sc['b']} | {sc['m']} | {chars} | {sc['d']} | {sc['v']} |")
    return rows, cats, beats, problems, srt_end


def main():
    rows, cats, beats, problems, srt_end = build()
    n = len(rows)
    print(f"Scenes: {n} | SRT end: {fmt(srt_end)} ({srt_end}s) | tối thiểu {-(-srt_end//25)} | kỳ vọng ~{srt_end//12}")
    if problems:
        print(f"\nDURATION/BEAT ({len(problems)}):")
        for p in problems:
            print("  ✗ " + p)
    st, sb = 0, None
    for i, sc in enumerate(SCENES):
        if sc["b"] == sb:
            st += 1
            if st >= 4:
                print(f"  ✗ Scene {i+1}: {st} scene liên tiếp cùng beat `{sb}`")
        else:
            st, sb = 1, sc["b"]
    FORB = {("tension", "resolution"), ("establishing", "emotional_peak"), ("resolution", "tension")}
    for i in range(1, len(SCENES)):
        if (SCENES[i - 1]["b"], SCENES[i]["b"]) in FORB:
            print(f"  ⚠ Scene {i+1}: chuyển beat cấm {SCENES[i-1]['b']}→{SCENES[i]['b']} (rule 3.3)")
    rest = 0
    for i, sc in enumerate(SCENES):
        rest = 0 if sc["b"] in ("establishing", "reflection") else rest + 1
        if rest == 8:
            print(f"  ⚠ Scene {i+1}: 8 scene liên tiếp không có beat nghỉ mắt (rule 3.6)")
    for i in range(0, n - 9, 10):
        w = cats[i:i + 10]
        c = {k: w.count(k) for k in ("wide", "medium", "closeup", "angle")}
        miss = [f"{k} {c[k]}/{v}" for k, v in (("wide", 2), ("medium", 3), ("closeup", 2), ("angle", 1)) if c[k] < v]
        if miss:
            print(f"  ⚠ Scenes {i+1}-{i+10}: thiếu {', '.join(miss)}")
    if "?" in cats:
        print(f"  ✗ Scene thiếu lens hợp lệ: {[i+1 for i, c in enumerate(cats) if c == '?']}")

    if "--check" in sys.argv:
        return
    total = sum(int(r.split("|")[4]) for r in rows)
    head = [f"# Scene Breakdown: {TITLE}",
            f"Total scenes: {n} | Total duration: {fmt(total)}", "",
            "| STT | Start | End | Dur(s) | Beat Type | Mood | Characters | Description | Visual Notes |",
            "|---|---|---|---|---|---|---|---|---|"]
    dist = ["", "## Beat Distribution"] + [f"- {k}: {v} ({v*100//n}%)" for k, v in sorted(beats.items())]
    OUT.write_text("\n".join(head + rows + dist) + "\n", encoding="utf-8")
    print(f"\n✓ Đã ghi {OUT.name} — {n} scene, tổng {total}s")


if __name__ == "__main__":
    main()
