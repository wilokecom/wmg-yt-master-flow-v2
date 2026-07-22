#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder Bước 4: sinh output/prompts.md (+ output/video-prompts.md cho hook).

Chỉ PART 1 (nhân vật + hành động) và PART 2 (bối cảnh phụ) được viết tay trong PARTS.
PART 3 (shot + lens), PART 4 (mood keywords), PART 5 (style anchor) do script ghép
NGUYÊN VĂN từ scene-breakdown + config — chống lỗi rơi dấu phẩy mood (KAIZEN 2026-07-17)
và lệch cụm định danh setting làm mất asset tag ở Bước 6 (KAIZEN 2026-07-06/07).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_breakdown import SCENES, parse_srt, fmt  # noqa: E402

CFG = json.loads((ROOT / "input" / "config.json").read_text(encoding="utf-8"))
STYLE = CFG["style"].strip()
FLASHBACK = CFG["flashback_style"].strip()
MOOD = CFG["mood_map"]
VSTYLE = CFG["video_hook"]["video_style"].strip()
NANO = {c["id"]: c["nano_name"] for c in CFG["characters"]}
# Cụm ĐỊNH DANH bối cảnh = cụm đầu tiên của settings[].keywords (Rule 4.1 Phần 2)
SETTING = {s["id"]: s["keywords"].split(",")[0].strip() for s in CFG["settings"]}
FLASHBACK_IDS = set(CFG.get("flashback_variants", []))

# Visual Notes (Bước 2) -> Phần 3 prompt. Thứ tự khớp dài trước ngắn.
SHOTS = [
    ("extreme wide shot 24mm wide-angle lens", "extreme wide shot, 24mm wide-angle lens"),
    ("extreme close-up 100mm macro", "extreme close-up, 100mm macro lens"),
    ("medium close-up 85mm lens", "medium close-up, 85mm lens"),
    ("close-up 85mm portrait lens", "close-up, 85mm portrait lens"),
    ("over-shoulder shot 50mm lens", "over-shoulder shot, 50mm lens"),
    ("low angle shot 50mm lens", "low angle shot, 50mm lens"),
    ("high angle shot 50mm lens", "high angle shot, 50mm lens"),
    ("medium shot 50mm lens", "medium shot, 50mm lens"),
    ("wide shot 35mm lens", "wide shot, 35mm lens"),
]

