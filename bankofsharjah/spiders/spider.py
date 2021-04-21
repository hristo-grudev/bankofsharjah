import datetime

import scrapy

from scrapy.loader import ItemLoader

from ..items import BankofsharjahItem
from itemloaders.processors import TakeFirst
base = 'https://www.bankofsharjah.com/en/news/lists/latest-news/{}'


class BankofsharjahSpider(scrapy.Spider):
	name = 'bankofsharjah'
	year = 2013
	start_urls = [base.format(year)]

	def parse(self, response):
		post_links = response.xpath('//div[@class="news-list"]//a[@class="more"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if self.year < datetime.datetime.now().year:
			self.year += 1
			yield response.follow(base.format(self.year), self.parse)


	def parse_post(self, response):
		if 'pdf' in response.url:
			return
		title = response.xpath('//h2[@class="col-blue4"]/text()').get()
		description = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "news-list", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg-9", " " ))]//text()[normalize-space() and not(ancestor::small)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//small[@class="date"]/text()').get().split(':')[1]

		item = ItemLoader(item=BankofsharjahItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
