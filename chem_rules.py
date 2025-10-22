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
    s = s.replace("•", "·")   # bullet -> middle dot (để có '·5H2O')
    # ===== MỞ RỘNG: đơn vị, chỉ số trên, ký hiệu micro, °F =====
    # (a) Nhiệt độ: oF / ° F  -> °F
    s = re.sub(r'(?<=\d)\s*o\s*F', ' °F', s)     # 77 oF -> 77 °F
    s = re.sub(r'°\s*F', '°F', s)                # 77 ° F -> 77 °F

    # (b) Ký hiệu micro: ug, um (hoặc u g / u m) -> µg, µm
    #     Chỉ thay khi 'u' đứng một mình trước g/m để tránh đụng từ khác.
    s = re.sub(r'\bu\s*(g)\b', r'µ\1', s, flags=re.IGNORECASE)
    s = re.sub(r'\bu\s*(m)\b', r'µ\1', s, flags=re.IGNORECASE)

    # (c) Diện tích/Thể tích cho các bội số phổ biến: km2, m2, cm2, mm2, dm2; km3, m3, cm3, mm3, dm3
    #     (nếu đã có dạng m^2/m^3, các quy tắc trước đó đã xử lý)
    unit_len = r'(?:km|m|cm|mm|dm)'   # thứ tự quan trọng: km trước m
    s = re.sub(rf'\b({unit_len})\s*([23])\b', r'\1<sup>\2</sup>', s)

    # (d) Số mũ âm cho đơn vị thời gian & chiều dài: s-1, min-1, h-1, m-1, m-2, m-3 ...
    unit_pow = r'(?:s|min|h|km|m|cm|mm|dm)'
    # Dạng có dấu mũ ^-n : m^-3, s^-1
    s = re.sub(rf'\b({unit_pow})\s*\^\s*(-[123])\b', r'\1<sup>\2</sup>', s)
    # Dạng không có ^ : m-3, s-1
    s = re.sub(rf'\b({unit_pow})\s*(-[123])\b', r'\1<sup>\2</sup>', s)

    # (e) Trường hợp có khoảng trắng giữa đơn vị và mũ: "m 3", "s  -1"
    s = re.sub(rf'\b({unit_len})\s+([23])\b', r'\1<sup>\2</sup>', s)
    s = re.sub(rf'\b({unit_pow})\s+\^\s*(-[123])\b', r'\1<sup>\2</sup>', s)
    s = re.sub(rf'\b({unit_pow})\s+(-[123])\b', r'\1<sup>\2</sup>', s)

    # --- (MỚI) Chuẩn hoá đơn vị & nhiệt độ ---
    # 1) 'oC' hoặc 'o C' sau số -> '°C'; cũng gom '° C' -> '°C'
    s = re.sub(r'(?<=\d)\s*o\s*C', ' °C', s)     # 25 oC -> 25 °C
    s = re.sub(r'°\s*C', '°C', s)                # 25 ° C -> 25 °C

    # 2) m^3, cm^3, dm^3, mm^3  -> dùng <sup>3>
    s = re.sub(r'\b([cdm]?m)\s*\^\s*([23])\b', r'\1<sup>\2</sup>', s)  # m^3, cm^2...

    # 3) m3, cm3, dm3, mm3 -> <sup>3> (chỉ áp cho đơn vị, không ảnh hưởng CH3)
    s = re.sub(r'\b([cdm]?m)\s*([23])\b', r'\1<sup>\2</sup>', s)       # m3 -> m<sup>3</sup>

    s = re.sub(r'(?<=[A-Za-z\)\]\}])(\d+)', r'<sub>\1</sub>', s)        # H2O, (SO4)3
    s = re.sub(r'(·)\s*(\d+)', r'\1<sub>\2</sub>', s)                    # ·5H2O
    s = re.sub(r'(?<=[\]\)\}])(\d*)([+-])', lambda m: f"<sup>{m.group(1)}{m.group(2)}</sup>", s)
    s = re.sub(r'(?<=[A-Za-z\]\)\}])([+-])', lambda m: f"<sup>{m.group(1)}</sup>", s)  # Na+
    s = re.sub(r'(?<=\b[A-Za-z0-9\]\)\}])\s+(\d[+-])\b', lambda m: f" <sup>{m.group(1)}</sup>", s) # SO4 2-
    s = re.sub(r'\^\{([^}]+)\}', lambda m: f"<sup>{m.group(1)}</sup>", s) # ^{2-}
    s = re.sub(r'\^(\d+[+-]?)', lambda m: f"<sup>{m.group(1)}</sup>", s)  # ^2-, ^3+
    s = re.sub(r'\^([+-])', lambda m: f"<sup>{m.group(1)}</sup>", s)      # ^+, ^-
    # --- FIX: nhận diện ion âm/dương kiểu SO4 2-, NO3-, Fe3+ ---
    # Dạng có khoảng trắng giữa gốc và điện tích (SO4 2-, Fe 3+, Cl -)
    s = re.sub(r'(?<=\b[A-Za-z0-9\)\]])\s*(\d?[+-])\b', lambda m: f"<sup>{m.group(1)}</sup>", s)
    # Dạng không có khoảng trắng: SO4-2, NO3-, Fe3+
    s = re.sub(r'(?<=\b[A-Za-z0-9\)\]])(\d?[+-])\b', lambda m: f"<sup>{m.group(1)}</sup>", s)

    return s

