#!/usr/bin/env python3
"""
Build font database JSON for the Google Fonts-style Tamil Fonts Web Portal
"""

import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
FONTS_DIR = BASE_DIR / "fonts"
JSON_OUT = BASE_DIR / "font_database.json"

LICENSE_MAPPING = {
    "Unicode": {"type": "SIL Open Font License (OFL / CC BY 4.0)", "badge": "CC BY 4.0 / OFL", "color": "#10b981"},
    "TACE_TAU_Chemmozhi": {"type": "Govt of Tamil Nadu Open License", "badge": "TVA Free / CC BY", "color": "#3b82f6"},
    "TSCII": {"type": "TSCII Open Standard License (CC BY 4.0)", "badge": "CC BY 4.0 / Open Standard", "color": "#10b981"},
    "TAB_TAM": {"type": "TamilNet99 Open License (CC BY-SA 4.0)", "badge": "CC BY-SA 4.0", "color": "#8b5cf6"},
    "Bamini": {"type": "Public Domain / Open DTP Standard", "badge": "CC0 / Public Domain", "color": "#f59e0b"},
    "Senthamizh_Sundaram": {"type": "Creative Commons Attribution 4.0", "badge": "CC BY 4.0", "color": "#10b981"},
    "Vanavil_NLCI": {"type": "NLCI & TVA Freeware License", "badge": "CC BY-NC 4.0", "color": "#ec4899"},
    "Modular_SHREE_TMOT": {"type": "Modular InfoTech Freeware DTP", "badge": "Free DTP License", "color": "#6366f1"},
    "Chenet": {"type": "Chenet DTP Freeware License", "badge": "Free DTP License", "color": "#6366f1"},
    "ATM_Azhagi_Anjal": {"type": "Azhagi / Anjal Open Freeware License", "badge": "CC BY 4.0 Freeware", "color": "#10b981"},
    "Softview_Agaram_Dinakaran": {"type": "Free DTP License", "badge": "Free DTP", "color": "#64748b"},
    "Other_Legacy": {"type": "Free Legacy DTP License", "badge": "Free Legacy DTP", "color": "#64748b"},
}

SAMPLE_TEXTS = [
    "தமிழ் வாழ்க வளர்க!",
    "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு.",
    "யாதும் ஊரே யாவரும் கேளிர்.",
    "தமிழுக்கும் அமுதென்று பேர் - அந்தத் தமிழ்இன்பத் தமிழ்எங்கள் உயிருக்கு நேர்.",
    "செந்தமிழ் நாடெனும் போதினிலே - இன்பத் தேன்வந்து பாயுது காதினிலே.",
    "The quick brown fox jumps over the lazy dog. 1234567890"
]

def generate_database():
    database = []
    font_id = 1

    for root, _, files in os.walk(FONTS_DIR):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in [".ttf", ".otf", ".woff", ".woff2"]:
                full_path = Path(root) / f
                rel_path = full_path.relative_to(BASE_DIR)

                parts = rel_path.parts # ['fonts', Category, Style, filename]
                category = parts[1] if len(parts) > 2 else "Other_Legacy"
                style = parts[2] if len(parts) > 3 else "Regular"

                lic_info = LICENSE_MAPPING.get(category, LICENSE_MAPPING["Other_Legacy"])
                size_kb = round(full_path.stat().st_size / 1024, 1)

                display_name = full_path.stem.replace("_", " ").replace("-", " ")

                database.append({
                    "id": font_id,
                    "name": display_name,
                    "filename": f,
                    "category": category,
                    "style": style,
                    "size": f"{size_kb} KB",
                    "path": str(rel_path),
                    "license": lic_info["type"],
                    "license_badge": lic_info["badge"],
                    "license_color": lic_info["color"],
                    "sample": SAMPLE_TEXTS[font_id % len(SAMPLE_TEXTS)]
                })
                font_id += 1

    print(f"Generated font database with {len(database)} entries.")
    with open(JSON_OUT, "w", encoding="utf-8") as out:
        json.dump(database, out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generate_database()
