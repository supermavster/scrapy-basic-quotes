# RUN: rm quotes.json && scrapy crawl quotes -a top=3
import scrapy

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com'
    ]
    custom_settings = {
        'FEED_URI': './dist/quotes.json',
        'FEED_FORMAT': 'json',
        'CURRENT_REQUESTS': 24,
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': ['ingeniero.miguelvargas@gmail.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'PepitoPerez',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    
    def parse_only_quotes(self, response, **kwargs):
        if kwargs:
            # Generate new Quotes (Page)
            new_quotes = self.get_all_author_quotes(response)
            kwargs["quotes"].extend(new_quotes)
            # Get the new link
            next_page = self.get_next_link(response)
            if next_page:
                yield response.follow(
                    next_page,
                    callback=self.parse_only_quotes,
                    cb_kwargs=kwargs
                )
            else:
                yield kwargs
        

    def parse(self, response):
        # Basic Data
        title = self.get_title(response)
        quotes = self.get_all_author_quotes(response)
        top_tags = self.get_top_tags(response)

        # Get the new link
        next_page = self.get_next_link(response)
        if next_page:
            yield response.follow(next_page, callback=self.parse_only_quotes,
                cb_kwargs={
                    "title": title, 
                    "top_tags": top_tags,
                    "quotes": quotes
                }
        )

    # Complements (General)
    def get_title(self, response):
        return response.xpath('//h1/a/text()').get()

    def get_top_tags(self, response):
        ''' Generate Content -a [OPTION]\nOption: -a top=3 Get the first 3 of the top '''
        top_tags = response.xpath('//div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()').getall()
        # Add Params
        top = getattr(self, 'top', None)
        if top:
            top_tags = top_tags[:int(top)]
        return top_tags


    def get_all_quotes(self, response):
        return response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()

    def get_all_author(self, response):
        return response.xpath('//span/small[@class="author" and @itemprop="author"]/text()').getall()
    
    def get_all_author_quotes(self, response):
        quotes = self.get_all_quotes(response)
        authors = self.get_all_author(response)
        return [({'quote':value_one, 'author': value_two}) for value_one, value_two in zip(quotes, authors)]

    def get_next_link(self, response):
        return response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()