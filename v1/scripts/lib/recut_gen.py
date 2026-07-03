#!/usr/bin/env python3
"""
recut_gen.py — talking-head-recut composition generator.

Emits a static hyperframes index.html from a beats JSON + niche preset.
Video plays full-bleed underneath; each beat is a designed overlay card.
Framing beats (split / pip) tween #video-wrap; everything else is full-bleed.

Usage:
  python recut_gen.py --beats beats.json --niche life \
      --video input-video.mp4 --dur 501.3 --width 1920 --height 1080 \
      --out public/index.html

beats.json: list of objects, each:
  { "t0": 8.0, "t1": 17.4, "type": "callout",
    "kicker": "and yet", "body": "still <em>falling short</em>", "sub": "" }

Body conventions per type:
  callout/big/split/pip/mask/pull  -> line (may contain <em>word</em>); pull.sub = attribution
  per_word                         -> sentence; <em>word</em> emphasised
  list/checklist/chip/flow/timeline/cta -> items joined by "|"
  chapter                          -> items "|"  (rendered 1 2 3)
  comparison                       -> "A|B"      (B emphasised); sub = caption
  before_after                     -> "before|after"
  definition                       -> "Term|the gloss text"
  stat                             -> "FROM>TO|UNIT|label"   e.g. "0>90|%|of mornings"
  section                          -> kicker="01", body="Title", sub="subtitle"
  diagram                          -> nodes "|"  (default engine loop if empty); sub = caption
"""
import argparse, json, re, html as _html

# ---------- niche presets ----------
NICHES = {
    "ds":     dict(accent="#4cc9f0", accent2="#22d3ee", bg="#0b1016", text="#eaf6fb",
                   ink="#08131a", head="Inter", hand=False, serif=False, sec="#0a2733"),
    "life":   dict(accent="#ffca3a", accent2="#ffb703", bg="#0b0805", text="#f7f3ec",
                   ink="#17120a", head="Inter", hand=False, serif=False, sec="#3a2905"),
    "poetry": dict(accent="#e9b877", accent2="#bf5700", bg="#0d0a05", text="#f6efe1",
                   ink="#1a1206", head="PoemSerif", hand=True, serif=True, sec="#241804"),
}

def em(s, ink):
    # ink=True -> accent-text + grow underline (poetry); else highlighter bar (ds/life)
    if ink:
        return re.sub(r"<em>(.*?)</em>",
            r'<span class="em ink"><span class="em-tx2">\1</span><i class="em-bar"></i></span>', s)
    return re.sub(r"<em>(.*?)</em>",
        r'<span class="em"><span class="em-hi"></span><span class="em-tx">\1</span></span>', s)

def esc(s): return _html.escape(s or "")

