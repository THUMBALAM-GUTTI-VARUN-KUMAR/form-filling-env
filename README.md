---
title: Form Filling Env
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
app_file: app.py
pinned: false
---

# 📋 AI Form Data Extractor


> Extract structured contact data from messy, unstructured user text — instantly, with zero APIs or LLMs.

---

## Problem

Users rarely fill forms neatly. They send contact details as casual messages — full of slang, abbreviations, Hinglish, random field order, and missing information:

> *"hey bro its rahul blr side 25 yrs call me 9876543210"*

Traditional form validation rejects this. Manual parsing is slow and error-prone. This project solves it automatically.

---

## Solution

A deterministic, rule-based extraction engine parses free-form text and outputs four clean structured fields:

| Field | Description |
|---|---|
| `name` | Full person name (Title Case) |
| `age` | Numeric age as a string |
| `city` | Canonical city name (e.g. `blr` → `Bangalore`) |
| `phone` | 10-digit mobile number |

If a field cannot be found, it returns `"unknown"`.

---

## Features

- ✅ Handles messy, casual, and noisy text
- ✅ Works with slang, Hinglish, and abbreviations (`blr`, `hyd`, `mum`, `del`)
- ✅ Handles informal and repeated name patterns
- ✅ Extract valid 10-digit phone numbers from noisy input
- ✅ Rule-based and deterministic — same input always gives same output
- ✅ Fast and lightweight — no internet, no GPU, no API keys
- ✅ Interactive Gradio UI included

---

## Demo

### Run the Gradio app

```bash
pip install gradio
python run app.py
```

### Run inference script (hackathon format)

```bash
python inference.py
# or with difficulty:
TASK=hard python inference.py
```

### Run with Docker

```bash
docker build -t form-filling-openenv .
docker run --rm form-filling-openenv
```

---

## Example

**Input**
```
hey bro rahul here blr 25 call me 9876543210
```

**Output**
```json
{
  "name": "Rahul",
  "age": "25",
  "city": "Bangalore",
  "phone": "9876543210"
}
```

**Harder input**
```
yo sign me up!! its priyanka... priyanka joshi okk. around 23-24 ish.
somewhere in blr ig. ping me on 98 7654 3210
```

**Output**
```json
{
  "name": "Priyanka Joshi",
  "age": "23",
  "city": "Bangalore",
  "phone": "9876543210"
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| UI | Gradio |
| Extraction | Regex + rule-based logic |
| Environment | OpenEnv-style (`env.py`) |
| Containerisation | Docker |

---

## Project Structure

```
form_filling_openenv/
├── app.py            # Gradio UI
├── agent.py          # RuleBasedAgent — core extraction logic
├── env.py            # FormEnv — reset(), step(), reward scoring
├── inference.py      # Hackathon runner — [START][STEP]x5[END]
├── dataset.json      # 50 labelled examples (easy / medium / hard)
├── openenv.yaml      # OpenEnv config
├── requirements.txt  # gradio
├── Dockerfile
└── README.md
```

---

## Evaluation

The `FormEnv` environment scores predictions field-by-field:

| Outcome | Score |
|---|---|
| Exact match | 1.0 |
| Partial match (alias / substring / age ±1) | 0.5 |
| Wrong or missing | 0.0 |

**Episode reward = mean(field scores) → range [0.0, 1.0]**

Achieves high accuracy across benchmark dataset examples.

---

## Note

> **No external APIs or LLMs are used.** This system is fully self-contained and runs offline. All extraction is performed by hand-crafted regex patterns and keyword matching.


---

## 🚀 Future Improvements

- Multi-entity extraction (handling multiple users in a single input)
- Context-aware disambiguation (e.g., multiple cities or phone numbers)
- Integration with chatbot or form automation systems
- Hybrid rule + ML approach for improved flexibility