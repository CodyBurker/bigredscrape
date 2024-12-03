from pathlib import Path
import json
import scrapy
from urllib.parse import unquote
from hashlib import md5

# subtype = "https://bigredliquors.com/shop/?subtype=whiskey&skip=0"
subtype = "whiskey"
order = "name+asc"
style = "list"
# cookie
store = "5e92445578e8f13c2cb1e14c"
class BigRed(scrapy.Spider):
    name = "br"

    def start_requests(self):
        urls = [
            "https://bigredliquors.com/shop/?subtype=whiskey",
        ]
        for url in urls:
            for i in range(0,1000,18):
              url2 = f"{url}&skip={i}&order={order}"
              yield scrapy.Request(url=url2, callback=self.parse)
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
        self.log(f"Beg: {start_index}:\t{end_index}")
        if start_index != -1 and end_index != -1:
          return result[start_index:end_index]
      return None
  
    def parse(self, response):
        # results = [x for x in response.css('script').getall() if 'ch-elements.search-results' in x]
        # self.log(f"Found {len(results)} results")
        beg = "JSON.parse(decodeURIComponent(\""
        end = "\"));"
        parsed = self.extract_text(response, beg, end)
         
        decoded_json = unquote(parsed)
        data = json.loads(decoded_json)
        Path(f'results/{md5(decoded_json.encode()).hexdigest()}.json').write_text(json.dumps(data, indent=9))
        # Path('result').write_text(decoded_json)
        # page = response.url.split("/")[-2]
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(json.dumps(results))
        # self.log(f"Saved file {filename}")