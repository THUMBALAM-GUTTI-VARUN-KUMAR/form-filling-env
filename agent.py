import re


CITY_MAP = {
    "blr": "Bangalore",
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "hyd": "Hyderabad",
    "mum": "Mumbai",
    "delhi": "Delhi",
    "chennai": "Chennai"
}


class RuleBasedAgent:

    def predict(self, text):

    # Handle comma-separated quick format
    parts = [x.strip() for x in text.split(",")]

    if len(parts) == 4:
        return {
            "name": parts[0].title(),
            "age": parts[1],
            "city": parts[2].title(),
            "phone": parts[3]
        }

    # Default regex extraction
    return {
        "name": self.extract_name(text),
        "age": self.extract_age(text),
        "city": self.extract_city(text),
        "phone": self.extract_phone(text)
    }


    # ---------------- NAME ----------------
    def extract_name(self, text):

        patterns = [
            r"my name is ([A-Za-z]+(?:\s[A-Za-z]+){0,2})",
            r"i am ([A-Za-z]+(?:\s[A-Za-z]+){0,2})",
            r"i'm ([A-Za-z]+(?:\s[A-Za-z]+){0,2})",
            r"its ([A-Za-z]+(?:\s[A-Za-z]+){0,2})"
        ]

        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1).title()

        return "unknown"

    # ---------------- AGE ----------------
    def extract_age(self, text):

        patterns = [
            r"age is (\d{1,2})",
            r"age[: ](\d{1,2})",
            r"(\d{1,2}) years old",
            r"i am (\d{1,2})"
        ]

        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return "unknown"

    # ---------------- CITY ----------------
    def extract_city(self, text):

        t = text.lower()

        for key, value in CITY_MAP.items():
            if key in t:
                return value

        patterns = [
            r"from ([A-Za-z]+)",
            r"in ([A-Za-z]+)",
            r"based in ([A-Za-z]+)",
            r"live in ([A-Za-z]+)"
        ]

        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1).title()

        return "unknown"

    # ---------------- PHONE ----------------
    def extract_phone(self, text):

        match = re.search(r"\b[6-9]\d{9}\b", text)

        if match:
            return match.group()

        return "unknown"


# For app.py import compatibility
def extract(text):
    agent = RuleBasedAgent()
    return agent.predict(text)