# ---------- per-type card inner-HTML ----------
def build_card(i, b, P, N, port=False):
    t0,t1 = b["t0"], b["t1"]; typ=b.get("type","callout")
    cid=f"card-{i:02d}"; kick=b.get("kicker",""); body=b.get("body",""); sub=b.get("sub","")
    ink = P["hand"]
    E = lambda s: em(s, ink)
    K = f'<div class="kick" id="{cid}-k">{esc(kick)}</div>' if kick else ""
    S = f'<div class="sub" id="{cid}-s">{esc(sub)}</div>' if sub else ""
    HL = lambda cls="hl": f'<div class="{cls}" id="{cid}-h">{E(body)}</div>'
    items = body.split("|") if body else []

    if typ=="big":
        inner=f'<div class="scrim big"></div><div class="bidx" id="{cid}-i">{i:02d} / {N:02d}</div><div class="bwrap">{K}{HL()}{S}</div>'
    elif typ=="mask":
        inner=f'<div class="scrim big"></div><div class="bwrap">{K}<div class="hl mask" id="{cid}-h">{E(body)}</div>{S}</div>'
    elif typ=="callout":
        inner=f'<div class="scrim band"></div><div class="cowrap">{K}{HL()}{S}</div>'
    elif typ=="pull":
        inner=f'<div class="scrim big"></div><div class="pullwrap"><div class="pullmark">&ldquo;</div>{HL("pl")}<div class="pullrule" id="{cid}-r"></div>{S}</div>'
    elif typ=="per_word":
        toks=re.findall(r"<em>.*?</em>|\S+", body); spans=[]
        for j,w in enumerate(toks):
            spans.append(f'<span class="w" id="{cid}-w{j}">{E(w)}</span>')
        inner=f'<div class="scrim band"></div><div class="cowrap">{K}<div class="hl pw">{" ".join(spans)}</div>{S}</div>'
    elif typ=="split":
        pc=" port" if port else ""
        inner=f'<div class="sp-panel{pc}"><div class="sp-in">{K}{HL()}{S}</div></div>'
    elif typ=="pip":
        pc=" port" if port else ""
        lab=f'<div class="pip-label{pc}" id="{cid}-s">{esc(sub)}</div>' if sub else ""
        inner=f'<div class="scrim pipbg{pc}"></div><div class="pip-wrap{pc}">{K}{HL()}</div>{lab}'
    elif typ=="section":
        inner=(f'<div class="sec-bg"></div><div class="sec-wrap">'
               f'<div class="sec-num" id="{cid}-n">{esc(kick)}</div>'
               f'<div class="sec-title" id="{cid}-h">{E(body)}</div>'
               f'<div class="sec-rule" id="{cid}-r"></div><div class="sec-sub" id="{cid}-s">{esc(sub)}</div></div>')
    elif typ=="stat":
        m=body.split("|"); rng=(m[0] if m else "0>0"); unit=(m[1] if len(m)>1 else ""); lab=(m[2] if len(m)>2 else "")
        fr,_,to=rng.partition(">"); to=to or fr
        inner=(f'<div class="scrim big"></div><div class="stwrap">{K}'
               f'<div class="stnum"><span id="{cid}-n" data-to="{to}" data-from="{fr or 0}">{fr or 0}</span>'
               f'<span class="stunit">{esc(unit)}</span></div>'
               f'<div class="stlab" id="{cid}-h">{E(lab)}</div>{S}</div>')
    elif typ=="comparison":
        a=items[0] if items else ""; c=items[1] if len(items)>1 else ""
        inner=(f'<div class="scrim big"></div><div class="cmpwrap">{K}<div class="cmprow">'
               f'<div class="cmpcol dim" id="{cid}-a">{E(a)}</div>'
               f'<div class="cmpvs" id="{cid}-v">vs</div>'
               f'<div class="cmpcol hot" id="{cid}-b">{E(c)}</div></div>{S}</div>')
    elif typ=="before_after":
        a=items[0] if items else ""; c=items[1] if len(items)>1 else ""
        inner=(f'<div class="scrim big"></div><div class="bawrap">{K}<div class="barow">'
               f'<div class="bacol" id="{cid}-a"><span class="balbl">before</span>{E(a)}</div>'
               f'<div class="baarr" id="{cid}-v">&rarr;</div>'
               f'<div class="bacol hot" id="{cid}-b"><span class="balbl">after</span>{E(c)}</div></div>{S}</div>')
    elif typ=="definition":
        term=items[0] if items else ""; gloss=items[1] if len(items)>1 else ""
        inner=(f'<div class="scrim band"></div><div class="defwrap">{K}'
               f'<div class="defterm" id="{cid}-h">{E(term)}</div>'
               f'<div class="defgloss" id="{cid}-s">{E(gloss)}</div></div>')
    elif typ=="diagram":
        nodes=items if items else ["Meditation","Focused work","Proof it matters"]
        row=[]
        for j,n in enumerate(nodes):
            if j: row.append(f'<div class="dg-arr" id="{cid}-a{j}">&rarr;</div>')
            row.append(f'<div class="dg-node" id="{cid}-n{j}">{E(n)}</div>')
        inner=(f'<div class="scrim big"></div><div class="dg-wrap">{K}<div class="dg-row">{"".join(row)}</div>'
               f'<div class="dg-loop" id="{cid}-l">&#8635;&nbsp; it loops back</div>{S}</div>')
    elif typ in ("list","checklist","chip","flow","timeline","chapter","cta"):
        rows=[]
        for j,it in enumerate(items):
            if typ=="chapter":
                rows.append(f'<div class="crow" id="{cid}-r{j}"><span class="cnum">{j+1}</span><span class="clab">{E(it)}</span></div>')
            elif typ=="cta":
                rows.append(f'<div class="ctarow" id="{cid}-r{j}">{E(it)}</div>')
            elif typ=="chip":
                rows.append(f'<span class="chip" id="{cid}-r{j}">{E(it)}</span>')
            elif typ=="checklist":
                rows.append(f'<div class="lrow" id="{cid}-r{j}"><span class="ltick">&#10003;</span><span class="ltx">{E(it)}</span></div>')
            elif typ=="flow":
                sep='<span class="farr">&rarr;</span>' if j else ''
                rows.append(f'{sep}<span class="fnode" id="{cid}-r{j}">{E(it)}</span>')
            elif typ=="timeline":
                rows.append(f'<div class="trow" id="{cid}-r{j}"><span class="tdot"></span><span class="ttx">{E(it)}</span></div>')
            else:  # list
                rows.append(f'<div class="lrow" id="{cid}-r{j}"><span class="ldot"></span><span class="ltx">{E(it)}</span></div>')
        rh="".join(rows)
        if typ=="chapter":
            inner=f'<div class="scrim big"></div><div class="cwrap">{K}<div class="crows">{rh}</div>{S}</div>'
        elif typ=="cta":
            inner=f'<div class="scrim ctabg"></div><div class="ctawrap"><div class="mark" id="{cid}-m">{esc(kick)}</div><div class="ctalines">{rh}</div></div>'
        elif typ=="chip":
            inner=f'<div class="scrim band"></div><div class="cowrap">{K}<div class="chiprow">{rh}</div>{S}</div>'
        elif typ=="flow":
            inner=f'<div class="scrim big"></div><div class="flwrap">{K}<div class="flrow">{rh}</div>{S}</div>'
        elif typ=="timeline":
            inner=f'<div class="scrim band"></div><div class="lwrap">{K}<div class="trows">{rh}</div></div>'
        else:
            inner=f'<div class="scrim band"></div><div class="lwrap">{K}<div class="lrows">{rh}</div></div>'
    else:
        inner=f'<div class="scrim band"></div><div class="cowrap">{K}{HL()}{S}</div>'

    return (f'  <div class="card-host clip" data-card-id="{cid}" data-start="{t0}" '
            f'data-duration="{round(t1-t0,3)}" data-track-index="2" '
            f'style="left:0;top:0;width:{{W}}px;height:{{H}}px;visibility:hidden;opacity:0;">\n'
            f'    <div class="card" data-card-id="{cid}"><div class="root">{inner}</div></div>\n  </div>')

