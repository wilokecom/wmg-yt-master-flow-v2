#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder: sinh output/sfx.json từ danh sách keyword do người viết cho TỪNG scene.

Script chỉ ghép + kiểm tra (phủ đủ stt, không âm đánh chữ, không đơn điệu) —
KHÔNG sinh keyword. Nguồn nội dung: output/scene-breakdown.md (Bước 2).

Quy tắc (.claude/rules/sound.md):
  8.2 chỉ âm diegetic có thật trong cảnh — CẤM nhạc nền/score
  8.3 cụm danh từ + hành động cụ thể, tìm được trên thư viện sfx
  8.7 CẤM âm đánh chữ/gõ phím (thuộc hiệu ứng typewriter, không phải sfx cảnh)
  8.8 đa dạng + hợp mood

Chạy:  python3 scripts/build_sfx.py          # ghi output/sfx.json
       python3 scripts/build_sfx.py --check  # chỉ kiểm, không ghi
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "sfx.json"
BREAKDOWN = ROOT / "output" / "scene-breakdown.md"

# stt: [keyword, ...]  — 1-3 cụm/scene, scene im lặng = []
SFX = {
# --- HOOK: bậc thềm tòa án lạnh, đồi kudzu, lời Kinh Thánh (1-10) ---
1: ["cold march wind down empty street", "small crowd shuffling on stone steps"],
2: ["auctioneer calling for bids outdoors", "paper bid card lifted"],
3: ["paper document sliding on wooden table"],
4: ["wind moving through dense kudzu leaves"],
5: ["distant highway traffic passing"],
6: ["men laughing in a small crowd", "boots scuffing stone steps"],
7: ["dry vine leaves brushing tree bark"],
8: ["thin bible page turning"],
9: ["quiet kitchen room tone", "wooden chair creaking"],
10: ["steady wind across open hillside"],
# --- ACT 1: phiên đấu giá, quá khứ Atlanta, ký giấy (11-30) ---
11: ["cold wind gusting between buildings", "courthouse door closing"],
12: ["coats rustling in cold wind", "low murmur of waiting men"],
13: ["suburban driveway ambience", "clipboard pen writing"],
14: ["ballpoint pen writing steadily on paper"],
15: ["distant ambulance siren approaching"],
16: ["bank check paper handled", "small metal ring set on wood"],
17: ["empty hallway ambience with echo", "child swinging legs against wooden bench"],
18: ["gravel county road ambience", "grasshoppers in roadside weeds"],
19: ["vine tendril scraping barbed wire"],
20: ["auction gavel strike on wood", "crowd falling silent"],
21: ["pickup truck driving on rural highway", "turn signal ticking"],
22: ["truck idling on roadside", "wind buffeting windshield"],
23: ["legal pad page flipped", "pencil underlining hard on paper"],
24: ["goat tearing leaves from vine"],
25: ["office papers stacked on counter", "county office room tone"],
26: ["rubber boots stepping through thick vines"],
27: ["contract page turning slowly", "wall clock ticking in quiet office"],
28: ["empty stock trailer rattling in wind"],
29: ["rusted padlock chain unlocked", "farm gate hinge groaning open"],
30: ["truck engine switched off", "cab settling in silence"],
# --- ACT 2: chui dưới tán, Burl, đàn dê đầu tiên (31-45) ---
31: ["heavy vine curtain pushed aside", "dry leaves crunching underfoot"],
32: ["crawling through undergrowth", "muffled ambience under dense canopy"],
33: ["water dripping from wet leaves"],
34: ["hand slapping hollow wooden post", "child voice counting outdoors"],
35: ["wind sweeping over open hilltop"],
36: ["goat herd bleating in distance", "wire fence twanging"],
37: ["older man talking over pasture ambience", "goats chewing nearby"],
38: ["goat herd milling in a pen", "brass bell shaken in hand"],
39: ["livestock trailer ramp lowered", "hooves clattering down metal ramp"],
40: ["electric netting posts pushed into soil", "fence energizer clicking"],
41: ["farm gate swinging wide open", "large goat herd rushing downhill"],
42: ["hundreds of leaves being stripped at once", "goat bell moving through brush"],
43: ["pickup truck slowing on gravel shoulder"],
44: ["diesel truck idling at a gate"],
45: ["truck window rolled down", "man calling out over pasture"],
# --- ACT 2B: rễ chưa chết, cái giếng, chín thân cây (46-72) ---
46: ["boots walking on bare dry soil", "electric fence line ticking"],
47: ["hand brushing over young shoots"],
48: ["spade cutting into packed soil", "root ball pulled from earth"],
49: ["rotary desk phone handset lifted", "quiet farmhouse room tone"],
50: ["loose stones falling into a deep well", "goat bleating in distress"],
51: ["rope creaking under strain", "hand winch ratcheting in the dark"],
52: ["rocks and clay shoveled into a hole"],
53: ["light breeze across cleared hillside"],
54: ["goat herd grazing across a slope", "netting posts being pulled up"],
55: ["frost crunching underfoot", "breath in cold morning air"],
56: ["dry vines snapping off fence wire"],
57: ["leaves brushing against bark"],
58: ["palm patting rough tree bark"],
59: ["measured footsteps pacing on dirt", "older man speaking quietly outdoors"],
60: ["wind moving through high tree crowns"],
61: ["pecan branches creaking in wind"],
62: ["dry husks crushed underfoot", "gusty autumn wind through orchard"],
63: ["fingertips scraping stripped wood"],
64: ["quiet hilltop ambience"],
65: ["bare branches rattling in cold wind"],
66: ["goats bleating near a fence", "man speaking flatly outdoors"],
67: ["welded wire mesh unrolled", "steel stake driven with a mallet"],
68: ["hay bales dropped on barn floor"],
69: ["light rain on dry ground"],
70: ["rain drumming on jacket hood", "fence staples hammered into post"],
71: ["child voice calling under trees", "boots running through wet grass"],
72: ["single bird call in bare orchard"],
# --- ACT 3: mẫu đất & sự thật về kudzu (73-84) ---
73: ["wide open countryside ambience"],
74: ["pickup truck arriving on gravel drive", "metal probe rattling in truck bed"],
75: ["two people talking beside a truck", "cold field ambience"],
76: ["soil probe pushed into wet ground", "core of earth tapped out"],
77: ["sample tubes clinking together", "winter wind across bare pasture"],
78: ["dry soil crumbled between fingers"],
79: ["goat herd grazing in open pasture", "distant crows calling"],
80: ["report page turned over on a hood", "finger tapping on paper"],
81: ["roots pulled apart by hand"],
82: ["steady wind over wide farmland"],
83: ["quiet indoor room tone"],
84: ["ledger page turning", "pen scratching entries in a notebook"],
# --- ACT 4: mùa đông cạn tiền & cuộc rút lui (85-109) ---
85: ["barn interior at night ambience", "sick goat breathing heavily"],
86: ["fence charger clicking steadily", "wire tensioned along a fence"],
87: ["child counting out loud at dusk", "goats settling for the night"],
88: ["heavy tarp dragged aside", "metal toolbox latch opened"],
89: ["socket wrench set down in tray", "toolbox lid closed"],
90: ["feed sack dropped on kitchen floor", "kitchen door swinging shut"],
91: ["soft bible cover opened on table", "coffee poured into mugs"],
92: ["single page settling in still air"],
93: ["empty feed sack rustling", "farm boots crossing gravel yard"],
94: ["bleak february wind over stubble"],
95: ["predawn ridge ambience"],
96: ["large herd browsing at sunrise", "distant goat bell"],
97: ["leaves torn steadily by grazing goats"],
98: ["hooves shifting on loose soil"],
99: ["vine stems snapping under teeth"],
100: ["boot pressing into soft red dirt"],
101: ["two people talking on a hillside"],
102: ["power line humming overhead", "brush crackling on a steep slope"],
103: ["trailer gate unlatched", "water sloshing into a stock tank"],
104: ["goats grazing among headstones", "cemetery ambience with birds"],
105: ["schoolchildren chattering outdoors", "chain link fence rattling"],
106: ["truck pulling onto gravel shoulder", "truck door opening"],
107: ["man speaking quietly outdoors", "cap brim handled in hands"],
108: ["goats bleating behind a fence", "roadside breeze"],
109: ["pencil writing on a paper receipt"],
# --- ACT 5: sương mù, cái tên đúng, vườn cây năm ba (110-136) ---
110: ["heavy fog ambience with dripping", "gate latch swinging loose"],
111: ["voice calling out swallowed by fog", "muffled stillness"],
112: ["single goat bell in the distance", "footsteps through wet grass"],
113: ["truck cabin road noise", "turn signal ticking"],
114: ["tires humming on country asphalt"],
115: ["ledger page turning under a lamp", "quiet night kitchen tone"],
116: ["evening breeze over cleared hillside"],
117: ["gravel road footsteps at sunset"],
118: ["auger boring planting holes", "soil shoveled beside a stake"],
119: ["marker flags snapping in wind", "young tree tamped into soil"],
120: ["grafting knife slicing green wood", "barn workbench ambience"],
121: ["grafting tape wound around a stem"],
122: ["breeze through young orchard rows"],
123: ["small sapling leaves rustling"],
124: ["water tank sloshing in a truck bed", "dry cracked ground underfoot"],
125: ["brittle dead sapling snapped off"],
126: ["car tires slowing on gravel road"],
127: ["pen clicking against a clipboard", "car idling on roadside"],
128: ["power window staying shut", "sedan pulling away on gravel"],
129: ["goat herd working a north slope", "wire gate opened"],
130: ["tailgate dropped open", "winter pasture ambience"],
131: ["folded paper unfolded in hands"],
132: ["older man speaking by a truck"],
133: ["two bucks shifting in a pen", "hooves on wooden boards"],
134: ["planting stakes driven into soil", "spring birdsong over open ground"],
135: ["gate hinge creaking at the orchard"],
136: ["footsteps counting along orchard rows"],
# --- ACT 6: kỳ thẩm định & phán quyết (137-149) ---
137: ["cattle guard rattling under tires", "truck turning onto a farm drive"],
138: ["rubber boots pulled on", "camera bag zipper closed"],
139: ["measuring wheel clicking along ground", "shutter of a camera"],
140: ["two people talking in open pasture", "pen on clipboard form"],
141: ["truck door shut", "heavy binder set on a tailgate"],
142: ["binder pages flipped in wind"],
143: ["footsteps climbing a grassy slope"],
144: ["wire baskets ticking against bark", "breeze through young orchard"],
145: ["boots pushing through remaining vines"],
146: ["clipboard set down on grass", "wind over an open ridge"],
147: ["short answer spoken outdoors", "pen writing on a form"],
148: ["envelope torn open", "letter unfolded on a table"],
149: ["kitchen chair pushed back", "screen door swinging shut"],
# --- ACT 7: định giá lại & vụ mùa đầu tiên (150-161) ---
150: ["mailbox lid opened on a post", "late summer cicadas"],
151: ["paper notice held in still room"],
152: ["papers laid side by side on a table"],
153: ["wide farmland ambience at midday"],
154: ["fiberglass pole striking branches", "pecans raining onto a tarp"],
155: ["nuts poured into a burlap sack"],
156: ["sacks dropped onto a platform scale", "buying station room tone"],
157: ["paper sliding across a kitchen table"],
158: ["kitchen lamp buzzing faintly", "pot set on a stove"],
159: ["feed store door bell", "scale ticking under a load"],
160: ["church basement chatter after supper", "chairs scraping on tile floor"],
161: ["co-op warehouse ambience", "pallet jack rolling on concrete"],
# --- ACT 8: bán bớt đàn dê, treo chuông, kết (162-186) ---
162: ["pencil figures on paper", "winter kitchen room tone"],
163: ["goats crowded in a small pasture", "hay pulled from a bale"],
164: ["hay bales stacked in a barn", "goats bleating for feed"],
165: ["gate swung between pens", "goats sorted into two groups"],
166: ["doe bleating softly in a pen"],
167: ["truck parked at a farm gate", "december wind across a yard"],
168: ["boots stopping at a fence line"],
169: ["cap taken off in the wind", "man speaking after a pause"],
170: ["woman explaining outdoors", "netting rolled out on grass"],
171: ["wind through fence wire", "quiet exchange at a fence"],
172: ["pause in conversation outdoors"],
173: ["goats loaded down a trailer ramp", "trailer gate latched"],
174: ["old goat walking slowly on gravel", "brass bell swinging softly"],
175: ["leather strap unbuckled", "bell lifted free of a collar"],
176: ["footsteps walking uphill through grass"],
177: ["brass bell hung on a branch", "light wind moving a bell"],
178: ["boy standing still in an orchard", "bell ringing faintly"],
179: ["wind over a solid wall of vines"],
180: ["breeze through cleared orchard rows"],
181: ["single fence wire humming in wind"],
182: ["netting posts pulled in morning mist", "boots in wet grass at dawn"],
183: ["car arriving up a farm drive", "coffee cups set on a porch rail"],
184: ["young orchard rustling in wind"],
185: ["brass bell ringing across a still morning"],
186: ["evening breeze over a farm", "distant bell fading"],
}

