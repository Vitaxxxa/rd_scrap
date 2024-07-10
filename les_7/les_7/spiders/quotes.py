import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    
    max_count_follow = 1

    def parse(self, response):
        quotes = response.css('div.quote')

        for quote in quotes:
            text = quote.css('span.text::text').get()
            author = quote.css('small.author::text').get()

            yield {
                'text': text,
                'author': author
            }

        next_btn = response.css('li.next a::attr(href)').get()

        if next_btn and self.max_count_follow:
            self.max_count_follow -= 1
            yield response.follow(next_btn, callback=self.parse)