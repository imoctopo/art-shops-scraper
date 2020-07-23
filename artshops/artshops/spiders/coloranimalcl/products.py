import scrapy
from slugify import slugify


class ProductsSpider(scrapy.Spider):
    """Scraps products, starting for the category's view page followed from sitemap's page."""
    name = 'coloranimal.products'
    start_urls = [
        'https://www.coloranimal.cl/mapa%20del%20sitio'
    ]
    handle_httpstatus_list = [500]
    custom_settings = {
        'USER_AGENT': 'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'FEED_URI': f'{name}.json',
        'FEED_FORMAT': 'json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'MEMUSAGE_LIMIT_MB': 1024,
        'HTTPERROR_ALLOWED_CODES': [500],
    }
    counter = 0

    def parse(self, response):
        """Parse implementation."""
        for li in response.xpath('//div[@class="row sitemap col-xs-12"]/div[2]/ul/li/ul/li'):
            link = li.xpath('./a/@href').get()
            yield response.follow(link, callback=self.parse_category_view)

    def parse_category_view(self, response):
        """Parse products from the category's view."""
        for a in response.xpath('//div[@id="js-product-list"]//article//div[@class="product-description"]/h1/a')[:3]:
            link = a.xpath('./@href').get()
            yield response.follow(link, callback=self.parse_product_view, cb_kwargs={'url': link})

        next_page_link = response.xpath('//a[@class="next js-search-link"]/@href').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse_category_view)

    def parse_product_view(self, response, **kwargs):
        url = kwargs['url']
        name = response.xpath('//h1[@class="h1" and @itemprop="name"]/text()').get()
        price = response.xpath('//div[@class="current-price"]/span/text()').get().replace('$ ', '')
        description = response.xpath('//div[@class="product-desc"]/p/text()').get()
        in_stock = response.xpath('//link[@itemprop="availability"]/@href').get()

        self.counter += 1
        print('*' * 20)
        print(self.counter)
        print('*' * 20)

        yield {
            'name': name,
            'description': description,
            'url': url,
            'price': price,
            'in_stock': in_stock,
        }
