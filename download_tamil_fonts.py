#!/usr/bin/env python3
"""
Tamil Fonts Downloader & Categorizer
Downloads and categorizes Tamil fonts across ALL encodings AND font styles (Bold, Italic, BoldItalic, Regular, Light, etc.)
"""

import os
import sys
import shutil
import hashlib
import zipfile
import tarfile
import struct
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
TEMP_CLONE_DIR = BASE_DIR / "tmp_repos"
COLLECTION_DIR = BASE_DIR / "fonts"

ENCODING_CATEGORIES = {
    "Unicode": [
        "unicode", "lohit", "noto", "catamaran", "baloo", "mukta", "hind", "meera", 
        "kavivanar", "coimbatore", "tiro", "latha", "vijaya", "parambikulam", "tsanti", 
        "tsu", "uni", "postnobills", "yaldevi", "agastya", "idhmavaha", "lopamudra", "kavithai"
    ],
    "TACE_TAU_Chemmozhi": [
        "tau-", "tau_", "tace", "chemmozhi"
    ],
    "TSCII": [
        "tsc", "tscii", "tscu", "paranar", "avarangal", "mylai"
    ],
    "TAB_TAM": [
        "tab", "tam_", "_tam", "tamkalyan", "tam-", "dhalapathy", "bilingual", "monolingual", "tamil", "tam"
    ],
    "Bamini": [
        "bamini", "baamini", "bamin"
    ],
    "Senthamizh_Sundaram": [
        "senthamizh", "sen_", "sundaram", "st-0", "st_0"
    ],
    "Vanavil_NLCI": [
        "vanavil", "avviyar", "auvai", "auva", "thiruvalluvar", "thir", "vaigai", "vaig"
    ],
    "Modular_SHREE_TMOT": [
        "shree", "tmot", "modular", "sm-"
    ],
    "Chenet": [
        "chenet"
    ],
    "ATM_Azhagi_Anjal": [
        "atm ", "atm_", "atm-", "anjal", "murasu", "inaimathi"
    ],
    "Softview_Agaram_Dinakaran": [
        "softview", "agaram", "dinakaran", "vivegam", "kani", "inia", "webtamil", "web-tamil"
    ],
}

STYLES = ["BoldItalic", "Bold", "Italic", "Light", "Medium_SemiBold", "Regular"]

REPOS_TO_CLONE = [
    ("thamizha/tamil-fonts", "https://github.com/thamizha/tamil-fonts.git"),
    ("eegarai/Tamilfonts", "https://github.com/eegarai/Tamilfonts.git"),
    ("eegarai/tamil-unicode-fonts", "https://github.com/eegarai/tamil-unicode-fonts.git"),
    ("ThaniThamizhAkarathiKalanjiyam/tamilfonts", "https://github.com/ThaniThamizhAkarathiKalanjiyam/tamilfonts.git"),
    ("linuxkathirvel/tamil-unicode-fonts", "https://github.com/linuxkathirvel/tamil-unicode-fonts.git"),
    ("lecramyajiv/fonts-tamil-tva", "https://github.com/lecramyajiv/fonts-tamil-tva.git"),
    ("lecramyajiv/fonts-tamil-nonlibre", "https://github.com/lecramyajiv/fonts-tamil-nonlibre.git"),
    ("chenet0005/fonts", "https://github.com/chenet0005/fonts.git"),
    ("sricreativecards-ops/tamil-fonts", "https://github.com/sricreativecards-ops/tamil-fonts.git"),
    ("ramasamy-duraipandy/tamil-unicode-fonts", "https://github.com/ramasamy-duraipandy/tamil-unicode-fonts.git"),
    ("dhalapathy/tam-fonts", "https://github.com/dhalapathy/tam-fonts.git"),
    ("KaniyamFoundation/Fonts", "https://github.com/KaniyamFoundation/Fonts.git"),
    ("nlci/taml-font-thiruvalluvar", "https://github.com/nlci/taml-font-thiruvalluvar.git"),
    ("mayooresan/Android-TamilUtil", "https://github.com/mayooresan/Android-TamilUtil.git"),
    ("virtualvinodh/agastya-tamil-extended", "https://github.com/virtualvinodh/agastya-tamil-extended.git"),
]

