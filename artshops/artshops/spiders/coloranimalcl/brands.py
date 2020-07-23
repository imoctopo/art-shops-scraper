import scrapy
from slugify import slugify


class BrandsSpider(scrapy.Spider):
    name = 'coloranimal.brands'
    allowed_domains = ['coloranimal.cl']
    start_urls = [
        'https://www.coloranimal.cl/mapa%20del%20sitio'
    ]
    custom_settings = {
        'USER_AGENT': 'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'FEED_URI': f'{name}.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'MEMUSAGE_LIMIT_MB': 512
    }

    def parse(self, response):
        """Parse implementation"""
        for li in response.xpath('//a[@id="manufacturer-page"]/../ul/li[position()>1]'):
            print(li.xpath('./a/@href').get())
            brand = {
                'name': li.xpath('normalize-space(./a/text())').get(),
                'slug': slugify(li.xpath('./a/text()').get(), to_lower=True),
                'url': li.xpath('./a/@href').get(),
            }
            yield brand
