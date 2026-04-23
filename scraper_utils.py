import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

def get_conn(database_url):
    return psycopg2.connect(database_url)

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def get_first_text(soup, selectors):
    for selector in selectors:
        el = soup.select_one(selector)
        if el:
            txt = clean_text(el.get_text(" ", strip=True))
            if txt:
                return txt
    return ""

def get_description(soup):
    selectors = [
        "#productDescription",
        "#aplus",
        "#bookDescription_feature_div",
        "#feature-bullets"
    ]
    parts = []
    for selector in selectors:
        el = soup.select_one(selector)
        if el:
            txt = clean_text(el.get_text(" ", strip=True))
            if txt and txt not in parts:
                parts.append(txt)
    return " ".join(parts).strip()

def get_features(soup):
    features = []
    selectors = [
        "#feature-bullets ul li span",
        "#feature-bullets li",
        "#detailBullets_feature_div li span"
    ]

    for selector in selectors:
        items = soup.select(selector)
        for item in items:
            txt = clean_text(item.get_text(" ", strip=True))
            if txt and txt not in features and len(txt) > 2:
                features.append(txt)

    filtered = []
    for f in features:
        low = f.lower()
        if "haz clic" in low or "opinion" in low or "calificación" in low:
            continue
        filtered.append(f)

    return filtered[:10]

def get_images(soup):
    images = []

    selectors = [
        "#landingImage",
        "#imgTagWrapperId img",
        "img.a-dynamic-image",
        "#main-image-container img",
        "#altImages img"
    ]

    for selector in selectors:
        items = soup.select(selector)
        for item in items:
            for attr in ["src", "data-old-hires", "data-a-dynamic-image"]:
                value = item.get(attr)
                if not value:
                    continue

                if attr == "data-a-dynamic-image":
                    found_urls = re.findall(r'https://[^"]+', value)
                    for url in found_urls:
                        if url not in images:
                            images.append(url)
                else:
                    if value not in images:
                        images.append(value)

    cleaned = []
    for img in images:
        if img and "sprite" not in img.lower():
            cleaned.append(img)

    return cleaned[:15]

def classify_stock(av_text: str) -> str:
    low = av_text.lower()

    if "in stock" in low or "disponible" in low or "hay existencias" in low:
        return "in_stock"

    if "currently unavailable" in low or "no disponible" in low or "temporarily out of stock" in low or "agotado" in low:
        return "out_of_stock"

    if "pre-order" in low or "preorder" in low or "preventa" in low:
        return "preorder"

    if "usually ships" in low or "ships within" in low or "envío en" in low or "se envía en" in low:
        return "delayed"

    return "unknown"

def scrape_amazon_product(url: str, database_url=None) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=30)

    with open("amazon_debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("HTTP STATUS:", response.status_code)
    print("URL FINAL:", response.url)
    print("HTML guardado en amazon_debug.html")

    if response.status_code != 200:
        return {
            "ok": False,
            "title": "",
            "price_text": "",
            "availability_text": "",
            "stock_status": "error",
            "description": "",
            "main_image_url": "",
            "images": [],
            "checked_at": datetime.now().isoformat()
        }

    soup = BeautifulSoup(response.text, "lxml")

    title = get_first_text(soup, ["#productTitle", "#title", "h1.a-size-large"])

    price = get_first_text(soup, [
        ".a-price .a-offscreen",
        "#corePrice_feature_div .a-offscreen",
        "#price_inside_buybox",
        "#newBuyBoxPrice",
        "#tp_price_block_total_price_ww .a-offscreen",
        "#apex_desktop .a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#priceblock_saleprice"
    ])

    availability_text = get_first_text(soup, [
        "#availability span",
        "#availability",
        "#outOfStock span",
        "#deliveryBlockMessage",
        "#availabilityInsideBuyBox_feature_div",
        "#mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE",
        "#exports_desktop_qualifiedBuybox_quantityFeatures",
        "#availability_feature_div"
    ])

    print("TITLE:", title)
    print("PRICE:", price)
    print("AVAILABILITY:", availability_text)

    description = get_description(soup)
    features = get_features(soup)
    images = get_images(soup)
    main_image_url = images[0] if images else ""
    stock_status = classify_stock(availability_text) if availability_text else "unknown"

    final_description = description
    if features:
        feature_text = " | ".join(features)
        if feature_text not in final_description:
            final_description = (final_description + " " + feature_text).strip()

    return {
        "ok": True,
        "title": title,
        "price_text": price,
        "availability_text": availability_text,
        "stock_status": stock_status,
        "description": final_description,
        "main_image_url": main_image_url,
        "images": images,
        "checked_at": datetime.now().isoformat()
    }
    response = requests.get(url, headers=HEADERS, timeout=30)

    if response.status_code != 200:
        return {
            "ok": False,
            "title": "",
            "price_text": "",
            "availability_text": "",
            "stock_status": "error",
            "description": "",
            "main_image_url": "",
            "images": [],
            "checked_at": datetime.now().isoformat()
        }

    soup = BeautifulSoup(response.text, "lxml")

    title = get_first_text(soup, ["#productTitle", "#title", "h1.a-size-large"])
    price = get_first_text(soup, [
        ".a-price .a-offscreen",
        "#corePrice_feature_div .a-offscreen",
        "#price_inside_buybox",
        "#newBuyBoxPrice",
        "#tp_price_block_total_price_ww .a-offscreen",
        "#apex_desktop .a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#priceblock_saleprice"
    ])

    availability_text = get_first_text(soup, [
        "#availability span",
        "#availability",
        "#outOfStock span",
        "#deliveryBlockMessage",
        "#availabilityInsideBuyBox_feature_div"
    ])

    description = get_description(soup)
    features = get_features(soup)
    images = get_images(soup)
    main_image_url = images[0] if images else ""
    stock_status = classify_stock(availability_text) if availability_text else "unknown"

    final_description = description
    if features:
        feature_text = " | ".join(features)
        if feature_text not in final_description:
            final_description = (final_description + " " + feature_text).strip()

    return {
        "ok": True,
        "title": title,
        "price_text": price,
        "availability_text": availability_text,
        "stock_status": stock_status,
        "description": final_description,
        "main_image_url": main_image_url,
        "images": images,
        "checked_at": datetime.now().isoformat()
    }

def update_product_data(product_id: int, data: dict, database_url: str):
    conn = get_conn(database_url)
    cur = conn.cursor()

    cur.execute("""
        UPDATE products
        SET title = %s,
            price_text = %s,
            availability_text = %s,
            stock_status = %s,
            description = %s,
            main_image_url = %s,
            checked_at = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (
        data["title"],
        data["price_text"],
        data["availability_text"],
        data["stock_status"],
        data["description"],
        data["main_image_url"],
        data["checked_at"],
        product_id
    ))

    cur.execute("DELETE FROM product_images WHERE product_id = %s", (product_id,))

    for i, image_url in enumerate(data["images"]):
        cur.execute("""
            INSERT INTO product_images (product_id, image_url, sort_order)
            VALUES (%s, %s, %s)
        """, (product_id, image_url, i))

    conn.commit()
    cur.close()
    conn.close()