DIRECT_URLS = [
    ("BalooThambi2-Regular", "https://raw.githubusercontent.com/google/fonts/main/ofl/baloothambi2/BalooThambi2%5Bwght%5D.ttf"),
    ("Catamaran-Regular", "https://raw.githubusercontent.com/google/fonts/main/ofl/catamaran/Catamaran%5Bwght%5D.ttf"),
    ("MuktaMalar-Regular", "https://raw.githubusercontent.com/google/fonts/main/ofl/muktamalar/MuktaMalar-Regular.ttf"),
    ("HindMadurai-Regular", "https://raw.githubusercontent.com/google/fonts/main/ofl/hindmadurai/HindMadurai-Regular.ttf"),
    ("Kavivanar-Regular", "https://raw.githubusercontent.com/google/fonts/main/ofl/kavivanar/Kavivanar-Regular.ttf"),
    ("MeeraInimai-Regular", "https://raw.githubusercontent.com/google/fonts/main/ofl/meerainimai/MeeraInimai-Regular.ttf"),
]

def log(msg):
    print(msg, flush=True)

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def detect_category(filename):
    fname_lower = filename.lower()
    for category, keywords in ENCODING_CATEGORIES.items():
        for kw in keywords:
            if kw in fname_lower:
                return category
    return "Other_Legacy"

