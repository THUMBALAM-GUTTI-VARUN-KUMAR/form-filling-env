import re

CITY_MAP = {
    "blr": "Bangalore",
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "hyd": "Hyderabad",
    "hyderabad": "Hyderabad",
    "delhi": "Delhi",
    "mumbai": "Mumbai",
    "mum": "Mumbai",
    "pune": "Pune",
    "jaipur": "Jaipur",
    "patna": "Patna",
    "bhopal": "Bhopal",
    "surat": "Surat",
    "amravati": "Amravati",
    "noida": "Noida"
}


class RuleBasedAgent:

    def predict(self, observation):

        text = observation["observation"].lower()

        result = {
            "name": "unknown",
            "age": "unknown",
            "city": "unknown",
            "phone": "unknown"
        }

        # -------- COMMA FORMAT --------
        if "," in text:
            parts = [x.strip() for x in text.split(",")]

            if len(parts) >= 4:
                result["name"] = parts[0].title()
                result["age"] = re.sub(r"\D", "", parts[1])

                city_raw = parts[2].lower()
                result["city"] = CITY_MAP.get(city_raw, city_raw.title())

                phone = re.sub(r"\D", "", parts[3])
                if len(phone) >= 10:
                    result["phone"] = phone[-10:]

                return result

        # -------- PHONE --------
        phone_match = re.search(r"\d{10,13}", text)
        if phone_match:
            result["phone"] = phone_match.group()[-10:]

        # -------- AGE --------
        age_match = re.search(r"\b(\d{1,2})\b", text)
        if age_match:
            result["age"] = age_match.group(1)

        # -------- CITY --------
        for key in CITY_MAP:
            if key in text:
                result["city"] = CITY_MAP[key]
                break

        # -------- NAME --------
        words = text.split()

        ignore_words = {
            "i", "am", "my", "name", "is", "age", "from",
            "city", "phone", "number", "years", "old",
            "living", "in", "call", "me"
        }

        name_words = []

        for word in words:
            clean = re.sub(r'[^a-z]', '', word)

            if clean and clean not in ignore_words and clean not in CITY_MAP:
                if not clean.isdigit():
                    name_words.append(clean)

            if len(name_words) == 2:
                break

        if name_words:
            result["name"] = " ".join(name_words).title()

        return result
