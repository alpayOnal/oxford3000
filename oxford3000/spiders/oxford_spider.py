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

        definitions = []
        for details in response.css('.sn-g'):
            sentences = details.css('.x-g ::text').extract()
            sentences = [sentence for sentence in sentences if sentence.split() != u' ']
            definitions.append({
                'def': details.css('.def::text').extract(),
                'sentences': sentences
            })

        examples = []
        for item in response.css('span[title="Extra examples"] .x'):
            examples.append(item.css('::text').extract()[0])

        nearby_words = []
        for item in response.css('.nearby .hwd'):
            if len(item.css('::text').extract()) > 0 and len(item.css('pos::text').extract()) > 0:
                nearby_words.append({
                    'word': item.css('::text').extract()[0],
                    'type': item.css('pos::text').extract()[0]
                })

        parsed_word = {
            'word': response.css('h2.h::text').extract()[0],
            'word_origin': " ".join(response.css('span[title="Word Origin"] .p::text').extract()),
            'nearby_words': nearby_words,
            'pron_us': response.css('div.pron-us::attr(data-src-mp3)').extract()[0],
            'pron_uk': response.css('div.pron-uk::attr(data-src-mp3)').extract()[0],
            'examples': examples,
            'definitions': definitions,
            'type': response.css('.pos::text').extract()[0]
        }

        yield parsed_word