# f -> (Phần 1: chủ thể + hành động, setting id hoặc None, chi tiết bối cảnh thêm hoặc None)
PARTS = {
1:("a dented tin coffee can with the lid pressed firmly shut",None,"standing on a scarred wooden table under a low hanging lamp"),
4:("Byron bent over a stack of county court forms filling in a line with a pen",None,"at a plain wooden desk under a small desk lamp"),
6:("Truman seated upright, alert brown eyes level, deeply lined face turned toward the lamp",None,"at a warm lit kitchen table"),
9:("Rook standing squared up facing the bars, ears forward and tail low","dean_gate",None),
12:("Rook lying across a kitchen doorway half in and half out, head resting on both paws","dean_kitchen",None),
16:("Dean setting a coffee mug down and reaching for a canvas coat, Rook squared up beyond the dark window","dean_kitchen",None),
18:("Truman and Verna walking arm in arm up the road through cold rain","section_road",None),
20:("Truman holding a battered tin coffee can pressed under a rain soaked coat",None,"one weathered hand closed over the lid"),
22:("a single distant yard light glowing at the far end of a long gravel drive","section_road",None),
24:("a tall pole yard light throwing a cone of light down into the falling rain","dean_gate",None),
26:("Dean standing small at the base of a galvanized windmill tower","windmill_pasture",None),
28:("cattle crowding around a low metal stock tank drained to the bottom","windmill_pasture",None),
30:("Dean hanging from the ladder of a windmill tower, one hand tight on a wrench","windmill_pasture",None),
32:("Dean resting a scarred forearm on a tower brace, gray blue eyes fixed on the horizon","windmill_pasture",None),
36:("Dean standing alone at the edge of a bare gravel yard","dean_porch",None),
38:("Dean facing a farm supply counter while the clerk turns away","coop_counter",None),
40:("a single wooden chair pulled up to a scarred kitchen table","dean_kitchen",None),
42:("Terrell walking through open pasture among scattered cattle, Rook close at his heel","windmill_pasture",None),
45:("Terrell standing thin beside a lowered pickup tailgate facing Dean, Rook between them","dean_porch",None),
48:("Dean looking straight at Terrell, jaw set","dean_porch",None),
50:("Rook lying across the threshold of a kitchen doorway","dean_kitchen",None),
52:("Dean standing small beside a brimming metal stock tank","windmill_pasture",None),
55:("a folded court packet tucked into a coat pocket, an embossed seal showing at the fold",None,"damp wool fabric closed around it"),
58:("Truman and Verna halted a short way back from the closed bars","dean_gate",None),
60:("Truman planting a dented aluminum cane into wet gravel, one hand closed around the grip",None,"loose wet stones around the tip"),
62:("Verna speaking at the bars in a damp mustard yellow cardigan buttoned out of line, Dean facing her","dean_gate",None),
64:("Truman leaning on a cane putting a question to Dean through the bars","dean_gate",None),
66:("Dean standing in the rain with the jaw clenched, water running down the face","dean_gate",None),
70:("Truman turning Verna back toward the road while Dean stands in the open gateway","dean_gate",None),
73:("Dean speaking through the open bars while Rook walks past into the yard","dean_gate",None),
75:("Rook sitting pressed against the leg of Verna, muzzle touching a hanging hand","dean_gate",None),
78:("Truman and Verna standing close together under the falling rain","dean_gate",None),
80:("Dean cooking at a stove while Truman and Verna sit at the table","dean_kitchen",None),
82:("Verna cupping both hands around a ceramic mug, shoulders drawn in","dean_kitchen",None),
83:("Verna resting one hand flat, the bare fourth finger carrying a pale sunken band of skin",None,"on a scarred wooden tabletop"),
85:("Truman setting a hinged weekly pill case beside a ring of keys, four wells still full","dean_kitchen",None),
87:("Dean reaching past for a salt shaker while Truman lays an arm across the can lid","dean_kitchen",None),
91:("Verna sitting with both hands in her lap beside one empty chair, Dean standing at the stove behind her","dean_kitchen",None),
93:("fine dust lifting from a wooden chair seat that Dean sets down for Truman",None,"in the cone of a hanging lamp"),
96:("Verna, Dean and Truman gathered around a scarred wooden table, an upturned feed crate serving as a seat","dean_kitchen",None),
99:("two headlight beams crawling up a long straight roadway","section_road",None),
101:("Byron standing at the closed bars with both hands held open and visible, Rook waiting inside","dean_gate",None),
104:("Byron speaking through the bars in a quilted forest green vest while Dean listens","dean_gate",None),
106:("Byron feeding a folded paper packet through the wet iron bars toward Dean","dean_gate",None),
108:("an embossed county seal and an inked signature on a sheet darkening with rain",None,"held flat in the lamplight"),
109:("Dean reading a folded court packet under the falling rain","dean_gate",None),
112:("Byron speaking through the bars with a courteous half smile while Dean listens from the yard","dean_gate",None),
113:("a dented propane cage standing against a side wall, scraped paint across the frame","coop_counter",None),
115:("Byron talking on evenly, rain beading across the shoulders of a quilted vest","dean_gate",None),
116:("Dean standing motionless inside the gateway while Byron talks from beyond the bars","dean_gate",None),
118:("Byron behind the wet bars wearing a fixed courteous half smile, Dean facing him in the rain","dean_gate",None),
120:("Byron leaning close to the wet bars, pale blue eyes level","dean_gate",None),
122:("Dean standing silent with rain running down the face","dean_gate",None),
125:("Dean standing still in the open yard while Byron talks beyond the bars","dean_gate",None),
129:("Dean standing braced in the rain seen from below","dean_gate",None),
131:("Byron laughing behind the wet iron bars, Rook watching from below","dean_gate",None),
135:("Verna sitting with tears on her face while Truman rests both hands on a tin can lid","dean_kitchen",None),
137:("Dean looking down at a court packet held in both hands, rain across the paper","dean_gate",None),
139:("Dean standing at a wall telephone under fluorescent light","coop_counter",None),
142:("Dean holding a wall telephone receiver, the coiled cord stretched across the frame","dean_kitchen",None),
144:("Dean writing on the back of an envelope beside a wall telephone","dean_kitchen",None),
146:("Dean pressing a telephone receiver to the ear, eyes lowered to the tabletop","dean_kitchen",None),
147:("Dean leaning a shoulder against the wall beside a telephone","dean_kitchen",None),
149:("a thick court file lying open across a kitchen table","dean_kitchen",None),
151:("Dean standing at the telephone with the eyes closed for a beat","dean_kitchen",None),
152:("Dean leaning toward a wall telephone, one hand gripping the coiled cord","dean_kitchen",None),
154:("a stack of receipts folded in quarters and bound with an aged rubber band",None,"resting on bare scarred wood"),
155:("Dean standing at the wall telephone at night while Rook lies in the doorway","dean_kitchen",None),
157:("rows of plain wooden benches standing unoccupied before a dark judge bench","courthouse",None),
160:("Dean straightening up beside the wall telephone","dean_kitchen",None),
163:("Dean holding the receiver against a shoulder, eyes toward a dark window","dean_kitchen",None),
166:("a thin yellowed receipt lying face up on bare scarred wood",None,"edges curled with age"),
167:("a tin coffee can with the lid seated shut standing at the middle of a table","dean_kitchen",None),
170:("Truman sitting alone at a long table with both hands open in his lap, Dean far off at the wall telephone","dean_kitchen",None),
173:("Truman setting a tin can between a salt shaker and a lamp base, both thumbs under the rim","dean_kitchen",None),
176:("an opened tin can with the lid lying tipped beside it",None,"on a scarred wooden tabletop under a hanging lamp"),
178:("paper folded in quarters packed tight inside a tin can, bound into bricks by aged rubber bands",None,"under warm lamplight"),
180:("Verna looking at the opened tin can, the corner of her mouth lifting","dean_kitchen",None),
182:("Truman lifting the topmost brick of folded paper out of the can","dean_kitchen",None),
184:("Byron seated across the table while Truman holds one weathered hand open and waiting",None,"at a plain kitchen table under a hanging lamp"),
187:("a receipt sliding across bare wood between two pairs of hands",None,"under a low warm lamp"),
190:("Byron sitting at ease squaring up a stack of papers",None,"at a plain kitchen table under a hanging lamp"),
192:("Ivy walking between an open laptop and a row of receipts laid along a table, Truman and Dean seated","dean_kitchen",None),
196:("Ivy pointing at a laptop screen, black framed glasses catching the light","dean_kitchen",None),
198:("a thin hotel receipt held between two fingers under a table lamp",None,"above a scarred wooden tabletop"),
201:("Ivy lifting her eyes from the laptop screen, expression level","dean_kitchen",None),
202:("Ivy resting a fingertip on one line of a printed statement",None,"a pale sheet against dark wood"),
204:("a small pawn ticket lying beside a printed statement, the two sheets touching at the edge",None,"on a scarred wooden tabletop"),
206:("Doctor Aitken sitting across the table from Truman and Verna in daylight","dean_kitchen",None),
209:("Doctor Aitken holding a certificate up to read, glasses catching the window light","dean_kitchen",None),
211:("Doctor Aitken raising her eyes from the page, calm green eyes level","dean_kitchen",None),
213:("Truman nudging a bound brick of paper half an inch to the left",None,"across a scarred wooden tabletop"),
215:("two stacks of paper set side by side, one machine printed and one folded in quarters",None,"on bare wood under a lamp"),
217:("Dean and Truman sitting on either side of a scarred table with an opened tin can between them","dean_kitchen",None),
220:("Truman talking with his eyes down on the tabletop under a low lamp","dean_kitchen",None),
223:("Young Truman waiting in a line of travellers, a canvas bag at his feet","airport_1968",None),
226:("Young Truman walking through the concourse with a folded brown paper sack under one arm","airport_1968",None),
228:("Young Truman standing alone in a crowded concourse while every face turns elsewhere","airport_1968",None),
231:("Young Truman facing a man behind a desk who nods and writes on a pad",None,"in a plain office with a wooden counter"),
234:("Young Truman sitting behind the wheel of an old truck cab, afternoon light across the windscreen",None,"dust settled on the glass"),
236:("Young Truman holding a thin stamped letter in both hands",None,"against a plain painted wall"),
239:("Truman sitting under a low kitchen lamp with an opened tin can at his elbow","dean_kitchen",None),
241:("Dean sitting across the table with the eyes lowered","dean_kitchen",None),
243:("Dean sitting on an upturned feed crate at the table while Rook lies in the doorway","dean_kitchen",None),
246:("Dean holding both hands around a cold coffee mug, shoulders lowered","dean_kitchen",None),
248:("a lone pickup parked at an angle in the gravel lot of a low roadside highway diner at dusk",None,"plate glass windows lit behind it"),
250:("Rook lying across a kitchen doorway with the light dividing his body","dean_kitchen",None),
252:("Dean sitting at the table looking toward the doorway where Rook lies","dean_kitchen",None),
254:("Dean facing Truman who sits straight backed across the table","dean_kitchen",None),
256:("Truman and Dean sitting on either side of the table with the opened can between them","dean_kitchen",None),
259:("Truman pushing a pale green receipt folded in quarters across bare wood with two fingers",None,"under a low warm lamp"),
262:("Rook resting his head on the knee of Dean, all four feet inside the room","dean_kitchen",None),
264:("an opened tin can at the middle of a table ringed by bricks of folded paper",None,"on scarred wood under a hanging lamp"),
267:("a ranch house seen from the dark yard with one kitchen window burning warm yellow","dean_porch",None),
270:("a stapled typed document lying square on a polished office desk",None,"beside a closed folder"),
274:("Dean standing on the porch while fence post shadows stripe the gravel yard","dean_porch",None),
277:("Sheriff Tilghman stepping down from a vehicle in a tan campaign hat, headlights behind","dean_porch",None),
279:("two attendants in clean uniforms stepping down beside a dark blue van with a folder of paperwork","dean_porch",None),
281:("Rook lying across the bottom step with the head lowered and the body drawn tight","dean_porch",None),
284:("Dean standing on the porch lowering one hand to call Rook back","dean_porch",None),
287:("Rook sitting at the left knee of Dean on the porch boards, head lifted toward the yard","dean_porch",None),
289:("Rook holding his gaze fixed on one point, amber brown eyes steady","dean_porch",None),
291:("Verna stepping onto the porch in a good coat with a purse over one arm, an attendant taking her elbow","dean_porch",None),
294:("Truman standing straight backed on the porch with a tin can clamped under one arm","dean_porch",None),
296:("Truman speaking plainly to Sheriff Tilghman from the porch, leaning on a cane","dean_porch",None),
298:("Sheriff Tilghman writing in a small leather logbook while Truman watches",None,"under the beam of a flashlight"),
300:("a dark blue van pulling away across the gravel, two red tail lights in the drizzle","dean_porch",None),
302:("Dean standing alone in an empty gravel yard at gray daybreak","dean_porch",None),
305:("Dean holding a wall telephone receiver at daybreak, the window pale behind him","dean_kitchen",None),
307:("Dean listening at the telephone, the gaze sharpening","dean_kitchen",None),
309:("Dean gripping a coiled telephone cord pulled taut",None,"against a plain plaster wall"),
311:("Ivy standing at a filing counter with a sheaf of papers in hand",None,"in a county courthouse corridor panelled in dark wood"),
313:("Dean sitting on an upturned crate beside two empty chairs, Rook lying underneath with the chin on a boot","dean_kitchen",None),
316:("Dean leaning beside the telephone with the eyes closed","dean_kitchen",None),
320:("rows of wooden benches filled with fourteen people before a dark judge bench","courthouse",None),
322:("Byron laying files in plastic sleeves out in a straight row across a wooden table","courthouse",None),
326:("Truman walking between the benches on a cane with a tin can clamped under one arm","courthouse",None),
328:("Judge Perrine nodding from the high bench toward Ivy standing below","courthouse",None),
330:("Ivy standing beside a projection screen with one hand raised toward the accounting","courthouse",None),
333:("a dented tin coffee can standing open on a wooden table",None,"in a wide quiet room"),
335:("Ivy setting a hotel bill down beside a printed accounting sheet","courthouse",None),
338:("Byron sitting with the face gone stiff, the courteous smile fading","courthouse",None),
339:("a stack of small mailing certificates fanned slightly apart",None,"on a wooden tabletop"),
342:("a lone metal mailbox on a wooden post beside an empty country road",None,"dry grass along both shoulders"),
344:("Byron standing with both hands braced on the table while Ivy waits","courthouse",None),
346:("Byron speaking up toward the bench with the chin slightly raised, Judge Perrine listening","courthouse",None),
348:("Byron turned toward Truman who sits holding a tin can on his lap","courthouse",None),
349:("Ivy standing level and composed behind thin black framed glasses, Byron seated beyond","courthouse",None),
352:("Truman rising on a cane in the middle of the room as the benches turn toward him","courthouse",None),
354:("Truman drawing a brittle rubber band off a bundle of folded paper",None,"over a wooden tabletop"),
356:("Truman reading aloud from a sheet held in one hand, eyes narrowed","courthouse",None),
359:("Verna in the benches lifting a hand to touch the bare fourth finger","courthouse",None),
361:("Truman standing on a cane reading from paper, tall windows behind","courthouse",None),
364:("Byron sitting with the courteous smile gone entirely","courthouse",None),
366:("folded quarters of paper lying open across a weathered palm",None,"in even room light"),
367:("Judge Perrine leaning forward over the high bench toward Verna in the benches","courthouse",None),
369:("Verna lifting her eyes to the bench and answering plainly","courthouse",None),
371:("Judge Perrine signing a file at the high bench, window light falling across the benches","courthouse",None),
375:("Truman sitting down in the front bench with a tin can on his lap while Byron walks out far behind","courthouse",None),
379:("Truman lifting the face into the light from the tall windows","courthouse",None),
381:("rows of wooden benches standing empty after the hearing, early sun through the tall windows","courthouse",None),
384:("papers and a brown envelope lying across a kitchen table","dean_kitchen",None),
386:("a lit glass jewelry case standing among crowded shelves of secondhand goods","pawn_shop",None),
389:("Dean laying counted cash on the glass top of a display case","pawn_shop",None),
391:("Truman lifting the eyes from a brown envelope toward Dean","dean_kitchen",None),
394:("Verna stopping short of the front step in a good coat","baird_house",None),
396:("Verna standing on the painted step with a key closed inside one hand","baird_house",None),
399:("Verna closing one weathered hand tight around a worn brass key",None,"against the fabric of a good coat"),
401:("Dean carrying a third wooden chair down the stairs while Verna sits at the table","dean_kitchen",None),
404:("Dean setting a third chair against the table while Truman watches from his seat","dean_kitchen",None),
407:("Truman standing at the tower base holding a toolbox while Dean works on the ladder above","windmill_pasture",None),
411:("Truman writing in a new spiral notebook resting on a truck hood",None,"open prairie beyond the fender"),
415:("Truman standing by the stock tank watching the windmill wheel turn over green ground","windmill_pasture",None),
418:("Truman shrugging beside the tank while Dean glances over from the frame edge","windmill_pasture",None),
420:("a scarred kitchen table ringed by four wooden chairs","dean_kitchen",None),
422:("Dean opening out a pale green receipt folded in quarters between both hands",None,"over a coat laid across a table"),
424:("Dean looking down at a thin slip held in one hand, the gaze halted","dean_kitchen",None),
426:("a single pickup standing alone at midday in the gravel lot of a low roadside highway diner",None,"plate glass windows dark behind it"),
429:("Truman sitting in a vinyl booth over a full coffee cup, plate glass window behind","diner_kearney",None),
431:("Dean facing Truman across the kitchen table under a warm hanging lamp","dean_kitchen",None),
433:("Rook lying under the table among four chair legs with one paw across a boot toe","dean_kitchen",None),
435:("Dean looking down at Rook under the table, warm lamplight across the face","dean_kitchen",None),
438:("Dean, Truman and Verna gathered at a supper table set for four","dean_kitchen",None),
441:("Verna passing a plate of bread across the table while Dean reaches to take it","dean_kitchen",None),
444:("Verna sitting at the supper table with the corner of the mouth lifting, eyes on her plate","dean_kitchen",None),
446:("a gold wedding band resting beside a dented tin coffee can",None,"on a scarred wooden tabletop"),
448:("warm yellow light standing in a single kitchen window of a darkened ranch house","dean_porch",None),
}