# --- footer/page cleaner (an toàn) ---
PURE_PAGE = re.compile(r'^\s*-?\s*\d{1,3}\s*-?\s*$')
PAGE_WORD = re.compile(r'^\s*(Trang|Page)\s*\d+(\s*[/\-]\s*\d+)?\s*$', re.IGNORECASE)
QSTART = re.compile(r'^\s*(Câu|Question|Q)\s*\d+', re.IGNORECASE)
OPTSTART = re.compile(r'^\s*[ABCDĐ]\.?\s+')

# (thêm ngay dưới các import/regex hiện có)
FOOTER_TYHH = re.compile(r'^\s*\d+\s*\|\s*T\s*Y\s*H\s*H\s*$', re.IGNORECASE)
FOOTER_TYHH_COMPACT = re.compile(r'^\s*\d+\s*\|\s*TYHH\s*$', re.IGNORECASE)

def clean_footer(lines):
    from collections import Counter
    freq = Counter([ln.strip() for ln in lines if ln.strip()])
    repeated = {t for t,c in freq.items() if c >= 3 and 4 <= len(t) <= 60}
    kept, removed = [], []
    for i, ln in enumerate(lines):
        s = ln.strip()
        rm = False
        # ➊ xoá số trang kiểu " 3 " hoặc "Trang 3/7"
        if PURE_PAGE.match(s) or PAGE_WORD.match(s):
            rm = True
        # ➋ xoá mẫu footer TYHH kiểu "4 | T Y H H" hoặc "4 | TYHH"
        elif FOOTER_TYHH.match(s) or FOOTER_TYHH_COMPACT.match(s):
            rm = True
        # ➌ xoá dòng ngắn lặp lại nhiều lần (nhưng không phải nội dung thật)
        elif s in repeated:
            if QSTART.match(s) or OPTSTART.match(s):
                rm = False
            elif any(sym in s for sym in ["->","<->","<=>","⇌","→","↔","⟶","=","+"]):
                rm = False
            elif re.search(r'\b(Phần|Câu|Bài)\b', s, re.IGNORECASE):
                rm = False
            else:
                rm = True
        if rm: removed.append({"i": i, "text": ln})
        else: kept.append(ln)
    return kept, removed
def merge_broken_paragraphs(lines):
    """
    Gộp các dòng bị ngắt giữa chừng (khi câu chưa kết thúc).
    Quy tắc:
    - Nếu dòng không kết thúc bằng dấu chấm, hỏi, chấm than, hoặc dấu hai chấm,
      và dòng kế tiếp bắt đầu bằng chữ thường -> nối 2 dòng lại.
    """
    merged = []
    buffer = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            # dòng trống: kết thúc đoạn
            if buffer:
                merged.append(buffer.strip())
                buffer = ""
            continue

        if buffer:
            # kiểm tra xem có nên nối với dòng trước không
            if (not buffer.endswith((".", "?", "!", ":", "…"))
                and stripped and stripped[0].islower()):
                buffer += " " + stripped
            else:
                merged.append(buffer.strip())
                buffer = stripped
        else:
            buffer = stripped

    if buffer:
        merged.append(buffer.strip())

    return merged

