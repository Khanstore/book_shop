



class RokomariExtractor:
    """Helper class to extract data from Rokomari product pages"""

    def __init__(self, soup):
        self.soup = soup

    def get_title(self):
        selectors = [
            ("h1", {"class": "mb-2 fs-20 fw-600"}),
            ("h1", {"class": lambda x: x and "book-title" in x.lower()}),
            ("h1", {"itemprop": "name"}),
        ]
        return self._extract_text(selectors, "Unknown Product")

    def get_current_price(self):
        selectors = [
            ("div", {"class": "fs-16 opacity-60"}),
            ("span", {"class": "price-current"}),
            ("span", {"class": lambda x: x and "price" in x.lower()}),
        ]
        return self._parse_price(self._extract_text(selectors))

    def get_original_price(self):
        selectors = [
            ("del", {"class": "original-price"}),
            ("span", {"class": "price-original"}),
            ("del", {}),
        ]
        return self._parse_price(self._extract_text(selectors))

    def get_stock_quantity(self):
        stock_elem = self.soup.find("span", id="available-quantity")
        if stock_elem:
            stock_text = stock_elem.get_text(strip=True)
            match = re.search(r'\d+', stock_text)
            return int(match.group()) if match else 0
        return 0  # safer default

    def get_description(self):
        selectors = [
            ("div", {"class": "shortSummery_summeryText__ycsRa"}),
            ("div", {"class": lambda x: x and "summary" in x.lower()}),
            ("div", {"itemprop": "description"}),
        ]
        desc_elem = self._find_element(selectors)
        return desc_elem.decode_contents().strip() if desc_elem else ""

    def get_image_url(self):
        script_tag = self.soup.find("script", {"type": "application/ld+json"})

        if script_tag:
            data = json.loads(script_tag.string.strip())
            image_url = data.get("image")
            return image_url



    def get_specifications(self):
        specs = {}
        for row in self.soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if "title" in key:
                    specs['title'] = value
                if "isbn" in key:
                    specs['isbn'] = value
                elif "author" in key or "লেখক" in key:
                    specs['author'] = value
                elif "publisher" in key or "প্রকাশক" in key:
                    specs['publisher'] = value
                elif "page" in key or "পৃষ্ঠা" in key:
                    match = re.search(r'\d+', value)
                    specs['pages'] = match.group() if match else value
                elif "edition" in key or "সংস্করণ" in key:
                    specs['edition'] = value
                elif "language" in key or "ভাষা" in key:
                    specs['language'] = value
                elif "country" in key or "দেশ" in key:
                    specs['country'] = value
                elif "weight" in key:
                    match = re.search(r'[\d.]+', value)
                    specs['weight'] = float(match.group()) if match else 0.0
        return specs

    # --- helpers ---
    def _extract_text(self, selectors, default=""):
        for tag, attrs in selectors:
            elem = self.soup.find(tag, attrs)
            if elem:
                return elem.get_text(strip=True)
        return default

    def _find_element(self, selectors):
        for tag, attrs in selectors:
            elem = self.soup.find(tag, attrs)
            if elem:
                return elem
        return None

    def _parse_price(self, price_text):
        if not price_text:
            return 0.0
        match = re.search(r'[\d,]+\.?\d*', price_text.replace('৳', '').replace('Tk', ''))
        return float(match.group().replace(',', '')) if match else 0.0

    def _normalize_url(self, url):
        if not url:
            return None
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return 'https://www.rokomari.com' + url
        return url