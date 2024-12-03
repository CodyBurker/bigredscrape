from pathlib import Path
import json
import scrapy

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
            "https://bigredliquors.com/shop/?subtype=whiskey&skip=0",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        results = [x for x in response.css('script').getall() if 'ch-elements.search-results' in x]
        self.log(f"Found {len(results)} results")
        "JSON.parse(decodeURIComponent("
        """
"));
      e.setAttribute('search-results', JSON.stringify(results));
        """
        # Path('result').write_text(results[0])
        # page = response.url.split("/")[-2]
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(json.dumps(results))
        # self.log(f"Saved file {filename}")