# ---------- per-type GSAP ----------
def build_gsap(i, b):
    t0,t1=b["t0"],b["t1"]; typ=b.get("type","callout"); cid=f"card-{i:02d}"
    kick=b.get("kicker",""); body=b.get("body",""); sub=b.get("sub","")
    L=[f"enter('{cid}',{t0});"]
    kf = (round(t0+0.15,3))
    if kick and typ not in ("section","cta"): L.append(f"fade('#{cid}-k',{kf},0.45);")
    def line(sel, at):
        L.append(f"rise('{sel}',{round(at,3)},0.6);"); L.append(f"hi('{sel}',{round(at+0.55,3)});")

    if typ in ("callout","big","split","pip"):
        ht=t0+(0.5 if kick else 0.25); line(f'#{cid}-h',ht)
        if typ=="big": L.append(f"fade('#{cid}-i',{round(t0+0.2,3)},0.5);")
        if sub: L.append(f"fade('#{cid}-s',{round(ht+0.7,3)},0.5);")
    elif typ=="mask":
        ht=t0+(0.5 if kick else 0.25)
        L.append(f"mask('#{cid}-h',{round(ht,3)});"); L.append(f"hi('#{cid}-h',{round(ht+0.6,3)});")
        if sub: L.append(f"fade('#{cid}-s',{round(ht+0.8,3)},0.5);")
    elif typ=="pull":
        ht=t0+0.3; L.append(f"rise('#{cid}-h',{round(ht,3)},0.6);"); L.append(f"hi('#{cid}-h',{round(ht+0.55,3)});")
        L.append(f"gx('#{cid}-r',{round(ht+0.7,3)},120);")
        if sub: L.append(f"fade('#{cid}-s',{round(ht+0.9,3)},0.5);")
    elif typ=="per_word":
        toks=re.findall(r"<em>.*?</em>|\S+", body); base=t0+(0.5 if kick else 0.25)
        for j in range(len(toks)):
            L.append(f"pop('#{cid}-w{j}',{round(base+j*0.14,3)},0.34);")
        last=base+len(toks)*0.14
        L.append(f"hi('.card[data-card-id=\"{cid}\"]',{round(last,3)});")
        if sub: L.append(f"fade('#{cid}-s',{round(last+0.2,3)},0.5);")
    elif typ=="section":
        L.append(f"pop('#{cid}-n',{round(t0+0.15,3)},0.5);")
        L.append(f"rise('#{cid}-h',{round(t0+0.4,3)},0.55);")
        L.append(f"gx('#{cid}-r',{round(t0+0.7,3)},120);")
        if sub: L.append(f"fade('#{cid}-s',{round(t0+0.85,3)},0.5);")
    elif typ=="stat":
        L.append(f"count('#{cid}-n',{round(t0+0.35,3)});")
        L.append(f"rise('#{cid}-h',{round(t0+0.5,3)},0.55);")
        if sub: L.append(f"fade('#{cid}-s',{round(t0+0.9,3)},0.5);")
    elif typ in ("comparison","before_after"):
        L.append(f"rise('#{cid}-a',{round(t0+0.35,3)},0.5);")
        L.append(f"pop('#{cid}-v',{round(t0+0.7,3)},0.4);")
        L.append(f"rise('#{cid}-b',{round(t0+0.95,3)},0.5);")
        if sub: L.append(f"fade('#{cid}-s',{round(t0+1.4,3)},0.5);")
    elif typ=="definition":
        L.append(f"rise('#{cid}-h',{round(t0+0.3,3)},0.55);")
        L.append(f"fade('#{cid}-s',{round(t0+0.7,3)},0.5);")
    elif typ=="diagram":
        nodes=(body.split("|") if body else ["a","b","c"]); base=t0+0.6; k=0
        for j in range(len(nodes)):
            if j: L.append(f"pop('#{cid}-a{j}',{round(base+k*0.35,3)},0.4);"); k+=1
            L.append(f"pop('#{cid}-n{j}',{round(base+k*0.35,3)},0.45);"); k+=1
        L.append(f"fade('#{cid}-l',{round(base+k*0.35+0.2,3)},0.6);")
        if sub: L.append(f"fade('#{cid}-s',{round(base+k*0.35+0.6,3)},0.5);")
    elif typ in ("list","checklist","chip","flow","timeline","chapter","cta"):
        items=body.split("|"); base=t0+(0.5 if kick else 0.2)
        if typ=="cta": L.append(f"fade('#{cid}-m',{round(t0+0.2,3)},0.5);")
        for j in range(len(items)):
            at=round(base+0.35+j*0.5,3)
            (L.append(f"pop('#{cid}-r{j}',{at},0.45);") if typ in ("chip","flow")
             else L.append(f"rise('#{cid}-r{j}',{at},0.5);"))
            if "<em>" in items[j]: L.append(f"hi('#{cid}-r{j}',{round(at+0.45,3)});")
        if typ=="chapter" and sub: L.append(f"fade('#{cid}-s',{round(base+0.35+len(items)*0.5,3)},0.5);")
    L.append(f"exit('{cid}',{round(t1-0.4,3)});")
    return "    "+" ".join(L)

