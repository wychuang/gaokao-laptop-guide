from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import xlrd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = [PROJECT_ROOT / "data", PROJECT_ROOT.parent]
OUTPUT = PROJECT_ROOT / "data" / "laptops.json"
PRICE_OVERRIDES = PROJECT_ROOT / "data" / "price-overrides.json"


SHEET_CONFIGS = [
    {
        "sheet": "甜品砖头",
        "category": "甜品砖头",
        "stop_before_row": 166,
        "cols": {
            "brand": 1,
            "model": 4,
            "screenSize": 9,
            "thicknessMm": 11,
            "weightKg": 13,
            "screenScore": 15,
            "pros": 17,
            "neutral": 26,
            "cons": 34,
            "display": 44,
            "cpu": 49,
            "gpu": 53,
            "memory": 57,
            "storage": 62,
            "link": 68,
        },
    },
    {
        "sheet": "高端砖头",
        "category": "高端砖头",
        "stop_before_row": None,
        "cols": {
            "brand": 1,
            "model": 4,
            "screenSize": 9,
            "thicknessMm": 11,
            "weightKg": 13,
            "screenScore": 15,
            "pros": 17,
            "neutral": 26,
            "cons": 34,
            "display": 43,
            "cpu": 48,
            "gpu": 52,
            "memory": 56,
            "storage": 61,
            "link": 67,
        },
    },
]


