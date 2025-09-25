from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
from urllib.parse import urlparse
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit='product.template'

    publisher_link=fields.Char("publisher link")

class importProductFromWebsite(models.TransientModel):
    _name = 'import.product.from.website'
    _description = 'import product from website'

    # Define fields (if needed)

    target_url = fields.Char(string="target URL")
    source_url = fields.Char(string="Source")
    product_name = fields.Char(string="Product Name")
    image_url = fields.Char(string="Image URL")
    ecommerce_description = fields.Text(string="E-commerce Description")
    face_value = fields.Float(string="Printed Price")
    stock_qty = fields.Integer(string="Stock Quantity")
    price = fields.Float(string="Sale Price")
    isbn = fields.Char(string="ISBN")
    pages = fields.Integer(string="Pages")
    editions = fields.Char(string="Editions")
    publication_date = fields.Char(string="Publication Date")
    # weight=fields.Float("weight")

    def fetch_data(self):
        url= urlparse(self.source_url)
        host= url.hostname
        domain_name=host.split('.')[1]
        if hasattr(self, '%s_products' % domain_name):
            return getattr(self, '%s_products' % domain_name)()
        else :
            return "cannt import product data from "+ domain_name



    def guardianpubs_products(self):
        url = self.source_url
        driver = webdriver.Chrome()  # or webdriver.Firefox()
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(3)  # wait for Angular to load content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        stock_div = soup.find("div", class_="stock")

        if stock_div:
            stock_text = stock_div.get_text(strip=True)
            self.stock_qty=int(re.findall(r'\d+', stock_text) [0])
        name_div = soup.find("div", class_="product-title")
        if name_div:
            self.product_name=name_div.get_text(strip=True)
        price_div = soup.find("div", class_="product-price")
        if price_div:
            price_text = price_div.get_text(strip=True)
            # Mapping Bengali digits to English
            bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

            # Find all Bengali numbers
            matches = re.findall(r"[০-৯]+", price_text)

            # Convert to English + int
            prices = [int(m.translate(bangla_to_english)) for m in matches]

            self.face_value=prices[0]
            if len (prices) > 1:
                self.price=prices[1]
            else:
                self.price=prices[0]


        description_div = soup.find("div", class_="description")
        if description_div:
            self.ecommerce_description=description_div.get_text(strip=True)
        img_tag = soup.select_one("div.product-image-box img")

        if img_tag and img_tag.has_attr("src"):
            self.image_url = img_tag["src"]

        desc_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "বিবরণ")]')))
        driver.execute_script("arguments[0].click();", desc_button)

        time.sleep(2)  # allow Angular to load content

        soup = BeautifulSoup(driver.page_source, "html.parser")

        isbn_td = None
        for row in soup.select("div.specification table tr"):
            th = row.find("th")
            td = row.find("td")
            if th and "ISBN" in th.get_text(strip=True):
                self.isbn = td.get_text(strip=True)
            if th and "Publish" in th.get_text(strip=True):
                self.publication_date = td.get_text(strip=True)
            if th and "Number of Pages" in th.get_text(strip=True):
                self.pages = td.get_text(strip=True)

            if th and "Title" in th.get_text(strip=True):
                self.product_name = td.get_text(strip=True)




        driver.quit()


    def khoshrozltd_products(self):
        url = self.source_url
        driver = webdriver.Chrome()  # or webdriver.Firefox()
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(3)  # wait for Angular to load content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        stock_div = soup.find("span", id="available-quantity")

        if stock_div:
            stock_text = stock_div.get_text(strip=True)
            self.stock_qty=int(stock_text)
        name_div = soup.find("h1", class_="mb-2 fs-20 fw-600")
        if name_div:
            self.product_name=name_div.get_text(strip=True)
        price_div = soup.find("div", class_="fs-16 opacity-60")
        if price_div:
            price_text = price_div.get_text(strip=True)
            match = re.search(r"[\d.]+", price_text)
            if match:
                price = float(match.group())
            self.face_value = price
        price_div = soup.find("strong", class_="h4 fw-700 text-primary")
        if price_div:
            price_text = price_div.get_text(strip=True)
            match = re.search(r"[\d.]+", price_text)
            if match:
                price = float(match.group())
            self.price = price

        description_div = soup.find("div", class_="mw-100 text-left")
        if description_div:
            self.ecommerce_description=description_div.decode_contents() # decode_context() get the inner html

        img_tag = soup.find("img",role="presentation")

        if img_tag and img_tag.has_attr("src"):
            self.image_url = img_tag["src"]

        desc_button = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Specification ")]')))
        driver.execute_script("arguments[0].click();", desc_button)

        time.sleep(2)  # allow Angular to load content

        soup = BeautifulSoup(driver.page_source, "html.parser")

        isbn_td = None
        for row in soup.select("#spec-table tr"):
            cells = row.find_all("td")
            print(cells[0].get_text(strip=True).lower())
            if len(cells) == 2 and "isbn" in cells[0].get_text(strip=True).lower():
                self.isbn = cells[1].get_text(strip=True)
            if len(cells) == 2 and "Number of Pages" in cells[0].get_text(strip=True):
                self.pages = cells[1].get_text(strip=True)

            if len(cells) == 2 and "Number of Pages" in cells[0].get_text(strip=True):
                self.pages = cells[1].get_text(strip=True)

        #     if th and "Publish" in th.get_text(strip=True):
        #         self.publication_date = td.get_text(strip=True)
        #     if th and "Title" in th.get_text(strip=True):
        #         self.product_name = td.get_text(strip=True)
        #



        driver.quit()

    def rokomari_products(self):
        url = self.source_url
        driver = webdriver.Chrome()  # or webdriver.Firefox()
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(3)  # wait for Angular to load content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        stock_div = soup.find("span", id="available-quantity")

        if stock_div:
            stock_text = stock_div.get_text(strip=True)
            self.stock_qty=int(stock_text)
        name_div = soup.find("h1", class_="mb-2 fs-20 fw-600")
        if name_div:
            self.product_name=name_div.get_text(strip=True)
        price_div = soup.find("div", class_="fs-16 opacity-60")
        if price_div:
            price_text = price_div.get_text(strip=True)
            match = re.search(r"[\d.]+", price_text)
            if match:
                price = float(match.group())
            self.face_value = price
        price_div = soup.find("del", class_="original-price")
        if price_div:
            price_text = price_div.get_text(strip=True)
            number = float(price_text.split()[1])
            self.face_value=number

        description_div = soup.find("div", class_="shortSummery_summeryText__ycsRa")
        if description_div:
            self.ecommerce_description=description_div.decode_contents() # decode_context() get the inner html

        img_tag = soup.select_one("div#ts--desktop-details-book-image-container img")

        if img_tag and img_tag.has_attr("src"):
            self.image_url = img_tag["src"]
        # fields that is shown after pressing specification Button
        desc_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Specification")]')))
        driver.execute_script("arguments[0].click();", desc_button)

        time.sleep(2)  # allow Angular to load content

        soup = BeautifulSoup(driver.page_source, "html.parser")

        isbn_td = None
        for row in soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) == 2 and "isbn" in cells[0].get_text(strip=True).lower():
                self.isbn = cells[1].get_text(strip=True)
            if len(cells) == 2 and "Name" in cells[0].get_text(strip=True):
                self.product_name = cells[1].get_text(strip=True)
            if len(cells) == 2 and "Edition" in cells[0].get_text(strip=True):
                self.publication_date = cells[1].get_text(strip=True)

            if len(cells) == 2 and "No of Page" in cells[0].get_text(strip=True):
                self.pages = cells[1].get_text(strip=True)






        driver.quit()


    def create_product(self):
        vals={}
        vals['publisher_link']=self.source_url
        vals['name']=self.product_name
        vals['is_storable']=True
        vals['pages']=self.pages
        vals['last_edition']=self.publication_date
        vals['isbn']=self.isbn
        vals['list_price']=self.face_value
        vals['description_ecommerce']=self.ecommerce_description
        vals['image_url_template']=self.image_url



        product=self.env['product.template'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'res_id': product.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',  # or 'new' for popup
            'context': self.env.context,
        }

    def action_open_google_image_search(self):
        self.ensure_one()
        query = self.name or ""
        return {
            'type': 'ir.actions.act_url',
            'url': f"https://www.google.com/search?tbm=isch&q={query}",
            'target': 'new',  # open in new tab
        }