def shot_of(v):
    """Phần 3 — shot type + lens, lấy từ Visual Notes Bước 2 (nguồn duy nhất)."""
    for src, out in SHOTS:
        if v.startswith(src):
            return out + (", full head within frame" if "full head within frame" in v else "")
    raise SystemExit(f"shot type không nhận ra: {v[:60]}")


def part2_of(set_id, extra):
    if set_id:
        return SETTING[set_id] + (f", {extra}" if extra else "")
    if not extra:
        raise SystemExit("scene không có setting id lẫn extra")
    return extra


def build_prompt(sc):
    p1, set_id, extra = PARTS[sc["f"]]
    parts = [p1, part2_of(set_id, extra), shot_of(sc["v"]), MOOD[sc["m"]], STYLE]
    text = ", ".join(parts)
    if any(c in FLASHBACK_IDS for c in sc["c"]):
        text += ", " + FLASHBACK
    return text


def main():
    ent = parse_srt()
    last = max(ent)
    missing = [sc["f"] for sc in SCENES if sc["f"] not in PARTS]
    assert not missing, f"thiếu PARTS cho entry: {missing}"
    rows = []
    for i, sc in enumerate(SCENES):
        nxt = SCENES[i + 1]["f"] - 1 if i + 1 < len(SCENES) else last
        rows.append((i + 1, ent[sc["f"]][0], ent[nxt][1], sc, build_prompt(sc)))

    out = [f"# Prompt Set: The Coffee Can (Cherry County, Nebraska)",
           f"Style: {STYLE} | Total prompts: {len(rows)}", ""]
    for stt, a, b, sc, text in rows:
        chars = ", ".join(NANO[c] for c in sc["c"]) if sc["c"] else "-"
        out += ["---", f"## {stt}",
                f"**Beat:** {sc['b']} | **Mood:** {sc['m']} | **Duration:** {b-a}s",
                f"**Characters:** {chars}", "**Prompt:**", text, ""]
    (ROOT / "output" / "prompts.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    wc = [len(t.replace("clean frame free of watermarks, logos, or AI icons", "").split())
          for *_, t in rows]
    print(f"WROTE prompts.md — {len(rows)} prompt | từ: min {min(wc)} / trung bình {sum(wc)//len(wc)} / max {max(wc)}")
    return rows


if __name__ == "__main__":
    main()