IMAGE_PROFILES = [
    {
        "match": ["猎刃sultra"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/288431/20/23702/125524/689a9f52Fbbc0212e/310b06b3bf3f2b8e.jpg",
        "source": "https://www.ithome.com/0/874/865.htm",
    },
    {
        "match": ["猎刃s"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/277981/9/25700/65490/6806f69dFca5d5c1b/42f0348ffd7f7ed0.jpg",
        "source": "https://www.ithome.com/0/848/111.htm",
    },
    {
        "match": ["曙光16s", "酷睿ultra"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/7/5b73006f-00cb-4088-b164-ff51dc3f6fb8.jpg?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/867/567.htm",
    },
    {
        "all": [],
        "any": ["曙光16s", "曙光16pro"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/5/2893c352-6c09-4df7-adb9-759f42b47bc7.png?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/852/512.htm",
    },
    {
        "match": ["蛟龙16pro"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/274105/14/28604/156713/6811c736F777ce622/6e54de4a5dee06ba.jpg",
        "source": "https://www.ithome.com/0/850/695.htm",
    },
    {
        "match": ["苍龙16xpro"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/294059/16/638/220628/6810a1a7Fb71fdf24/348754b26d7d468b.jpg",
        "source": "https://www.ithome.com/0/851/196.htm",
    },
    {
        "match": ["苍龙16ultra"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/6/926ed2ef-fcde-45da-8aff-c24b4356f169.jpg?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/860/287.htm",
    },
    {
        "match": ["极光xpro"],
        "image": "https://img13.360buyimg.com/n1/jfs/t1/280080/20/18129/124943/67f8b86eF219d0cf3/5d47d2c59099a37f.jpg",
        "source": "https://www.ithome.com/0/846/359.htm",
    },
    {
        "match": ["耀世16ultra"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/284794/10/24323/167423/68074064Fe45c1750/8d2ec330d33c8ce7.jpg",
        "source": "https://www.ithome.com/0/848/113.htm",
    },
    {
        "match": ["橘宝", "r16pro"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/345523/35/23452/96538/690c7c92Fdeb2875d/9e8e0d0c2ae63ff2.jpg",
        "source": "https://www.ithome.com/0/895/874.htm",
    },
    {
        "match": ["泰坦18pro"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/5/5c123d78-deda-4f48-92d4-8879f6464d03.jpg?x-bce-process=image/format,f_auto",
        "source": "https://m.ithome.com/html/854294.htm",
    },
    {
        "match": ["雷影18"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/285063/8/6335/245356/67dd36c3F51bdfa17/dd2c457f206979e1.jpg",
        "source": "https://www.ithome.com/0/839/960.htm",
    },
    {
        "match": ["泰坦16"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/282828/40/13238/274142/67ebb20bFc67aee05/5818b471e6e610c6.jpg",
        "source": "https://www.ithome.com/0/843/239.htm",
    },
    {
        "match": ["魔霸"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/6/67abbc67-e2f1-45bf-a798-a372b0e09054.jpg?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/860/648.htm",
    },
    {
        "match": ["枪神"],
        "image": "https://img14.360buyimg.com/pop/jfs/t1/255607/19/25478/181817/67bdbf36F6d77e244/9c502c1d62fa044a.jpg",
        "source": "https://www.ithome.com/0/833/605.htm",
    },
    {
        "all": [],
        "any": ["暗影精灵", "hyperx"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/1/13c57153-4de7-4d7d-ab07-4983a44db302.png?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/822/973.htm",
    },
    {
        "match": ["r9000p"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/9/1bd114f0-cd34-4124-be8f-ce05ca864059.jpg?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/882/833.htm",
    },
    {
        "all": [],
        "any": ["y9000p", "legion9"],
        "image": "https://img.ithome.com/newsuploadfiles/2025/5/1bada262-4ca7-40cd-8b13-566ff1202e4c.jpg?x-bce-process=image/format,f_auto",
        "source": "https://www.ithome.com/0/853/464.htm",
    },
    {
        "match": ["winh9"],
        "image": "https://img.ithome.com/newsuploadfiles/2026/4/57dfb384-799c-4aa9-9d97-49910a020316.png?x-bce-process=image/format,f_auto",
        "source": "https://m.ithome.com/html/942541.htm",
    },
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n+", "/", text)
    return text.strip(" /")


def numeric(value: Any) -> float | None:
    if value in ("", None):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else None


def compact(text: str) -> str:
    return re.sub(r"[\s/（）()]+", "", text).lower()


def split_notes(text: str) -> list[str]:
    if not text:
        return []
    parts = [part.strip() for part in re.split(r"[/\n]+", text) if part.strip()]
    return parts[:8]


def image_for(brand: str, model: str) -> dict[str, str]:
    target = compact(f"{brand}{model}")
    for profile in IMAGE_PROFILES:
        required = profile.get("all", profile.get("match", []))
        optional = profile.get("any", [])
        if all(token.lower() in target for token in required) and (
            not optional or any(token.lower() in target for token in optional)
        ):
            return {
                "image": profile["image"],
                "imageSource": profile["source"],
            }
    return {
        "image": "",
        "imageSource": "",
    }


def normalize_gpu(gpu: str) -> str:
    text = gpu.replace(" ", "")
    match = re.search(r"RTX/?\s*(50[789]0(?:Ti)?)", text, re.I)
    if match:
        return "RTX " + match.group(1).replace("Ti", " Ti")
    return clean(gpu)


def load_price_overrides() -> dict[str, Any]:
    if not PRICE_OVERRIDES.exists():
        return {}
    return json.loads(PRICE_OVERRIDES.read_text(encoding="utf-8"))


def price_override_for(overrides: dict[str, Any], item_id: str, brand: str, model: str) -> dict[str, Any]:
    if item_id in overrides:
        return overrides[item_id]
    model_key = compact(f"{brand}{model}")
    for key, value in overrides.items():
        if compact(key) == model_key:
            return value
    return {}


def parse_sheet(book: xlrd.Book, config: dict[str, Any], price_overrides: dict[str, Any]) -> list[dict[str, Any]]:
    sheet = book.sheet_by_name(config["sheet"])
    stop_before = config["stop_before_row"]
    cols = config["cols"]
    items: list[dict[str, Any]] = []
    carry: dict[str, Any] = {}
    section: dict[str, Any] | None = None
    price_re = re.compile(r"(\d+)k\s*~\s*(\d+)k价位")

    max_row = min(sheet.nrows, stop_before - 1) if stop_before else sheet.nrows
    for row in range(max_row):
        row_text = " ".join(clean(sheet.cell_value(row, col)) for col in range(min(sheet.ncols, 12)))
        price_match = price_re.search(row_text)
        if price_match:
            low = int(price_match.group(1))
            high = int(price_match.group(2))
            section = {
                "priceLabel": f"{low}-{high}k",
                "priceMinK": low,
                "priceMaxK": high,
                "priceMidK": round((low + high) / 2, 1),
            }
            carry = {}
            continue
        if section is None:
            continue

        raw_model = clean(sheet.cell_value(row, cols["model"]))
        if not raw_model:
            continue
        if any(marker in raw_model for marker in ["型号", "为什么", "注："]):
            continue

        row_data: dict[str, Any] = {}
        for key, col in cols.items():
            value = clean(sheet.cell_value(row, col))
            if value:
                carry[key] = value
            row_data[key] = value or carry.get(key, "")

        brand = row_data["brand"]
        model = row_data["model"]
        if not brand or not model or brand in ["品牌"]:
            continue

        screen_size = numeric(row_data["screenSize"])
        thickness = numeric(row_data["thicknessMm"])
        weight = numeric(row_data["weightKg"])
        image_data = image_for(brand, model)
        item_id = f"{config['category']}-{len(items) + 1:02d}-{row + 1}"
        override = price_override_for(price_overrides, item_id, brand, model)
        exact_price = numeric(override.get("priceCny")) if override else None
        price_mid_cny = int(section["priceMidK"] * 1000)
        price_point_k = round((exact_price or price_mid_cny) / 1000, 2)

        # Price basis mapping from override confidence
        confidence = override.get("confidence", "") if override else ""
        if exact_price:
            if confidence == "high":
                price_basis = "jd_live"
            elif confidence == "medium":
                price_basis = "published"
            else:
                price_basis = "manual"
            price_display = f"¥{int(exact_price):,}"
        else:
            price_basis = "guide_range_midpoint"
            price_display = f"约 ¥{price_mid_cny:,}"

        # Price source info
        price_source = None
        if override.get("sourceName"):
            price_source = {
                "name": override.get("sourceName", ""),
                "url": override.get("sourceUrl", ""),
                "confidence": confidence or "low",
                "method": override.get("method", ""),
            }

        # Configs from override (JD variants)
        configs = override.get("configs") if override else None

        item = {
            "id": item_id,
            "category": config["category"],
            "brand": brand,
            "model": model,
            "priceLabel": section["priceLabel"],
            "priceMinK": section["priceMinK"],
            "priceMaxK": section["priceMaxK"],
            "priceMidK": section["priceMidK"],
            "priceRangeCny": [section["priceMinK"] * 1000, section["priceMaxK"] * 1000],
            "priceCny": int(exact_price) if exact_price else None,
            "estimatedPriceCny": price_mid_cny,
            "pricePointK": price_point_k,
            "priceDisplay": price_display,
            "priceBasis": price_basis,
            "priceSource": price_source,
            "priceNote": override.get("note", "") if override else "源表格仅提供价位段；这里用区间中值定位。",
            "configs": configs,
            "screenSize": screen_size,
            "thicknessMm": thickness,
            "weightKg": weight,
            "screenScore": row_data["screenScore"],
            "display": row_data["display"],
            "cpu": row_data["cpu"],
            "gpu": normalize_gpu(row_data["gpu"]),
            "memory": row_data["memory"],
            "storage": row_data["storage"],
            "pros": split_notes(row_data["pros"]),
            "neutral": split_notes(row_data["neutral"]),
            "cons": split_notes(row_data["cons"]),
            "guideLink": row_data["link"],
            "sourceSheet": config["sheet"],
            "sourceRow": row + 1,
            **image_data,
        }
        items.append(item)
    return items


def source_file() -> Path:
    for directory in SOURCE_DIRS:
        matches = sorted(directory.glob("*.et"))
        if matches:
            return matches[0]
    searched = ", ".join(str(path) for path in SOURCE_DIRS)
    raise FileNotFoundError(f"No .et source found in {searched}")


def main() -> None:
    source = source_file()
    book = xlrd.open_workbook(str(source), formatting_info=True)
    price_overrides = load_price_overrides()
    items: list[dict[str, Any]] = []
    for config in SHEET_CONFIGS:
        items.extend(parse_sheet(book, config, price_overrides))

    data = {
        "title": "高考后游戏本选购可视化",
        "updatedAt": "2026-05-14",
        "guideUpdatedAt": "2026-05-08",
        "currency": "CNY",
        "priceNote": "价位来自源指南价位段，未计算平台神券、国补、地区仓和临时促销。",
        "sourceWorkbook": source.name,
        "items": items,
        "sources": sorted(
            {
                item["imageSource"]
                for item in items
                if item.get("imageSource")
            }
        ),
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} items to {OUTPUT}")


if __name__ == "__main__":
    main()
