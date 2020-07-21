import scrapy
from slugify import slugify


class CategoriesSpider(scrapy.Spider):
    name = 'coloranimal.categories'
    start_urls = [
        'https://www.coloranimal.cl/mapa%20del%20sitio'
    ]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
        'FEED_URI': f'{name}.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'MEMUSAGE_LIMIT_MB': 2048
    }

    def parse(self, response):
        """Parse implementation"""
        for li in response.xpath('//div[@class="row sitemap col-xs-12"]/div[2]/ul/li/ul/li'):
            print(li.xpath('./a/@href').get())
            cat = {
                'name': li.xpath('normalize-space(./a/text())').get(),
                'slug': slugify(li.xpath('./a/text()').get(), to_lower=True),
                'url': li.xpath('./a/@href').get(),
            }
            # If the "li" element has an "ul" element as next node, extracts the children categories
            if li.xpath('./ul/li'):
                cat['children'] = self.parse_children(li)
            yield cat

    def parse_children(self, category):
        """Extract category's children recursively"""
        data = []
        cat_children = category.xpath('./ul/li')
        for li in cat_children:
            obj = {
                'name': li.xpath('normalize-space(./a/text())').get(),
                'slug': slugify(li.xpath('./a/text()').get(), to_lower=True),
                'url': li.xpath('./a/@href').get(),
            }
            # If the "li" element has an "ul" element as next node, extracts the children categories recursively
            if li.xpath('./ul/li'):
                obj['children'] = self.parse_children(li)
            data.append(obj)
        return data
