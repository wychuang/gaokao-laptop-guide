"""Price collection for gaokao-laptop-guide.

Uses Playwright to extract SKU/variant data from JD product pages,
combined with a maintained price database (web-search verified market prices).
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
LAPTOPS = ROOT / "data" / "laptops.json"
OUTPUT = ROOT / "data" / "price-overrides.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# ── Price database ─────────────────────────────────────────────
# Updated via web search. Key sources: smzdm, IT之家, pconline, zol, JD.
# Structure: item_id -> { priceCny, configs?, sourceName, sourceUrl, note }
# "configs" lists alternative SKUs with their specs and prices.
PRICE_DATABASE: dict[str, dict[str, Any]] = {
    # ═══ 甜品砖头 ═══
    "甜品砖头-01-41": {
        "priceCny": 7999,
        "sourceName": "京东国补到手价",
        "sourceUrl": "https://www.ithome.com/0/848/111.htm",
        "note": "雷神猎刃S R9-7945HX/16G/1T/RTX5070Ti/蜂鸟屏。日常价¥10,499，国补后¥7,999。另有i9版同价。",
    },
    "甜品砖头-02-46": {
        "priceCny": 7999,
        "sourceName": "京东国补到手价",
        "sourceUrl": "https://www.ithome.com/0/852/512.htm",
        "note": "机械师曙光16S R9-7945HX/16G/1T/RTX5070Ti。首发¥9,999，国补后¥7,999。",
    },
    "甜品砖头-03-51": {
        "priceCny": 8099,
        "sourceName": "京东PLUS+国补到手价",
        "sourceUrl": "https://wiki.smzdm.com/p/oe0yvxv/",
        "note": "机械革命蛟龙16 Pro R9-8945HX/32G/1T/RTX5070Ti。面价¥10,499，PLUS+国补低至¥7,787。取¥8,099为近期中位。另有R9-9955HX版¥8,999。",
    },
    "甜品砖头-04-58": {
        "priceCny": 9699,
        "sourceName": "IT之家首发价",
        "sourceUrl": "https://www.ithome.com/0/895/874.htm",
        "note": "七彩虹橘宝R16 Pro R7-8745HX/32G/1T/RTX5070Ti。首发¥9,699。",
    },
    "甜品砖头-05-65": {
        "priceCny": 9999,
        "sourceName": "京东首发/国补价",
        "sourceUrl": "https://www.ithome.com/0/843/239.htm",
        "note": "微星泰坦16 U7-255HX/16G/1T/RTX5070Ti。国补价约¥9,999。",
    },
    "甜品砖头-06-86": {
        "priceCny": 9999,
        "sourceName": "IT之家起售价",
        "sourceUrl": "https://www.ithome.com/0/874/865.htm",
        "note": "雷神猎刃S Ultra R9-9850HX/32G/1T/RTX5070Ti。",
    },
    "甜品砖头-07-92": {
        "priceCny": 11499,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命蛟龙16 X Pro 2025 水冷模块版。",
    },
    "甜品砖头-08-98": {
        "priceCny": 11499,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命蛟龙16 Ultra 水冷模块版。",
    },
    "甜品砖头-09-103": {
        "priceCny": 9999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命蛟龙16 Pro 2025 同系列参考价。",
    },
    "甜品砖头-10-108": {
        "priceCny": 8499,
        "sourceName": "IT之家国补价",
        "sourceUrl": "https://www.ithome.com/0/846/359.htm",
        "note": "机械革命极光X Pro 2025款。国补后¥8,499。",
    },
    "甜品砖头-11-113": {
        "priceCny": 11499,
        "sourceName": "IT之家发布价",
        "sourceUrl": "https://www.ithome.com/0/848/113.htm",
        "note": "机械革命耀世16 Ultra 冰川白/水冷模块。",
    },
    "甜品砖头-12-119": {
        "priceCny": 11499,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械师曙光16S 2025 酷睿Ultra版。",
    },
    "甜品砖头-13-136": {
        "priceCny": 12999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "ROG魔霸新锐/2025/锐龙版。",
    },
    "甜品砖头-14-145": {
        "priceCny": 11499,
        "sourceName": "IT之家发布价",
        "sourceUrl": "https://www.ithome.com/0/848/113.htm",
        "note": "机械革命耀世16 Ultra 冰川白。",
    },
    "甜品砖头-15-150": {
        "priceCny": 11499,
        "sourceName": "IT之家发布价",
        "sourceUrl": "https://www.ithome.com/0/848/113.htm",
        "note": "机械革命耀世16 Ultra 冰川白/水冷模块。",
    },
    "甜品砖头-16-155": {
        "priceCny": 12999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "惠普暗影精灵MAX。",
    },
    # ═══ 高端砖头 ═══
    "高端砖头-01-41": {
        "priceCny": 14999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械师曙光16 Pro 2025。价位段14-16k。",
    },
    "高端砖头-02-50": {
        "priceCny": 16999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命耀世16 Ultra 顶配。",
    },
    "高端砖头-03-57": {
        "priceCny": 16999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命蛟龙16 Ultra 顶配。",
    },
    "高端砖头-04-66": {
        "priceCny": 17999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "微星泰坦16 2025 高配版。价位段16-18k。",
    },
    "高端砖头-05-90": {
        "priceCny": 19999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "惠普HyperX/暗影精灵MAX 顶配。",
    },
    "高端砖头-06-98": {
        "priceCny": 19999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命耀世16 Ultra 水冷版顶配。",
    },
    "高端砖头-07-104": {
        "priceCny": 19999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命蛟龙16 Ultra 水冷版顶配。",
    },
    "高端砖头-08-110": {
        "priceCny": 19999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "微星泰坦16 2025 顶配。价位段18-22k。",
    },
    "高端砖头-09-120": {
        "priceCny": 22999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "ROG枪神9/锐龙版 顶配。",
    },
    "高端砖头-10-128": {
        "priceCny": 24999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "ROG枪神9 Plus/锐龙版。18寸大屏。",
    },
    "高端砖头-11-135": {
        "priceCny": 22999,
        "sourceName": "IT之家国补价",
        "sourceUrl": "https://www.ithome.com/0/839/960.htm",
        "note": "微星雷影18 2025。18寸大屏，国补价¥22,999。",
    },
    "高端砖头-12-153": {
        "priceCny": 21999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命耀世16 Ultra 水冷版旗舰。",
    },
    "高端砖头-13-159": {
        "priceCny": 21999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "机械革命蛟龙16 Ultra 水冷版旗舰。",
    },
    "高端砖头-14-165": {
        "priceCny": 21999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "ROG枪神9/锐龙版 高配。",
    },
    "高端砖头-15-173": {
        "priceCny": 19999,
        "sourceName": "京东售价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "联想拯救者Y9000P 2025 至尊版。价位段18-22k。",
    },
    "高端砖头-16-190": {
        "priceCny": 26999,
        "sourceName": "IT之家国补价",
        "sourceUrl": "https://m.ithome.com/html/854294.htm",
        "note": "微星泰坦18 Pro 2025/锐龙版。18寸旗舰。",
    },
    "高端砖头-17-198": {
        "priceCny": 34999,
        "sourceName": "IT之家首发价",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "微星泰坦18 Pro 2025 顶配/水冷。",
    },
    "高端砖头-18-206": {
        "priceCny": 39999,
        "sourceName": "海外售价参考",
        "sourceUrl": "https://www.kdocs.cn/l/chzEHrH90jRz",
        "note": "联想Legion 9 18IAX10。海外版，无国行价格。",
    },
}


def resolve_jd_shortlink(url: str) -> dict[str, Any]:
    """Follow a u.jd.com short link to find the SKU ID."""
    import urllib.error
    import urllib.request

    result: dict[str, Any] = {"url": url}
    if not url.startswith("https://u.jd.com/"):
        return result

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", "ignore")
        match = re.search(r"var hrl='([^']+)'", html)
        if not match:
            result["error"] = "no_jda_url"
            return result
        jump_url = match.group(1)
        opener = urllib.request.build_opener(NoRedirect)
        try:
            opener.open(urllib.request.Request(jump_url, headers={"User-Agent": UA, "Referer": url}), timeout=20)
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location", "")
            result["resolvedUrl"] = location
            sku = _sku_from_url(location)
            if sku:
                result["sku"] = sku
    except Exception as exc:
        result["error"] = type(exc).__name__
    return result


def _sku_from_url(url: str) -> str | None:
    for pat in [r"/product/(\d+)\.html", r"item\.jd\.com/(\d+)\.html", r"[?&]sku(?:Id)?=(\d+)"]:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


async def _extract_product_config(sku: str) -> dict[str, Any]:
    """Use Playwright to extract pageConfig.product from a JD page."""
    from playwright.async_api import async_playwright

    result: dict[str, Any] = {"sku": sku, "itemUrl": f"https://item.jd.com/{sku}.html"}
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=UA,
                locale="zh-CN",
            )
            page = await context.new_page()
            await page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            # Warm cookies from homepage
            await page.goto("https://www.jd.com/", timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            await page.goto(result["itemUrl"], timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)

            product = await page.evaluate("""() => {
                const p = window.pageConfig?.product;
                if (!p) return null;
                return {
                    name: p.name,
                    skuid: p.skuid,
                    colorSize: p.colorSize,
                    skuMarkJson: p.skuMarkJson,
                    venderId: p.venderId,
                    shopId: p.shopId,
                    catName: p.catName,
                    stockSkuNum: p.stockSkuNum,
                };
            }""")

            if product:
                result["title"] = product.get("name", "")
                result["variants"] = product.get("colorSize") or []
                result["stockSkuNum"] = product.get("stockSkuNum")
                result["isSelf"] = True  # implied by successful extraction

            await browser.close()
    except Exception as exc:
        result["error"] = type(exc).__name__
    return result


def _build_configs(variants: list[dict[str, Any]], source_sku: str) -> list[dict[str, Any]]:
    """Convert JD colorSize variants to our configs format."""
    configs: list[dict[str, Any]] = []
    for v in variants:
        sku_id = str(v.get("skuId", ""))
        # Build a readable spec string from variant keys
        parts = []
        for key in ["处理器或显卡", "存储", "颜色", "内存", "硬盘"]:
            if key in v and v[key]:
                parts.append(str(v[key]))
        spec = "|".join(parts) if parts else sku_id
        configs.append({
            "sku": sku_id,
            "spec": spec,
            "isDefault": sku_id == source_sku,
        })
    return configs


def _lookup_price(item_id: str) -> dict[str, Any] | None:
    """Look up price in the maintained database."""
    return PRICE_DATABASE.get(item_id)


async def main() -> None:
    data = json.loads(LAPTOPS.read_text(encoding="utf-8"))
    overrides: dict[str, Any] = {}
    collected_at = time.strftime("%Y-%m-%d")
    items = data["items"]

    print(f"Collecting prices for {len(items)} items...")
    print(f"{'='*70}")

    for i, item in enumerate(items):
        item_id = item["id"]
        brand = item["brand"]
        model = item["model"]
        link = item.get("guideLink", "")

        print(f"\n[{i+1}/{len(items)}] {item_id} | {brand} {model}")

        db_price = _lookup_price(item_id)
        entry: dict[str, Any] = {
            "collectedAt": collected_at,
        }

        # ── Step 1: Resolve JD shortlink / get SKU ──
        sku: str | None = None
        variants: list[dict[str, Any]] = []
        if link.startswith("https://u.jd.com/"):
            resolved = resolve_jd_shortlink(link)
            sku = resolved.get("sku")
            if sku:
                entry["sku"] = sku
                entry["itemUrl"] = f"https://item.jd.com/{sku}.html"
                entry["resolvedUrl"] = resolved.get("resolvedUrl", "")

                # ── Step 2: Extract variant/SKU data via Playwright ──
                print(f"  SKU: {sku} → extracting product config...")
                product_data = await _extract_product_config(sku)
                if product_data.get("title"):
                    entry["title"] = product_data["title"]
                if product_data.get("variants"):
                    variants = product_data["variants"]
                    entry["variantCount"] = len(variants)
                    entry["configs"] = _build_configs(variants, sku)
                    print(f"  Got {len(variants)} variants")
                if product_data.get("error"):
                    print(f"  Playwright error: {product_data['error']}")
            else:
                print(f"  Shortlink resolution failed: {resolved.get('error', 'unknown')}")
        else:
            print(f"  No JD shortlink (link: {link[:60]}...)")

        # ── Step 3: Merge price from database ──
        if db_price:
            entry["priceCny"] = db_price["priceCny"]
            entry["sourceName"] = db_price["sourceName"]
            entry["sourceUrl"] = db_price["sourceUrl"]
            entry["note"] = db_price.get("note", "")
            entry["confidence"] = "medium"
            entry["method"] = "price_database"

            # Attach prices to configs if price database has per-config data
            if entry.get("configs") and db_price.get("configs"):
                db_configs = {c["sku"]: c for c in db_price["configs"]}
                for cfg in entry["configs"]:
                    if cfg["sku"] in db_configs:
                        cfg["priceCny"] = db_configs[cfg["sku"]].get("priceCny")

            print(f"  Price: ¥{entry['priceCny']:,} ({entry['sourceName']})")
        else:
            entry["confidence"] = "missing"
            entry["method"] = "not_found"
            entry["sourceName"] = "待核价"
            entry["sourceUrl"] = item.get("imageSource") or "https://www.kdocs.cn/l/chzEHrH90jRz"
            entry["note"] = "暂未在价格数据库中找到此机型。"
            print(f"  Price: NOT FOUND in database")

        overrides[item_id] = entry

    # ── Write output ──
    OUTPUT.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")
    priced = sum(1 for e in overrides.values() if e.get("priceCny"))
    with_variants = sum(1 for e in overrides.values() if e.get("configs"))
    print(f"\n{'='*70}")
    print(f"Done: {priced}/{len(items)} priced, {with_variants} with variants → {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
