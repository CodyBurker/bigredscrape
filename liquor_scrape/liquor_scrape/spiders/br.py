from pathlib import Path
import json
import scrapy
from urllib.parse import unquote
from hashlib import md5
import jsonlines
import datetime
from pymongo import MongoClient
import os

# subtype = "https://bigredliquors.com/shop/?subtype=whiskey&skip=0"
subtype = "whiskey"
order = "name+asc"
style = "list"
# cookie
# stores = ["5e92445578e8f13c2cb1e14c","5e92506478e8f13c2cb1e150"]
stores = ["5e92544978e8f13c2cb1e16c"]

class BigRed(scrapy.Spider):
    name = "br"

    def start_requests(self):
        urls = [
            "https://bigredliquors.com/shop/?subtype=whiskey",
        ]
        for url in urls:
            for i in range(0,10000,18):
              url2 = f"{url}&skip={i}&order={order}"
              for store in stores:
                self.log(f'Checking store: {store}: skip:{i}')
                yield scrapy.Request(url=url2, callback=self.parse, cookies={'ch_currentMerchantId': store})
    def extract_text(self, response, beg, end):
      """
      Extracts text from a string between two delimiters.

      Args:
        response: The input string.
        beg: The beginning delimiter.
        end: The ending delimiter.

      Returns:
        The extracted text, or None if the delimiters are not found.
      """
      results = [x for x in response.css('script').getall() if 'ch-elements.search-results' in x]
      if results:
        result = results[0]
        start_index = result.find(beg) + len(beg)
        end_index = result.find(end, start_index)
        # self.log(f"Beg: {start_index}:\t{end_index}")
        if start_index != -1 and end_index != -1:
          return result[start_index:end_index]
      return None
  
    def parse(self, response):
        # results = [x for x in response.css('script').getall() if 'ch-elements.search-results' in x]
        # self.log(f"Found {len(results)} results")
        # Check if the div "no-products" exists. If so stop scraping with CloseSpider exception
        # if response.xpath("//*[contains(text(), 'No products to show')]").get():
        # self.log(f'No products to show? {'No products to show'.lower() in response.text.lower()}')
        # if 'No proudcts to show' in response.text:
          #  self.log(f'Found empty page')
          #  raise scrapy.exceptions.CloseSpider('End of products')
        beg = "JSON.parse(decodeURIComponent(\""
        end = "\"));"
        parsed = self.extract_text(response, beg, end)
        decoded_json = unquote(parsed)
        data = json.loads(decoded_json)['products']
        # Surface merchant id(s) to top level too
        new_data = []
        for item in data:
          new_item = item
          new_item['merchant_id'] = item['merchants'][0]['merchant_id']
          new_item['date'] = datetime.date.today().strftime('%Y-%m-%d')
          new_data.append(new_item)
        if len(data) == 0:
           self.log('Found empty page now.')
           raise scrapy.exceptions.CloseSpider('End of products')
        # Probably need to do something fancy to avoid creating a ton of connections but here we are
        client = MongoClient()
        import os
        pw = os.environ['PW']
        cnstg = f"mongodb+srv://codyburker:{pw}@cluster0.phkpa.mongodb.net/"
        client = MongoClient(cnstg)
        db = client.bigred
        collection = db.bigred
        collection.insert_many(new_data)
        # with jsonlines.open('output.jsonl',mode='a') as writer:
        #    writer.write_all(new_data)