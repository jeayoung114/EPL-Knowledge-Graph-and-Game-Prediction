import scrapy
import logging
import re

class name_crawler(scrapy.Spider):
    name = "player"

    def __init__(self, date='', **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = ['http://www.worldfootball.net']
        self.start_urls = [
            "http://www.worldfootball.net/players_list/eng-premier-league-2000-2001/nach-name/1",
            "http://www.worldfootball.net/players_list/eng-premier-league-2000-2001/nach-name/2"

        ]
        self.handle_httpstatus_list = [404]

    def parse(self, response):
        logging.info("response.status:%s" % response.status)
        for idx, post in enumerate(response.css("div[class='white'] table[class='standard_tabelle'] tr")):
            if idx != 0:
                print(post)
                name = post.css("td ::text").getall()[0].strip()
                team = post.css("td ::text").getall()[3]
                birth = post.css("td ::text").getall()[4]
                height = post.css("td ::text").getall()[5]
                pos = post.css("td ::text").getall()[6]

                yield {
                    'name' : name,
                    'team' : team,
                    'DateOfBirth' : birth,
                    'height' : height,
                    'Position' : pos
                }
