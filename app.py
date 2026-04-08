import re
import gradio as gr


# =============================================================================
# CITY MAP — abbreviations + full names → canonical Title Case
# =============================================================================
CITY_MAP = {
    # Bangalore
    "blr": "Bangalore", "bengaluru": "Bangalore", "bangalore": "Bangalore",
    # Ballari
    "bly": "Ballari", "ballari": "Ballari", "bellary": "Ballari",
    # Hyderabad
    "hyd": "Hyderabad", "hyderabad": "Hyderabad", "secundarabad": "Hyderabad",
    # Mumbai
    "mum": "Mumbai", "mumbai": "Mumbai", "bombay": "Mumbai",
    # Delhi
    "del": "Delhi", "delhi": "Delhi", "new delhi": "Delhi", "newdelhi": "Delhi",
    # Chennai
    "chn": "Chennai", "chennai": "Chennai", "madras": "Chennai",
    # Kolkata
    "kol": "Kolkata", "kolkata": "Kolkata", "calcutta": "Kolkata",
    # Others
    "pun": "Pune",       "pune": "Pune",
    "ahm": "Ahmedabad",  "ahmedabad": "Ahmedabad",
    "jpr": "Jaipur",     "jaipur": "Jaipur",
    "lko": "Lucknow",    "lucknow": "Lucknow",
    "ngp": "Nagpur",     "nagpur": "Nagpur",
    "noida": "Noida",    "gurgaon": "Gurgaon",    "gurugram": "Gurgaon",
    "mysore": "Mysore",  "mangalore": "Mangalore", "udupi": "Udupi",
    "surat": "Surat",    "patna": "Patna",
    "bhopal": "Bhopal",  "indore": "Indore",
    "vizag": "Visakhapatnam", "visakhapatnam": "Visakhapatnam",
    "coimbatore": "Coimbatore", "cbe": "Coimbatore",
    "kochi": "Kochi",    "cochin": "Kochi",
    "trivandrum": "Thiruvananthapuram", "thiruvananthapuram": "Thiruvananthapuram",
    "chandigarh": "Chandigarh", "amritsar": "Amritsar",
    "bhubaneswar": "Bhubaneswar", "guwahati": "Guwahati",
    "ranchi": "Ranchi",  "raipur": "Raipur",
    "nashik": "Nashik",  "aurangabad": "Aurangabad",
    "agra": "Agra",      "varanasi": "Varanasi",   "allahabad": "Prayagraj",
    "prayagraj": "Prayagraj", "meerut": "Meerut",  "kanpur": "Kanpur",
    "rajkot": "Rajkot",  "vadodara": "Vadodara",   "baroda": "Vadodara",
    "amravati": "Amravati", "kolhapur": "Kolhapur", "solapur": "Solapur",
    "hubli": "Hubli",    "dharwad": "Dharwad",     "belgaum": "Belagavi",
    "belagavi": "Belagavi",
}

# Words that must never be returned as a person's name
NAME_IGNORE = {
    "hi", "hello", "hey", "bro", "sis", "sir", "mam", "madam", "dear",
    "this", "is", "are", "was", "were", "here", "am", "i", "im", "me", "my",
    "myself", "yourself", "himself", "herself",
    "call", "reach", "contact", "text", "ping", "ring",
    "name", "age", "city", "phone", "number", "mobile", "mob", "ph", "tel",
    "from", "in", "at", "and", "the", "a", "an", "or",
    "years", "year", "old", "yrs", "yr", "aged",
    "side", "please", "register", "just", "add",
    "for", "on", "of", "to", "with", "by", "about",
    "lives", "living", "located", "stay", "staying", "residing",
    "not", "no", "yes", "yeah", "okay", "ok", "sure",
    "details", "info", "data", "profile",
    "location", "address", "place",
    "between", "near", "around",
    "hello", "greetings", "dear",
}


# =============================================================================
# STAGE 1 — CSV fast-path (name, age, city, phone)
# =============================================================================
def _try_csv(raw: str):
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 4:
        return None

    name_raw, age_raw, city_raw, phone_raw = parts

    # Validate: age must be digits, phone must be digits
    if not re.fullmatch(r"\d{1,3}", age_raw.strip()):
        return None
    phone_digits = re.sub(r"[\s\-]", "", phone_raw)
    if not re.fullmatch(r"\+?(\d{7,15})", phone_digits):
        return None
    phone_digits = re.sub(r"\D", "", phone_digits)  # strip any +

    # Clean name — strip leading pronoun phrases
    name_clean = re.sub(
        r"(?i)^(?:i'?m|i\s+am|my\s+name\s+is|myself)\s+", "", name_raw
    ).strip() or name_raw

    # Resolve city through map, fallback to Title Case
    city_clean = CITY_MAP.get(city_raw.strip().lower(), city_raw.strip().title())

    return {
        "name":  name_clean.title(),
        "age":   age_raw.strip(),
        "city":  city_clean,
        "phone": phone_digits[-10:],  # keep last 10 digits (handles +91 prefix)
    }


