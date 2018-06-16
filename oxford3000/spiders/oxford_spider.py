import scrapy


class OxfordSpider(scrapy.Spider):
    name = "oxford"
    entry_url = 'https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_'
    word_url = 'https://www.oxfordlearnersdictionaries.com/definition/english/'

    def start_requests(self):
        url = 'https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/'
        yield scrapy.Request(url=url, callback=self.parse_entry)

    def parse_entry(self, response):
        for entry in response.css('.hide_phone li'):
            entry_name = entry.css('::text').extract()[0]
            entry_page = self.entry_url + entry_name + '/'
            yield scrapy.Request(entry_page, callback=self.parse_words)

    def parse_words(self, response):
        if response.css('.paging_links li:last-child a::text').extract()[0] == '>':
            next_page = response.css('.paging_links li:last-child a::attr(href)').extract_first()
            yield scrapy.Request(next_page, callback=self.parse_words)

        for word in response.css('.wordlist-oxford3000 li'):
            word_page = self.word_url + word.css('::text').extract()[1]
            yield scrapy.Request(word_page, callback=self.parse_word)

    def parse_word(self, response):
        yield {
            'word': response.css('h2.h::text').extract()[0],
            'description': response.css('#entryContent').extract(),
            'nearby_words': response.css('.nearby').extract(),
        }