# KAIZEN 2026-07-22 (Rule 8.9) — SFX là ĐIỂM NHẤN cảm xúc, không phải lớp phủ.
# Dict trên giữ nguyên làm tư liệu tra cứu; chỉ các scene trong ACCENT mới giữ keyword:
#   (1) sự kiện âm cụ thể narration nhắc tới (búa gõ, cổng mở, đàn dê tràn, phong bì xé,
#       cattle guard "nghe thấy trước khi nhìn thấy", tiếng cả đàn ăn "như mưa trên mái"...)
#   (2) khoảnh khắc cảm xúc cần nhấn (giếng đêm, hộp đồ nghề của Nolan, dựng rào trong mưa)
#   (3) motif chuông đồng trọn chuỗi: 38→42→96→112→174→175→177→178→185→186
ACCENT = {
    1, 2, 4, 6, 11, 15, 20, 24, 29, 30,            # hook + act 1: đấu giá, còi cứu thương, búa, cổng gỉ
    31, 34, 38, 39, 41, 42,                         # vào dưới tán, chuông trao tay, đàn xuống đồi
    48, 49, 50, 51, 52, 62, 67, 70, 71,             # rễ, điện thoại, cái giếng, rào chắn trong mưa
    74, 76, 80, 84,                                 # Nadine khoan đất, báo cáo, sổ cái
    85, 87, 88, 89, 91, 94, 96, 100, 102, 105, 106, 109,  # mùa đông, hộp đồ nghề, cả đàn ăn
    110, 111, 112, 115, 118, 120, 124, 125, 128, 131,     # sương mù + chuông, trồng cây, hạn
    137, 139, 141, 148, 149,                        # cattle guard, thẩm định, lá thư
    150, 154, 156, 160,                             # định giá lại, rung hạt, cân, tin lan
    167, 173, 174, 175, 177, 178, 185, 186,         # bán đàn, tháo chuông, treo chuông, kết
}
SFX = {stt: (kw if stt in ACCENT else []) for stt, kw in SFX.items()}