# =============================================================================
# STAGE 2 — Natural-language extraction
# =============================================================================

def _extract_phone(raw: str) -> str:
    """Return first valid 10-digit Indian mobile number."""
    # Strip country code
    cleaned = re.sub(r"\+91[\s\-]?", "", raw)
    cleaned = re.sub(r"\b0(?=[6-9]\d{9}\b)", "", cleaned)

    m = re.search(r"\b([6-9]\d{9})\b", cleaned)
    if m:
        return m.group(1)
    # Spaced format: "98765 43210"
    m = re.search(r"[6-9](?:[\s\-]*\d){9}(?!\d)", cleaned)
    if m:
        digits = re.sub(r"\D", "", m.group())
        if len(digits) == 10:
            return digits
    # Any 10-digit number fallback
    m = re.search(r"\b(\d{10})\b", raw)
    return m.group(1) if m else "unknown"


def _extract_age(raw: str) -> str:
    """Return age as a string, or 'unknown'."""
    t = raw.lower()
    patterns = [
        r"age[d]?\s*(?:is\s*)?[:\-]?\s*(\d{1,3})",    # age 18 / aged 18 / age: 18
        r"(\d{1,3})\s*(?:years?\s*old)",                 # 18 years old
        r"(\d{1,3})\s*yr?s?\b",                          # 28yrs / 28yr / 28 yrs
        r"\bi'?m\s+(\d{1,3})\b",                         # I'm 18
        r"\bim\s+(\d{1,3})\b",                           # Im 18
        r"\bi\s+am\s+(\d{1,3})\b",                       # I am 18
        r"(\d{1,3})\s+years?\b",                         # 18 years
        r"\b(\d{1,3})\s*yo\b",                           # 18yo
    ]
    for pat in patterns:
        m = re.search(pat, t)
        if m:
            val = int(m.group(1))
            if 5 <= val <= 100:
                return str(val)
    # Last-resort: first 1-2 digit number not inside a phone number
    stripped = re.sub(r"\b\d{7,}\b", "", t)
    for n in re.findall(r"\b(\d{1,3})\b", stripped):
        if 5 <= int(n) <= 100:
            return n
    return "unknown"


def _extract_city(raw: str) -> str:
    """
    Priority order:
      1. 'from <city>'
      2. 'city <city>' / 'location <city>' / 'located in <city>'
      3. 'in <city>' / 'at <city>'
      4. Known keyword anywhere in text (longest match first)
      5. Freeform unknown city after location keywords
    """
    t = raw.lower()

    # 1. "from <city>"
    m = re.search(r"\bfrom\s+([a-z][a-z\s]{2,20}?)(?=\s+(?:age|aged|\d|phone|number|mob|my|$)|\s*[,.]|$)", t)
    if m:
        w = m.group(1).strip()
        if w in CITY_MAP:
            return CITY_MAP[w]
        if w not in NAME_IGNORE and len(w) >= 3:
            return w.title()

    # 2. Explicit city label: "city amravati", "location pune", "located in X"
    m = re.search(r"\b(?:city|location|place|located\s+in|residing\s+in|staying\s+in|living\s+in)\s+([a-z]{3,20})\b", t)
    if m:
        w = m.group(1).strip()
        if w in CITY_MAP:
            return CITY_MAP[w]
        if w not in NAME_IGNORE and len(w) >= 3:
            return w.title()

    # 3. Known keyword scan (longest first)
    for kw in sorted(CITY_MAP, key=len, reverse=True):
        if re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", t):
            return CITY_MAP[kw]

    # 4. "in <word>" / "at <word>"
    m = re.search(r"\b(?:in|at)\s+([a-z]{3,20})\b", t)
    if m:
        w = m.group(1)
        if w not in NAME_IGNORE:
            return CITY_MAP.get(w, w.title())

    return "unknown"


