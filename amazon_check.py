import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

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
        if "haz clic" in f.lower():
            continue
        if "opinion" in f.lower():
            continue
        if "calificación" in f.lower():
            continue
        filtered.append(f)

    return filtered[:10]

def get_description(soup):
    description_selectors = [
        "#productDescription",
        "#aplus",
        "#bookDescription_feature_div",
        "#feature-bullets"
    ]

    parts = []

    for selector in description_selectors:
        el = soup.select_one(selector)
        if el:
            txt = clean_text(el.get_text(" ", strip=True))
            if txt and txt not in parts:
                parts.append(txt)

    return " ".join(parts).strip()

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
                    # viene como JSON/string con varias URLs
                    found_urls = re.findall(r'https://[^"]+', value)
                    for url in found_urls:
                        if url not in images:
                            images.append(url)
                else:
                    if value not in images:
                        images.append(value)

    # limpiar miniaturas o imágenes vacías
    cleaned = []
    for img in images:
        if not img:
            continue
        if "sprite" in img.lower():
            continue
        cleaned.append(img)

    return cleaned[:15]

def classify_stock(av_text: str) -> str:
    low = av_text.lower()

    if (
        "in stock" in low
        or "disponible" in low
        or "hay existencias" in low
    ):
        return "in_stock"

    if (
        "currently unavailable" in low
        or "no disponible" in low
        or "temporarily out of stock" in low
        or "agotado" in low
    ):
        return "out_of_stock"

    if "pre-order" in low or "preorder" in low or "preventa" in low:
        return "preorder"

    if (
        "usually ships" in low
        or "ships within" in low
        or "envío en" in low
        or "se envía en" in low
    ):
        return "delayed"

    return "unknown"

def scrape_amazon_product(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=30)

    if response.status_code != 200:
        return {
            "ok": False,
            "http_status": response.status_code,
            "message": "No se pudo obtener la página",
            "url": url,
            "checked_at": datetime.now().isoformat()
        }

    soup = BeautifulSoup(response.text, "lxml")

    title = get_first_text(soup, [
        "#productTitle",
        "#title",
        "h1.a-size-large"
    ])

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
    main_image = images[0] if images else ""
    status = classify_stock(availability_text) if availability_text else "unknown"

    data = {
        "ok": True,
        "url": url,
        "title": title,
        "price": price,
        "availability_text": availability_text,
        "status": status,
        "description": description,
        "features": features,
        "main_image": main_image,
        "images": images,
        "checked_at": datetime.now().isoformat()
    }

    return data

if __name__ == "__main__":
    url = "https://www.amazon.com/-/es/Lenovo-Legion-Tower-Inteligencia-Almacenamiento/dp/B0F5YNX43T/ref=sr_1_1?_encoding=UTF8&content-id=amzn1.sym.edf433e2-b6d4-408e-986d-75239a5ced10&dib=eyJ2IjoiMSJ9.f-mrOrpTgHZ0CD-BT_mxSpQ78eiraXuUr2LrCMaO1aKQm4AB39mOIr7m9t4J5KOLUzudY9jN1s7eiU4XR29rJQuYVqJUTTS1TC4Iz4suOBEZx4-L6c-U0jGnrErqesvHb-KRWEFxxmnaxGrgmV55Y6hHObgjyhEYDwZwx_tdkizeM6ZhZggFYzMv92lOsOXuTjEZbZ1Vvm31Qj0VuTzBDq_8jm9AhfzL9bS4jaFvObeCMdwcwaDzeoG_GSPt3DAOBiDVZnnZe7L15xIgbnabPeoX3OF8qLmZ1HjDxpvOgfA.XFsaL_TV3t8WEc0rwxdZjoPGyQQHZ_TXGvcy9qZIQ0A&dib_tag=se&keywords=gaming&pd_rd_r=63b50a1e-0b52-4565-95e5-1ada81e9b8d6&pd_rd_w=fomL9&pd_rd_wg=7PBhe&qid=1776742862&sr=8-1"
    data = scrape_amazon_product(url)

    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("Imagen principal:", data["main_image"])
print("Galería:")
for img in data["images"]:
    print(img)  