def load_scene_stts():
    md = BREAKDOWN.read_text(encoding="utf-8")
    return [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", md, re.M)]


TW = re.compile(r"typewriter|typing|keyboard|keystroke|key\s?clack", re.I)
MUSIC = re.compile(r"\b(music|score|piano|strings|soundtrack|ambient pad)\b", re.I)


def main():
    stts = load_scene_stts()
    missing = [s for s in stts if s not in SFX]
    extra = [s for s in SFX if s not in stts]
    print(f"Scenes: {len(stts)} | có keyword: {len(SFX)} | thiếu: {len(missing)} | thừa: {len(extra)}")
    if missing:
        print(f"  ⚠ chưa viết sfx cho: {missing[:20]}{'...' if len(missing) > 20 else ''}")
    if extra:
        print(f"  ✗ stt lạ: {extra}")

    flat = [k.lower() for v in SFX.values() for k in v]
    for k in flat:
        if TW.search(k):
            print(f"  ✗ Rule 8.7 — âm đánh chữ trong sfx: `{k}`")
        if MUSIC.search(k):
            print(f"  ✗ Rule 8.2 — nhạc nền trong sfx: `{k}`")
    nonempty = [s for s, v in SFX.items() if v]
    if nonempty:
        top, cnt = Counter(flat).most_common(1)[0]
        share = cnt / len(nonempty)
        flag = "✗" if share > 0.5 else ("⚠" if share > 0.25 else "✓")
        print(f"  {flag} đa dạng: keyword lặp nhiều nhất `{top}` {cnt}/{len(nonempty)} scene ({share:.0%})")
        print(f"  ✓ tổng keyword: {len(flat)} | khác nhau: {len(set(flat))}")
    # lặp liên tiếp
    prev = set()
    runs = {}
    for s in sorted(SFX):
        cur = set(x.lower() for x in SFX[s])
        for k in cur:
            runs[k] = runs.get(k, 0) + 1 if k in prev else 1
            if runs[k] >= 4:
                print(f"  ⚠ `{k}` lặp {runs[k]} scene liên tiếp (tới stt {s})")
        prev = cur

    if "--check" in sys.argv or missing:
        if missing:
            print("\n(chưa ghi file — còn scene thiếu keyword)")
        return
    data = {"sfx": [{"stt": s, "keywords": SFX[s]} for s in stts]}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n✓ Đã ghi {OUT.name} — {len(stts)} scene")


if __name__ == "__main__":
    main()