def _extract_name(raw: str) -> str:
    """
    Priority order:
      1. Explicit labels: 'my name is X', 'name is X', 'i am X', 'i'm X', etc.
      2. 'myself X'
      3. '<word> here' / '<word> this side'
      4. After dash/colon separator: 'details - meena 24'
      5. First capitalised word not in ignore/city lists
      6. First meaningful lowercase word
    """
    t = raw.strip()

    label_patterns = [
        r"(?:my\s+)?name\s+is\s+([a-zA-Z]+)",
        r"\bi\s+am\s+([a-zA-Z]+)",
        r"\bi'?m\s+([a-zA-Z]+)",
        r"\bim\s+([a-zA-Z]+)",
        r"\bthis\s+is\s+([a-zA-Z]+)",
        r"\bcall\s+me\s+([a-zA-Z]+)",
        r"\bmyself\s+([a-zA-Z]+)",          # "myself karthik"
        r"\bits\s+([a-zA-Z]+)",             # "its zubair"
        r"\bit'?s\s+([a-zA-Z]+)",           # "it's meera"
    ]
    for pat in label_patterns:
        m = re.search(pat, t, re.IGNORECASE)
        if m:
            w = m.group(1).strip()
            if w.lower() not in NAME_IGNORE and len(w) >= 2:
                return w.title()

    # "rahul here" / "sana this side"
    m = re.search(r"\b([a-zA-Z]{2,20})\s+(?:here|this\s+side)\b", t, re.IGNORECASE)
    if m and m.group(1).lower() not in NAME_IGNORE:
        return m.group(1).title()

    # After dash or colon separator: "contact details - meena 24"
    m = re.search(r"[-–:]\s*([a-zA-Z]{2,20})\b", t)
    if m:
        w = m.group(1).strip()
        if w.lower() not in NAME_IGNORE and w.lower() not in CITY_MAP:
            return w.title()

    # First capitalised word that isn't a city or noise
    known_cities = set(CITY_MAP.values())
    for w in re.findall(r"\b([A-Z][a-z]{1,20})\b", t):
        if w.lower() not in NAME_IGNORE and w not in known_cities:
            return w

    # First meaningful lowercase word
    for w in re.findall(r"\b([a-zA-Z]{2,20})\b", t):
        if w.lower() not in NAME_IGNORE and w.lower() not in CITY_MAP:
            return w.title()

    return "unknown"


# =============================================================================
# Main predict — Stage 1 → Stage 2
# =============================================================================
def predict(text: str) -> dict:
    raw = text.strip()
    if not raw:
        return {"name": "unknown", "age": "unknown", "city": "unknown", "phone": "unknown"}

    # Stage 1: CSV
    result = _try_csv(raw)
    if result:
        return result

    # Stage 2: NLP
    return {
        "name":  _extract_name(raw),
        "age":   _extract_age(raw),
        "city":  _extract_city(raw),
        "phone": _extract_phone(raw),
    }


# =============================================================================
# Gradio UI
# =============================================================================
EXAMPLES = [
    ["varun, 18, ballari, 7649620937"],
    ["i am varun age 18 from bangalore my number 9079874576"],
    ["myself karthik 27 years old living in noida 9123456780"],
    ["this is roshni from bhopal aged 19 number 8765432100"],
    ["hello my name is ayesha i am 23 staying in surat call 7890123456"],
    ["bro its zubair here age 31 location patna mob 9345678901"],
    ["anjali 26 pune 9988001122"],
    ["my name is tariq age 33 city amravati phone 8800112233"],
    ["name ravi 35 delhi +91 9810001234"],
    ["pooja 22yrs from jaipur 9765001234"],
]

with gr.Blocks(title="AI Form Data Extractor") as demo:

    gr.Markdown("# 📋 AI Form Data Extractor")
    gr.Markdown(
        "Extracts **name · age · city · phone** from any messy input — "
        "comma format or natural language, any name, any city, any phrasing."
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 💡 Problem")
            gr.Markdown("Users send unstructured text instead of filling proper forms.")
        with gr.Column():
            gr.Markdown("### 🚀 Solution")
            gr.Markdown("Rule-based parser handles comma format **and** free-form sentences.")

    gr.Markdown("---")

    with gr.Row():
        with gr.Column(scale=2):
            input_box = gr.Textbox(
                label="Enter your text",
                placeholder=(
                    "Comma format:   varun, 18, ballari, 7649620937\n"
                    "Natural text:   i am varun age 18 from bangalore my number 9079874576\n"
                    "Casual:         myself karthik 27 noida 9123456780"
                ),
                lines=4,
            )
            with gr.Row():
                submit_btn = gr.Button("🔍 Extract", variant="primary")
                clear_btn  = gr.Button("🗑️ Clear")

        with gr.Column(scale=2):
            output_json = gr.JSON(label="Extracted Fields")

    gr.Markdown("#### 💡 Click an example to try it")
    gr.Examples(
        examples=EXAMPLES,
        inputs=input_box,
        label=None,
    )

    submit_btn.click(fn=predict, inputs=input_box, outputs=output_json)
    input_box.submit(fn=predict, inputs=input_box, outputs=output_json)
    clear_btn.click(fn=lambda: ("", None), inputs=[], outputs=[input_box, output_json])

if __name__ == "__main__":
    demo.launch()