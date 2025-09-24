from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
from urllib.parse import urlparse
from odoo import models, fields, api

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


    def create_product(self):
        vals={}
        vals['name']=self.product_name
        vals['is_storable']=True
        vals['page']=self.pages
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

