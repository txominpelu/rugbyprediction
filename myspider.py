import scrapy
import re
import urllib2
import json


class MatchItem(scrapy.Item):
    result  = scrapy.Field() 
    # diff
    htf = scrapy.Field()
    hta = scrapy.Field()
    ground = scrapy.Field()
    date = scrapy.Field()
    gameId = scrapy.Field()
    league = scrapy.Field()
    home_name = scrapy.Field()
    home_id = scrapy.Field()
    home_score = scrapy.Field()
    away_name = scrapy.Field()
    away_score = scrapy.Field()
    away_id = scrapy.Field()
    competition_name = scrapy.Field()
 

class BlogSpider(scrapy.Spider):

    name = 'blogspider'
    base_url = 'http://en.espn.co.uk/statsguru/rugby/team/{0}.html?class=1;spanmin1=01+Jan+2000;spanval1=span;template=results;type=team;view=results'
    start_urls = [base_url.format(i) for i in xrange(1,140)]

    def parse(self, response):
        sites = response.css('table.engineTable:nth-child(4) tr')[1:]

        for site in sites:
            item = MatchItem()
            item['result'] = site.xpath('td[1]/text()').extract()
            item['htf'] = site.xpath('td[5]/text()').extract()[0]
            item['hta'] = site.xpath('td[6]/text()').extract()[0]
            item['ground'] = site.xpath('td[9]/a/text()').extract()[0]
            item['date'] = site.xpath('td[10]/b/text()').extract()[0]
	    match_details_url = site.xpath('td[11]/a/@href').extract()[0]
	    yield scrapy.Request(response.urljoin(match_details_url), lambda x: self.extract_match_api_url(site, x), meta={'item':item} )

    def extract_match_api_url(self, site, response):
	item = MatchItem(response.meta["item"])
	m = re.search("gameId=(?P<game>\d*)&league=(?P<league>\d*)",response.url)
	url = 'http://site.api.espn.com/apis/site/v2/sports/rugby/{0}/summary?event={1}'.format(m.group('league'),m.group('game'))
	yield scrapy.Request(url, self.parse_match, meta={'item':item} )

    def parse_team(self, json, item, prefix):
        item["{0}_name".format(prefix)] = json['team']['displayName']
        item["{0}_id".format(prefix)] = json['team']['id']
        item["{0}_score".format(prefix)] = json['score']
        return item

    def parse_match(self, response):
	item = MatchItem(response.meta["item"])
	js = json.loads(response.body_as_unicode())
	competitors = js['header']['competitions'][0]['competitors']
	item = self.parse_team([ t for t in competitors if t['homeAway'] == 'home'][0], item, "home")
	item = self.parse_team([ t for t in competitors if t['homeAway'] != 'home'][0], item, "away")
	item['gameId'] = js['header']['id']
	item['league'] = js['header']['league']['id']
	item['competition_name'] = js['header']['league']['abbreviation']
	yield item

