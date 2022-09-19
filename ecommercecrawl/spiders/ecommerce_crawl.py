from unicodedata import category
import scrapy
from datetime import date
import re

class EcomSpider(scrapy.Spider):
    name = "farfetch"
    custom_settings = {'CLOSESPIDER_PAGECOUNT': 100}
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

    def start_requests(self):
        urls = [
            'https://www.farfetch.com/ae/shopping/women/clothing-1/items.aspx',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_no_pages(self, response):
        """
        get number of pages in given category page and return urls of all pages
        """
        search = re.compile(r'"totalPages\\\\":([0-9]+),\\\\', re.IGNORECASE)\
            .findall(str(response.body))[-1]
        pages = [x + 1 for x in range(int(search))][1:]
        urls = [response.url + f'?page={str(page)}' for page in pages]
        return urls

    def parse(self, response):
        # check if ending with items.aspx > plp
        if response.url.split('/')[-1].split('?')[0] == 'items.aspx':
            # check if first page, if first get all pages
            if len(response.url.split('?')) > 1:
                pass
            else:
                urls = self.get_no_pages(response)
                for url in urls:
                    yield scrapy.Request(url=url, callback=self.parse)
            # get all pdps from plp               
            pdps = response.xpath('//a[@data-component="ProductCardLink"]/@href').getall()
            for pdp in pdps:
                yield scrapy.Request(response.urljoin(pdp), callback=self.parse)
        else: 
            response.url.split('/')[-1].split('?')[0] != 'items.aspx'
            price = response.css('div.ltr-10c5n0l.eev02n90>p.ltr-o8ptjq-Heading.ex663c10::text').get()
            breadcrumbs = response.css('a.ltr-4egbt7-Footnote.e1w8i7z30::text').getall()
            yield {
            'site':'Farfetch',
            'crawl_date':date.today(),
            'url':response.url.split('?'),
            'subfolder':('' if response.url is None else response.url).split("/")[3],
            'portal_itemid':('' if response.url is None else response.url).split('?')[0].split('/')[-1].split('.')[0].split('-')[-1],
            'product_name':response.css('p.ltr-13ze6d5-Body.e1hhaa0c0::text').get(),
            'gender':('' if response.url is None else response.url).split('/')[5],
            'brand':response.xpath('//a[@data-ffref="pp_infobrd"]/text()').get(),
            'category': ('' if not breadcrumbs else breadcrumbs[2]),
            'subcategory':('' if not breadcrumbs else breadcrumbs[3]),
            'price':('' if price is None else price).split(' ')[-1],
            'currency':('' if price is None else price).split(' ')[0],
            'price_discount':response.css('div.ltr-zi04li.e12td3gj0>p.es58y7t0.ltr-1oyjj5-Footnote.e1ektl920::text').get(),
            'sold_out':response.css('p._2d473a._05a6bd::text').get(),
            'new':response.css('p.ltr-8h1fa5-Body.e3gfwc50::text').get(),
            'image_url':response.css('button.ltr-18eg0sl.e1g6ondk0>img::attr(src)').get(),
            }
        
        