def parse_header_style(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read(1024)
            if len(data) < 12:
                return None
            num_tables = struct.unpack('>H', data[4:6])[0]
            offset = 12
            head_offset = None
            for _ in range(num_tables):
                if offset + 16 > len(data):
                    break
                tag = data[offset:offset+4]
                t_offset = struct.unpack('>I', data[offset+8:offset+12])[0]
                if tag == b'head':
                    head_offset = t_offset
                    break
                offset += 16
            
            if head_offset is not None:
                f.seek(head_offset + 44)
                mac_style_bytes = f.read(2)
                if len(mac_style_bytes) == 2:
                    mac_style = struct.unpack('>H', mac_style_bytes)[0]
                    is_bold = bool(mac_style & 1)
                    is_italic = bool(mac_style & 2)
                    if is_bold and is_italic:
                        return 'BoldItalic'
                    elif is_bold:
                        return 'Bold'
                    elif is_italic:
                        return 'Italic'
    except Exception:
        pass
    return None

def detect_style(filepath):
    fname = filepath.name.lower()
    
    # Check filename patterns first
    if any(k in fname for k in ['bolditalic', 'bold_italic', 'bold-italic', 'bi.ttf', 'bi.otf', 'bdit', 'bold italic']):
        return 'BoldItalic'
    
    # Header check as secondary signal
    hdr_style = parse_header_style(filepath)
    if hdr_style == 'BoldItalic':
        return 'BoldItalic'
    
    if any(k in fname for k in ['italic', 'oblique']) or fname.endswith('-i.ttf') or fname.endswith('_i.ttf') or fname.endswith('i.ttf') or fname.endswith('i.otf'):
        return 'Italic'
    if hdr_style == 'Italic':
        return 'Italic'

    if any(k in fname for k in ['bold']) or fname.endswith('-b.ttf') or fname.endswith('_b.ttf') or fname.endswith('bd.ttf') or fname.endswith('b.ttf') or fname.endswith('b.otf'):
        return 'Bold'
    if hdr_style == 'Bold':
        return 'Bold'

    if any(k in fname for k in ['light', 'thin', 'extralight']):
        return 'Light'
    if any(k in fname for k in ['medium', 'semibold', 'extrabold', 'black', 'heavy']):
        return 'Medium_SemiBold'

    return 'Regular'

def extract_archives(target_dir):
    log("Extracting archive files (zip, tar, gz)...")
    for root, _, files in os.walk(target_dir):
        for f in files:
            file_path = Path(root) / f
            if f.endswith(".zip"):
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(file_path.parent)
                    log(f"Extracted zip: {f}")
                except Exception as e:
                    log(f"Failed to extract zip {f}: {e}")
            elif f.endswith(".tar.gz") or f.endswith(".tgz"):
                try:
                    with tarfile.open(file_path, 'r:gz') as tar_ref:
                        tar_ref.extractall(file_path.parent)
                    log(f"Extracted tar.gz: {f}")
                except Exception as e:
                    log(f"Failed to extract tar.gz {f}: {e}")

def clone_repositories():
    TEMP_CLONE_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in REPOS_TO_CLONE:
        repo_dir = TEMP_CLONE_DIR / name.replace("/", "_")
        if repo_dir.exists():
            log(f"Skipping {name}, already cloned.")
            continue
        log(f"Cloning {name} from {url}...")
        try:
            subprocess.run(["git", "clone", "--depth", "1", url, str(repo_dir)], check=True)
        except Exception as e:
            log(f"Error cloning {name}: {e}")

def download_direct_urls():
    direct_dir = TEMP_CLONE_DIR / "direct_downloads"
    direct_dir.mkdir(parents=True, exist_ok=True)
    for name, url in DIRECT_URLS:
        dest = direct_dir / f"{name}.ttf"
        if not dest.exists():
            log(f"Downloading direct URL: {name}...")
            try:
                urllib.request.urlretrieve(url, dest)
            except Exception as e:
                log(f"Failed to download {name}: {e}")

def organize_fonts():
    if COLLECTION_DIR.exists():
        shutil.rmtree(COLLECTION_DIR)

    categories = list(ENCODING_CATEGORIES.keys()) + ["Other_Legacy"]
    for cat in categories:
        for st in STYLES:
            (COLLECTION_DIR / cat / st).mkdir(parents=True, exist_ok=True)

    seen_hashes = set()
    font_count = 0
    cat_counts = {cat: 0 for cat in categories}
    style_counts = {st: 0 for st in STYLES}

    font_inventory = []

    log("\nScanning and categorizing font files across encodings and styles...")
    for root, _, files in os.walk(TEMP_CLONE_DIR):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in [".ttf", ".otf", ".woff", ".woff2"]:
                src_path = Path(root) / f
                try:
                    fhash = hash_file(src_path)
                except Exception as e:
                    log(f"Skipping file {src_path}: {e}")
                    continue

                if fhash in seen_hashes:
                    continue
                seen_hashes.add(fhash)

                category = detect_category(f)
                style = detect_style(src_path)
                
                dest_dir = COLLECTION_DIR / category / style
                dest_path = dest_dir / f

                idx = 1
                orig_stem = dest_path.stem
                while dest_path.exists():
                    dest_path = dest_dir / f"{orig_stem}_{idx}{ext}"
                    idx += 1

                shutil.copy2(src_path, dest_path)
                font_count += 1
                cat_counts[category] += 1
                style_counts[style] += 1
                size_kb = dest_path.stat().st_size / 1024
                
                rel_path = dest_path.relative_to(BASE_DIR)
                font_inventory.append({
                    "name": dest_path.name,
                    "category": category,
                    "style": style,
                    "size_kb": f"{size_kb:.1f} KB",
                    "path": str(rel_path),
                    "hash": fhash[:10]
                })

    log(f"\nCompleted! Total unique fonts collected: {font_count}")
    log("\nBreakdown by Encoding Category:")
    for cat, count in cat_counts.items():
        log(f"  - {cat}: {count} fonts")

    log("\nBreakdown by Font Style / Weight:")
    for st, count in style_counts.items():
        log(f"  - {st}: {count} fonts")

    return font_inventory, cat_counts, style_counts

def write_catalog(font_inventory, cat_counts, style_counts):
    index_md = BASE_DIR / "FONT_INDEX.md"
    content = "# Tamil Fonts Master Catalog\n\n"
    content += "A comprehensive collection of Tamil fonts split by encoding standards and font styles (Regular, Bold, Italic, BoldItalic, Light, Medium).\n\n"
    
    content += "## Summary by Encoding Category\n\n"
    content += "| Encoding Category | Font Count | Description |\n"
    content += "|---|---|---| \n"
    content += f"| **Unicode** | {cat_counts.get('Unicode', 0)} | Modern standard Tamil OpenType/TrueType fonts (Google Fonts, Lohit, Noto, PostNoBills, Yaldevi, Agastya, etc.) |\n"
    content += f"| **TACE / TAU / Chemmozhi** | {cat_counts.get('TACE_TAU_Chemmozhi', 0)} | Tamil Virtual Academy & Govt of Tamil Nadu TACE16/TAU standard fonts |\n"
    content += f"| **TSCII** | {cat_counts.get('TSCII', 0)} | Tamil Script Code for Information Interchange 8-bit standard fonts |\n"
    content += f"| **TAB / TAM** | {cat_counts.get('TAB_TAM', 0)} | Tamil Bilingual (TAB) & Monolingual (TAM) legacy fonts |\n"
    content += f"| **Bamini** | {cat_counts.get('Bamini', 0)} | Classic Bamini typewriter encoding fonts (popular in Sri Lanka & DTP) |\n"
    content += f"| **Senthamizh & Sundaram** | {cat_counts.get('Senthamizh_Sundaram', 0)} | Senthamizh and Sundaram series legacy publishing fonts |\n"
    content += f"| **Vanavil & NLCI** | {cat_counts.get('Vanavil_NLCI', 0)} | Vanavil Avviyar, Vaigai, ThiruValluvar, and NLCI fonts |\n"
    content += f"| **Modular / SHREE / TMOT** | {cat_counts.get('Modular_SHREE_TMOT', 0)} | Modular InfoTech SHREE and TMOT series Tamil fonts |\n"
    content += f"| **Chenet** | {cat_counts.get('Chenet', 0)} | Chenet Tamil legacy font series |\n"
    content += f"| **ATM / Azhagi / Anjal** | {cat_counts.get('ATM_Azhagi_Anjal', 0)} | ATM, Azhagi, Murasu, and Anjal Tamil series fonts |\n"
    content += f"| **Softview / Agaram / Dinakaran** | {cat_counts.get('Softview_Agaram_Dinakaran', 0)} | Softview, Agaram, Dinakaran, Vivegam & DTP series fonts |\n"
    content += f"| **Other Legacy** | {cat_counts.get('Other_Legacy', 0)} | Non-standard legacy & custom DTP fonts |\n\n"

    content += "## Summary by Style & Weight Subfolders\n\n"
    content += "| Style Subfolder | Font Count | Description |\n"
    content += "|---|---|---| \n"
    content += f"| **Regular** | {style_counts.get('Regular', 0)} | Standard regular weight typefaces |\n"
    content += f"| **Bold** | {style_counts.get('Bold', 0)} | Bold weight typefaces |\n"
    content += f"| **Italic** | {style_counts.get('Italic', 0)} | Italic / Oblique slant typefaces |\n"
    content += f"| **BoldItalic** | {style_counts.get('BoldItalic', 0)} | Combined Bold and Italic weight typefaces |\n"
    content += f"| **Light** | {style_counts.get('Light', 0)} | Light / Thin weight typefaces |\n"
    content += f"| **Medium_SemiBold** | {style_counts.get('Medium_SemiBold', 0)} | Medium, SemiBold, ExtraBold, Black weight typefaces |\n\n"

    content += "## Font Inventory List\n\n"
    content += "| Font Filename | Category | Style | Size | Path |\n"
    content += "|---|---|---|---|---|\n"
    for item in sorted(font_inventory, key=lambda x: (x["category"], x["style"], x["name"].lower())):
        content += f"| `{item['name']}` | {item['category']} | `{item['style']}` | {item['size_kb']} | `[{item['path']}](file://{BASE_DIR}/{item['path']})` |\n"

    index_md.write_text(content, encoding="utf-8")
    log(f"Catalog saved to {index_md}")

    readme_md = BASE_DIR / "README.md"
    readme_content = f"""# Comprehensive Tamil Fonts Collection

This repository contains a curated, deduplicated collection of **{len(font_inventory)} Tamil fonts** categorized by encoding standards AND split into **style subfolders** (`Regular/`, `Bold/`, `Italic/`, `BoldItalic/`, `Light/`, `Medium_SemiBold/`).

## Directory Hierarchy & Style Subfolders

```text
fonts/
├── <Encoding_Category>/
│   ├── Regular/
│   ├── Bold/
│   ├── Italic/
│   ├── BoldItalic/
│   ├── Light/
│   └── Medium_SemiBold/
```

### Encoding Categories:

- `fonts/Unicode/`: Modern OpenType / TrueType Unicode fonts (Google Fonts, Lohit, Noto, PostNoBills, Yaldevi, Agastya, etc.)
- `fonts/TACE_TAU_Chemmozhi/`: Tamil Virtual Academy & Govt of Tamil Nadu TACE16 and TAU standard fonts
- `fonts/TSCII/`: Tamil Script Code for Information Interchange 8-bit fonts (TSCu_Paranar, TSC_Avarangal, etc.)
- `fonts/TAB_TAM/`: Tamil Bilingual (TAB) and Monolingual (TAM) fonts
- `fonts/Bamini/`: Classic Bamini typewriter encoding fonts
- `fonts/Senthamizh_Sundaram/`: Senthamizh and Sundaram series DTP fonts
- `fonts/Vanavil_NLCI/`: Vanavil Avviyar, Vaigai, ThiruValluvar, and NLCI fonts
- `fonts/Modular_SHREE_TMOT/`: Modular InfoTech SHREE and TMOT fonts
- `fonts/Chenet/`: Chenet Tamil legacy font series
- `fonts/ATM_Azhagi_Anjal/`: ATM, Azhagi, Murasu, and Anjal Tamil series fonts
- `fonts/Softview_Agaram_Dinakaran/`: Softview, Agaram, Dinakaran, Vivegam & DTP series fonts
- `fonts/Other_Legacy/`: Additional non-Unicode DTP fonts

## Master Catalog

Detailed index of all font files with sizes, styles, and paths: [FONT_INDEX.md](file://""" + str(index_md) + """)
"""
    readme_md.write_text(readme_content, encoding="utf-8")

def main():
    log("=== Starting Tamil Fonts Aggregator ===")
    clone_repositories()
    download_direct_urls()
    extract_archives(TEMP_CLONE_DIR)
    inventory, cat_counts, style_counts = organize_fonts()
    write_catalog(inventory, cat_counts, style_counts)
    log("=== Process Finished Successfully ===")

if __name__ == "__main__":
    main()