# ---------- video framing per beat ----------
def vstate(typ,W,H):
    """Video-wrapper geometry per beat, aspect-aware. PiP preserves source aspect
    (h=w*H/W). Landscape split=left-text/right-video; portrait split=top-video/
    bottom-text. Everything else full-bleed (or dimmed for section/cta)."""
    port = H>W
    if typ=="split":
        if port: return dict(l=0,t=0,w=W,h=int(H*0.52),op=1,cls="video-wrapper",z=1)
        return dict(l=int(W*0.44),t=0,w=W-int(W*0.44),h=H,op=1,cls="video-wrapper",z=1)
    if typ=="pip":
        if port:
            pw=int(W*0.42); ph=int(pw*H/W)
            return dict(l=W-pw-int(W*0.05),t=int(H*0.06),w=pw,h=ph,op=1,cls="video-wrapper pip-pill",z=50)
        pw=int(W*0.265); ph=int(pw*H/W)
        return dict(l=W-pw-int(W*0.04),t=H-ph-int(H*0.08),w=pw,h=ph,op=1,cls="video-wrapper pip-pill",z=50)
    if typ in ("section","cta"): return dict(l=0,t=0,w=W,h=H,op=0.14,cls="video-wrapper",z=1)
    return dict(l=0,t=0,w=W,h=H,op=1,cls="video-wrapper",z=1)

def vid_tweens(beats,W,H):
    """Video is full-bleed by default; framing beats (split/pip) and dim beats
    (section/cta) tween #video-wrap in at t0-0.5 and back to full-bleed at their
    exit, UNLESS the next beat continues the same state with no real gap. This
    prevents the video staying parked over black during inter-card gaps."""
    out=[]; full=vstate("callout",W,H); prev=full
    def emit(st,t):
        out.append(f"    tl.set(W,{{className:'{st['cls']}',zIndex:{st['z']}}},{max(0.0,round(t,3))});")
        out.append(f"    tl.to(W,{{left:{st['l']},top:{st['t']},width:{st['w']},height:{st['h']},opacity:{st['op']},duration:0.55,ease:'power2.inOut'}},{max(0.0,round(t,3))});")
    for idx,b in enumerate(beats):
        st=vstate(b.get("type","callout"),W,H)
        if st!=prev:
            emit(st,b["t0"]-0.5); prev=st
        if st!=full:
            nxt=vstate(beats[idx+1].get("type","callout"),W,H) if idx+1<len(beats) else full
            gap=(beats[idx+1]["t0"]-b["t1"]) if idx+1<len(beats) else 1.0
            if nxt!=st or gap>0.15:            # not a same-state continuation -> return to full
                emit(full,b["t1"]); prev=full
    return "\n".join(out)

