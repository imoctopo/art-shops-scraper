import scrapy


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

    def parse(self, response):
        """Parse implementation."""
        for li in response.xpath('//div[@class="row sitemap col-xs-12"]/div[2]/ul/li/ul/li'):
            link = li.xpath('./a/@href').get()
            yield response.follow(link, callback=self.parse_category_view)

    def parse_category_view(self, response):
        """Parse products from the category's view."""
        for a in response.xpath('//div[@id="js-product-list"]//article//div[@class="product-description"]/h1/a'):
            link = a.xpath('./@href').get()
            yield response.follow(link, callback=self.parse_product_view, cb_kwargs={'url': link})

        next_page_link = response.xpath('//a[@class="next js-search-link"]/@href').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse_category_view)

    @staticmethod
    def parse_product_view(response, **kwargs):
        url = kwargs['url']
        name = response.xpath('//h1[@class="h1" and @itemprop="name"]/text()').get()
        price = response.xpath('//meta[@property="product:price:amount"]/@content').get()
        condition = response.xpath('//meta[@property="product:condition"]/@content').get()
        description = response.xpath('//div[@class="product-desc"]/p/text()').get()
        in_stock = True if response.xpath('//meta[@property="product:availability"]/@content').get() == 'In stock' else False
        brand = response.xpath('//meta[@property="product:brand"]/@content').get()
        sku = response.xpath('//span[@itemprop="sku"]/text()').get().replace('Cod: ', '')
        img_url = response.xpath('//meta[@property="og:image"]/@content').get()

        cats = []
        for li in response.xpath('//ol[@itemtype="http://schema.org/BreadcrumbList"]/li[position()>1 and position()<last()]'):
            cats.append(li.xpath('./a/span/text()').get())

        # Add the product's variables
        variables = []
        for tr in response.xpath('//div[@class="ctp_container"]/table/tbody/tr'):
            variables.append({
                'name': tr.xpath('.//td[last()-2]//span/text()').get(),
                'price': tr.xpath('.//td[@id="product_price_wt"]//span/text()').get().replace('$ ', '').replace('.', ''),
                'in_stock': True if tr.xpath('.//td[@class="ctp_quantity_input add_to_cart"]//div[@class="ctp_shopping_cart"]/text()').get() else False,
                'sku': tr.xpath('.//td[@id="reference"]//span/text()').get(),
            })

        data = {
            'name': name,
            'description': description,
            'url': url,
            'price': price,
            'condition': condition,
            'in_stock': in_stock,
            'brand': brand,
            'sku': sku,
            'img_url': img_url,
            'categories': cats
        }

        # If has variables, add them to the dict
        if variables:
            data['variables'] = variables

        yield data
