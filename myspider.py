import scrapy
import re


class MatchItem(scrapy.Item):
    result  = scrapy.Field() 
    team_score = scrapy.Field()
    rival_score = scrapy.Field()
    # diff
    htf = scrapy.Field()
    hta = scrapy.Field()
    rival_name = scrapy.Field()
    ground = scrapy.Field()
    date = scrapy.Field()
    team_id = scrapy.Field()
 

class BlogSpider(scrapy.Spider):

    name = 'blogspider'
    base_url = 'http://en.espn.co.uk/statsguru/rugby/team/{0}.html?class=1;spanmin1=01+Jan+2000;spanval1=span;template=results;type=team;view=results'
    start_urls = [base_url.format(i) for i in xrange(1,140)]

    def parse(self, response):
        sites = response.css('table.engineTable:nth-child(4) tr')[1:]

        for site in sites:
            item = MatchItem()
            item['result'] = site.xpath('td[1]/text()').extract()
            item['team_score'] = site.xpath('td[2]/text()').extract()
            item['rival_score'] = site.xpath('td[3]/text()').extract()
            item['htf'] = site.xpath('td[5]/text()').extract()
            item['hta'] = site.xpath('td[6]/text()').extract()
            item['rival_name'] = site.xpath('td[8]/text()').extract()
            item['ground'] = site.xpath('td[9]/a/text()').extract()
            item['date'] = site.xpath('td[10]/b/text()').extract()
            item['team_id'] = re.search('http://en.espn.co.uk/statsguru/rugby/team/{0}.html'.replace("{0}",'(?P<teamid>\d*)'), response.url).group('teamid')
            yield item