KNOWN_TYPES={"callout","big","per_word","mask","pull","list","checklist","chip",
             "chapter","section","definition","stat","comparison","before_after",
             "timeline","flow","diagram","split","pip","cta"}
STAGGER_TYPES={"list":0.5,"checklist":0.5,"chip":0.5,"chapter":0.5,"cta":0.5,
               "timeline":0.5,"flow":0.5,"diagram":0.7}

def validate_beats(beats, dur):
    """Fail loudly on the silent-failure classes: unknown type (renders a blank
    dark scrim), inverted/zero-length timing, out-of-range, non-numeric stat.
    Warn on staggered intros that overrun the beat."""
    import sys
    errs=[]; warns=[]
    for i,b in enumerate(sorted(beats,key=lambda x:x["t0"]),1):
        typ=b.get("type","callout"); t0=b.get("t0"); t1=b.get("t1"); tag=f"beat {i} ({typ})"
        if typ not in KNOWN_TYPES: errs.append(f"{tag}: unknown type '{typ}'")
        if t0 is None or t1 is None: errs.append(f"{tag}: missing t0/t1"); continue
        if t1<=t0: errs.append(f"{tag}: t1({t1})<=t0({t0})")
        if t1>dur+0.05: errs.append(f"{tag}: t1({t1})>dur({dur})")
        if t1-t0<1.0: warns.append(f"{tag}: only {round(t1-t0,2)}s — too short to read/animate")
        if typ=="stat":
            m=(b.get("body","")).split("|"); rng=m[0] if m else ""
            for v in rng.replace(">","|").split("|"):
                if v and not re.fullmatch(r"-?\d+(\.\d+)?",v):
                    errs.append(f"{tag}: stat value '{v}' is not numeric (count-up needs numbers)")
        if typ in STAGGER_TYPES:
            n=len((b.get("body","")).split("|")); need=0.35+n*STAGGER_TYPES[typ]+0.6
            if need>(t1-t0-0.4):
                warns.append(f"{tag}: {n} items need ~{round(need,1)}s but beat is {round(t1-t0,1)}s — rows will pop after exit")
    for w in warns: print(f"[recut_gen] WARN {w}", file=sys.stderr)
    if errs:
        raise SystemExit("[recut_gen] beats.json invalid:\n  - " + "\n  - ".join(errs))

# ---------- assemble ----------
def render(beats, niche, video, dur, W, H, out, focus="55% 30%"):
    P=NICHES[niche]; N=len(beats)
    beats=sorted(beats,key=lambda b:b["t0"])
    validate_beats(beats,dur); port=H>W
    hosts="\n".join(build_card(i+1,b,P,N,port).replace("{W}",str(W)).replace("{H}",str(H)) for i,b in enumerate(beats))
    tls="\n".join(build_gsap(i+1,b) for i,b in enumerate(beats))
    vids=vid_tweens(beats,W,H); iv=vstate("callout",W,H)  # video starts full-bleed
    panel_w=int(W*0.44)
    doc=CSS_JS(P,dur,W,H,hosts,tls,vids,iv,panel_w,video,focus)
    open(out,"w").write(doc)
    from collections import Counter
    return dict(cards=N, types=dict(Counter(b.get("type","callout") for b in beats)))

def CSS_JS(P,dur,W,H,hosts,tls,vids,iv,panel_w,video,focus="55% 30%"):
    head_serif = "'PoemSerif',serif" if P["serif"] else "'Inter',sans-serif"
    hand = "'Caveat',cursive" if P["hand"] else "'Inter',sans-serif"
    big_font = head_serif if P["serif"] else "'Inter',sans-serif"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<style>
