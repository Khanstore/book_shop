"""class PBSExtractor:
    """Helper class to extract data from PBS product pages"""

    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def get_title(self):
        """Extract book title"""
        selectors = [
            ("h1", {"class": lambda x: x and "text-xl" in x}),  # usually main title
            ("h1", {"itemprop": "name"}),
        ]
        return self._extract_text(selectors, "Unknown Title")

    def get_original_price(self):
        """Extract current and original price"""
        # Prices are inside <p class="price"> with <ins> and <del>
        price_container = self.soup.select_one("p del")
        if price_container:
            return self._parse_price(price_container.get_text(strip=True))
        return 0
    def get_current_price(self):
        """Extract current and original price"""
        price_container = self.soup.select_one("p del").parent.parent.find('h5')
        if price_container:
            return self._parse_price(price_container.get_text(strip=True))
        return 0

    def get_description(self):
        """Extract book description (বই সংক্ষেপ)"""
        heading = self.soup.find("h5", string=lambda t: t and "বই সংক্ষেপ" in t)
        if heading:
            desc_p = heading.find_parent().find_next("p")
            if desc_p:
                return desc_p.get_text(" ", strip=True)
        return ""

    def get_authors(self):
        """Extract book description (বই সংক্ষেপ)"""
        author_tag = self.soup.find('span', string='লেখক')
        if author_tag:
            author_name = author_tag.parent.find_parent().find_next("p")
            if desc_p:
                return desc_p.get_text(" ", strip=True)
        return ""

    def get_image_url(self):
        """Extract main book cover image"""
        img = self.soup.select_one("div.grid img")
        if img:
            src ="https://pbs.com.bd" + img.get("src")

            # Parse the URL
            parsed = urllib.parse.urlparse(src)
            query = urllib.parse.parse_qs(parsed.query)

            # Extract the 'url' parameter and decode it
            if "url" in query:
                clean_url = urllib.parse.unquote(query["url"][0])
                return clean_url

    def get_specifications(self):
        """Extract all specifications from details table"""
        specs = {}
        table = self.soup.find("table")
        if not table:
            return specs

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[-1].get_text(strip=True)

                if "isbn" in key:
                    specs["isbn"] = value
                # elif "Translator" in key or "অনুবাদক" in key:
                #     specs["author"] = value
                # elif "author" in key or "লেখক" in key:
                #     specs["author"] = value
                elif "publisher" in key or "প্রকাশক" in key:
                    specs["publisher"] = value
                elif "title" in key:
                    specs["title"] = value
                elif "edition" in key or "সংস্করণ" in key:
                    specs["edition"] = value
                elif "number of pages" in key or "পৃষ্ঠা" in key:
                    match = re.search(r'\d+', value)
                    specs["pages"] = match.group() if match else value
                elif "language" in key or "ভাষা" in key:
                    specs["language"] = value
                elif "country" in key or "দেশ" in key:
                    specs["country"] = value

        return specs

    # ------------------- Helpers ------------------- #
    def _extract_text(self, selectors, default=""):
        for tag, attrs in selectors:
            elem = self.soup.find(tag, attrs)
            if elem:
                return elem.get_text(strip=True)
        return default

    def _parse_price(self, text):
        """Parse price into float"""
        if not text:
            return 0.0
        match = re.search(r'[\d,]+\.?\d*', text)
        return float(match.group().replace(',', '')) if match else 0.0"""
