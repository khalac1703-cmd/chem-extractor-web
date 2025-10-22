import re
from collections import Counter

ARROW_MAP = [
    ("<=>", "⇌"), ("<->", "↔"),
    ("->", "→"), ("<-", "←"),
    ("=>", "⟶"), ("-->", "→"), ("<--", "←"),
]

def normalize_arrows(s: str, enabled: bool) -> str:
    if not enabled: return s
    for a,b in ARROW_MAP: s = s.replace(a,b)
    return s

def chem_transform_v3(s: str, normalize_ascii_arrows: bool=False) -> str:
    s = normalize_arrows(s, normalize_ascii_arrows)
    s = s.replace("•", "·")
    s = re.sub(r'(?<=[A-Za-z\)\]\}])(\d+)', r'<sub>\1</sub>', s)        # H2O, (SO4)3
    s = re.sub(r'(·)\s*(\d+)', r'\1<sub>\2</sub>', s)                    # ·5H2O
    s = re.sub(r'(?<=[\]\)\}])(\d*)([+-])', lambda m: f"<sup>{m.group(1)}{m.group(2)}</sup>", s)
    s = re.sub(r'(?<=[A-Za-z\]\)\}])([+-])', lambda m: f"<sup>{m.group(1)}</sup>", s)  # Na+
    s = re.sub(r'(?<=\b[A-Za-z0-9\]\)\}])\s+(\d[+-])\b', lambda m: f" <sup>{m.group(1)}</sup>", s) # SO4 2-
    s = re.sub(r'\^\{([^}]+)\}', lambda m: f"<sup>{m.group(1)}</sup>", s) # ^{2-}
    s = re.sub(r'\^(\d+[+-]?)', lambda m: f"<sup>{m.group(1)}</sup>", s)  # ^2-, ^3+
    s = re.sub(r'\^([+-])', lambda m: f"<sup>{m.group(1)}</sup>", s)      # ^+, ^-
    return s

# --- footer/page cleaner (an toàn) ---
PURE_PAGE = re.compile(r'^\s*-?\s*\d{1,3}\s*-?\s*$')
PAGE_WORD = re.compile(r'^\s*(Trang|Page)\s*\d+(\s*[/\-]\s*\d+)?\s*$', re.IGNORECASE)
QSTART = re.compile(r'^\s*(Câu|Question|Q)\s*\d+', re.IGNORECASE)
OPTSTART = re.compile(r'^\s*[ABCDĐ]\.?\s+')

def clean_footer(lines):
    freq = Counter([ln.strip() for ln in lines if ln.strip()])
    repeated = {t for t,c in freq.items() if c >= 3 and 4 <= len(t) <= 60}
    kept, removed = [], []
    for i, ln in enumerate(lines):
        s = ln.strip()
        rm = False
        if PURE_PAGE.match(s) or PAGE_WORD.match(s):
            rm = True
        elif s in repeated:
            if QSTART.match(s) or OPTSTART.match(s): rm = False
            elif any(sym in s for sym in ["->","<->","<=>","⇌","→","↔","⟶","=","+"]): rm = False
            elif re.search(r'\b(Phần|Câu|Bài)\b', s, re.IGNORECASE): rm = False
            else: rm = True
        if rm: removed.append({"i": i, "text": ln})
        else: kept.append(ln)
    return kept, removed