@font-face{{font-family:'Inter';src:url('fonts/Inter-700-latin.woff2') format('woff2');font-weight:700;font-display:block}}
@font-face{{font-family:'Inter';src:url('fonts/Inter-400-latin.woff2') format('woff2');font-weight:400;font-display:block}}
@font-face{{font-family:'Caveat';src:url('fonts/Caveat-700-latin.woff2') format('woff2');font-weight:700;font-display:block}}
@font-face{{font-family:'Caveat';src:url('fonts/Caveat-400-latin.woff2') format('woff2');font-weight:400;font-display:block}}
@font-face{{font-family:'PoemSerif';src:url('fonts/Georgia.ttf') format('truetype');font-weight:400;font-style:normal;font-display:block}}
@font-face{{font-family:'PoemSerif';src:url('fonts/Georgia-Italic.ttf') format('truetype');font-weight:400;font-style:italic;font-display:block}}
:root{{--accent:{P['accent']};--accent2:{P['accent2']};--text:{P['text']};--ink:{P['ink']};--bg:{P['bg']}}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:100%;height:100%;overflow:hidden;background:#000;font-family:'Inter',ui-sans-serif,system-ui,sans-serif}}
#stage{{position:relative;width:100%;height:100%;overflow:hidden;background:#000}}
.video-wrapper{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;overflow:hidden;z-index:1}}
.video-wrapper video{{width:100%;height:100%;object-fit:cover;object-position:{focus}}}
.video-wrapper.pip-pill{{border-radius:22px;border:3px solid rgba(255,255,255,.9);box-shadow:0 22px 60px rgba(0,0,0,.6)}}
.card-host{{position:absolute;pointer-events:none;overflow:hidden;z-index:2}}
.card-host .card,.card-host .root{{position:relative;width:100%;height:100%;overflow:hidden}}
.scrim{{position:absolute;inset:0}}
.scrim.band{{background:linear-gradient(to top,rgba(6,5,3,.94) 0%,rgba(6,5,3,.86) 16%,rgba(6,5,3,.3) 42%,rgba(6,5,3,0) 60%)}}
.scrim.big{{background:linear-gradient(to right,rgba(5,4,2,.85) 0%,rgba(5,4,2,.66) 52%,rgba(5,4,2,.4) 100%)}}
.scrim.pipbg{{background:linear-gradient(115deg,rgba(18,13,4,.97) 0%,rgba(8,6,3,.9) 58%,rgba(8,6,3,.62) 100%)}}
.scrim.ctabg{{background:radial-gradient(80% 70% at 50% 46%,{P['sec']},rgba(4,3,1,.93))}}
.em{{position:relative;display:inline-block;white-space:nowrap}}
.em-hi{{position:absolute;left:-6px;right:-6px;top:12%;bottom:14%;background:var(--accent);border-radius:5px;transform:scaleX(0);transform-origin:left center;z-index:0}}
.em-tx{{position:relative;z-index:1;color:var(--text);padding:0 2px}}  /* starts readable; hi() flips to --ink as the bar sweeps in */
.em.ink .em-tx2{{color:var(--accent)}}
.em.ink .em-bar{{position:absolute;left:0;bottom:6px;height:6px;width:0;background:var(--accent2);border-radius:4px;opacity:.85}}
.kick{{font-family:'Inter',sans-serif;font-weight:700;font-size:26px;letter-spacing:.34em;text-transform:uppercase;color:var(--accent);opacity:0}}
.sub{{font-family:'Inter',sans-serif;font-weight:400;font-size:30px;color:rgba(247,243,236,.72);margin-top:22px;opacity:0}}
.cowrap{{position:absolute;left:96px;right:120px;bottom:118px}}
.cowrap .kick{{margin-bottom:24px}}
.hl{{font-family:{hand};font-weight:700;font-size:66px;line-height:1.1;color:var(--text);opacity:0;text-shadow:0 2px 24px rgba(0,0,0,.5)}}
.hl.pw{{opacity:1}} .hl.pw .w{{display:inline-block;opacity:0}}
.bwrap{{position:absolute;left:104px;right:120px;top:50%;transform:translateY(-50%)}}
.bwrap .kick{{margin-bottom:26px}}
.bwrap .hl{{font-family:{big_font};font-size:132px;line-height:1.02;letter-spacing:-.01em}}
.bidx{{position:absolute;top:70px;right:90px;font-weight:700;font-size:24px;letter-spacing:.24em;color:rgba(247,243,236,.5);opacity:0}}
.pullwrap{{position:absolute;left:120px;right:150px;top:50%;transform:translateY(-50%)}}
.pullmark{{font-family:{head_serif};font-size:160px;line-height:.5;color:var(--accent);opacity:.5;height:70px}}
.pl{{font-family:{head_serif};font-size:86px;line-height:1.14;color:var(--text);opacity:0;margin-top:10px}}
.pullrule{{width:0;height:5px;background:var(--accent);margin-top:34px;border-radius:3px}}
.sp-panel{{position:absolute;left:0;top:0;bottom:0;width:{panel_w}px;background:linear-gradient(135deg,rgba(7,5,3,.98),rgba(13,10,5,.93));border-right:4px solid var(--accent)}}
.sp-in{{position:absolute;top:50%;left:74px;right:60px;transform:translateY(-50%)}}
.sp-in .kick{{margin-bottom:24px}} .sp-in .hl{{font-size:72px;line-height:1.08}}
/* portrait split: bottom text panel, video sits top */
.sp-panel.port{{left:0;right:0;top:52%;bottom:0;width:100%;border-right:none;border-top:4px solid var(--accent);background:linear-gradient(to top,rgba(7,5,3,.98),rgba(13,10,5,.94))}}
.sp-panel.port .sp-in .hl{{font-size:66px}}
.pip-wrap{{position:absolute;left:90px;right:{int(W*0.38)}px;top:50%;transform:translateY(-50%)}}
.pip-wrap .kick{{margin-bottom:24px}} .pip-wrap .hl{{font-size:64px;line-height:1.12}}
/* portrait pip: video top-right, text fills the lower frame */
.pip-wrap.port{{left:70px;right:70px;top:auto;bottom:180px;transform:none}}
.pip-wrap.port .hl{{font-size:70px}}
.pip-label{{position:absolute;left:{int(W*0.69)}px;width:{int(W*0.265)}px;top:{int(H*0.94)}px;text-align:center;font-weight:700;font-size:20px;letter-spacing:.24em;text-transform:uppercase;color:rgba(247,243,236,.6);opacity:0}}
.pip-label.port{{display:none}}
.sec-bg{{position:absolute;inset:0;background:linear-gradient(120deg,{P['sec']} 0%,rgba(12,9,4,.98) 46%,rgba(6,5,2,1) 100%)}}
.sec-wrap{{position:absolute;left:130px;right:120px;top:50%;transform:translateY(-50%)}}
.sec-num{{font-family:'Inter',sans-serif;font-weight:700;font-size:200px;line-height:.86;color:var(--accent);opacity:0}}
.sec-title{{font-family:{big_font};font-weight:700;font-size:104px;color:var(--text);margin-top:6px;opacity:0}}
.sec-rule{{width:0;height:5px;background:var(--accent);margin:34px 0 26px;border-radius:3px}}
.sec-sub{{font-weight:400;font-size:32px;letter-spacing:.06em;color:rgba(247,243,236,.66);opacity:0}}
.stwrap{{position:absolute;left:110px;right:120px;top:50%;transform:translateY(-50%)}}
.stwrap .kick{{margin-bottom:20px}}
.stnum{{font-family:'Inter',sans-serif;font-weight:700;font-size:230px;line-height:.9;color:var(--accent);letter-spacing:-.02em}}
.stunit{{font-size:110px;margin-left:8px}}
.stlab{{font-weight:700;font-size:58px;color:var(--text);margin-top:14px;opacity:0}}
.cmpwrap,.bawrap,.flwrap{{position:absolute;left:100px;right:120px;top:50%;transform:translateY(-50%)}}
.cmpwrap .kick,.bawrap .kick,.flwrap .kick{{margin-bottom:40px}}
.cmprow,.barow{{display:flex;align-items:center;gap:30px}}
.cmpcol,.bacol{{font-weight:700;font-size:76px;color:var(--text);line-height:1.05;flex:1;opacity:0;position:relative}}
.cmpcol.dim{{color:rgba(247,243,236,.45)}} .cmpcol.hot,.bacol.hot{{color:var(--accent)}}
.cmpvs,.baarr{{font-weight:700;font-size:44px;color:var(--accent);opacity:0;flex:none}}
.balbl{{display:block;font-size:22px;letter-spacing:.24em;text-transform:uppercase;color:rgba(247,243,236,.5);margin-bottom:12px}}
.defwrap{{position:absolute;left:96px;right:140px;bottom:120px}}
.defterm{{font-weight:700;font-size:96px;color:var(--accent);opacity:0}}
.defgloss{{font-weight:400;font-size:46px;line-height:1.3;color:var(--text);margin-top:18px;opacity:0}}
.dg-wrap,.flwrap{{position:absolute;left:90px;right:110px;top:50%;transform:translateY(-50%)}}
.dg-wrap .kick{{margin-bottom:44px}}
.dg-row,.flrow{{display:flex;align-items:center;flex-wrap:wrap;gap:6px}}
.dg-node,.fnode{{padding:24px 34px;border:2px solid var(--accent);border-radius:16px;font-weight:700;font-size:44px;color:var(--text);background:rgba(8,6,3,.55);opacity:0}}
.dg-arr,.farr{{font-size:56px;color:var(--accent);margin:0 18px;opacity:0}}
.dg-loop{{margin-top:44px;font-weight:700;font-size:42px;color:var(--accent);opacity:0}}
.dg-wrap .sub,.flwrap .sub{{margin-top:18px}}
.lwrap{{position:absolute;left:96px;right:120px;bottom:110px}}
.lwrap .kick{{margin-bottom:34px}}
.lrow,.trow{{display:flex;align-items:center;font-weight:700;font-size:56px;line-height:1.28;color:var(--text);opacity:0;text-shadow:0 2px 20px rgba(0,0,0,.5)}}
.ldot,.tdot{{flex:none;width:16px;height:16px;border-radius:50%;background:var(--accent);margin-right:28px}}
.ltick{{flex:none;color:var(--accent);font-size:52px;margin-right:26px}}
.trows{{border-left:3px solid rgba(255,255,255,.18);padding-left:4px;margin-left:8px}}
.trow{{margin:18px 0}}
.chiprow{{display:flex;flex-wrap:wrap;gap:20px}}
.chip{{padding:16px 30px;border:2px solid var(--accent);border-radius:999px;font-weight:700;font-size:40px;color:var(--text);opacity:0}}
.cwrap{{position:absolute;left:110px;right:120px;top:50%;transform:translateY(-50%)}}
.cwrap .kick{{margin-bottom:40px}}
.crow{{display:flex;align-items:baseline;opacity:0;margin:10px 0}}
.cnum{{font-weight:700;font-size:64px;color:var(--accent);width:120px;flex:none}}
.clab{{font-weight:700;font-size:92px;color:var(--text);line-height:1.05}}
.cwrap .sub{{margin-top:40px;font-size:28px;letter-spacing:.06em}}
.ctawrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 140px}}
.mark{{font-weight:700;font-size:30px;letter-spacing:.4em;text-transform:uppercase;color:var(--accent);margin-bottom:46px;opacity:0}}
.ctarow{{font-weight:700;font-size:58px;line-height:1.24;color:var(--text);opacity:0;margin:10px 0}}
</style></head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{dur}" data-fps="30" data-width="{W}" data-height="{H}">
  <div class="{iv['cls']}" id="video-wrap" style="left:{iv['l']}px;top:{iv['t']}px;width:{iv['w']}px;height:{iv['h']}px;opacity:{iv['op']};z-index:{iv['z']}">
    <video id="bg-video" src="{video}" muted playsinline data-start="0" data-duration="{dur}" data-track-index="1"></video>
  </div>
{hosts}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function(){{
    var gsap=window.gsap, tl=gsap.timeline({{paused:true}}), W='#video-wrap', INK='{P['ink']}';
    function enter(id,t){{var s='.card-host[data-card-id="'+id+'"]';tl.set(s,{{visibility:'visible'}},t);tl.fromTo(s,{{opacity:0}},{{opacity:1,duration:0.4,ease:'power2.out'}},t);}}
    function exit(id,t){{var s='.card-host[data-card-id="'+id+'"]';tl.to(s,{{opacity:0,duration:0.4,ease:'power2.in'}},t);tl.set(s,{{visibility:'hidden'}},t+0.4);}}
    function fade(sel,t,d){{tl.fromTo(sel,{{opacity:0}},{{opacity:1,duration:(d||0.5),ease:'power2.out'}},t);}}
    function rise(sel,t,d){{tl.fromTo(sel,{{opacity:0,y:26}},{{opacity:1,y:0,duration:(d||0.55),ease:'power3.out'}},t);}}
    function pop(sel,t,d){{tl.fromTo(sel,{{opacity:0,y:14,scale:0.86}},{{opacity:1,y:0,scale:1,duration:(d||0.45),ease:'back.out(1.7)'}},t);}}
    function mask(sel,t){{tl.fromTo(sel,{{opacity:1,clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:0.6,ease:'power2.inOut'}},t);}}
    function gx(sel,t,w){{tl.fromTo(sel,{{width:0}},{{width:(w||120),duration:0.5,ease:'power2.out'}},t);}}
    function hi(sel,t){{tl.to(sel+' .em-hi',{{scaleX:1,duration:0.42,ease:'power2.inOut'}},t);tl.to(sel+' .em-tx',{{color:INK,duration:0.42,ease:'power2.inOut'}},t);tl.to(sel+' .em-bar',{{width:'100%',duration:0.42,ease:'power2.out'}},t);}}
    function count(sel,t){{var el=document.querySelector(sel);if(!el)return;var f=parseFloat(el.getAttribute('data-from'))||0,to=parseFloat(el.getAttribute('data-to'))||0,o={{v:f}};tl.to(o,{{v:to,duration:1.1,ease:'power2.out',onUpdate:function(){{el.textContent=Math.round(o.v);}}}},t);}}
{vids}
{tls}
    window.__timelines=window.__timelines||{{}};
    window.__timelines['talking-head-recut']=tl;
  }})();
  </script>
</div>
</body></html>'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--beats",required=True); ap.add_argument("--niche",required=True,choices=list(NICHES))
    ap.add_argument("--video",default="input-video.mp4"); ap.add_argument("--dur",type=float,required=True)
    ap.add_argument("--width",type=int,default=1920); ap.add_argument("--height",type=int,default=1080)
    ap.add_argument("--focus",default="55% 30%",help="object-position for the video (from the face-x you measured), e.g. '60% 25%'")
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    beats=json.load(open(a.beats))
    r=render(beats,a.niche,a.video,a.dur,a.width,a.height,a.out,a.focus)
    print(f"[recut_gen] {a.out}  niche={a.niche}  {r}")

if __name__=="__main__":
    main()
