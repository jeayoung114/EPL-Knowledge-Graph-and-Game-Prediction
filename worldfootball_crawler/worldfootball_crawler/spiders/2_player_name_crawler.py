import scrapy
import logging
import re

class name_crawler(scrapy.Spider):
    name = "player"

    def __init__(self, date='', **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = ['http://www.worldfootball.net']
        seasons = [str(i) + "-" + str(i+1) for i in range(2009, 2021)]
        self.start_urls = [
            "http://www.worldfootball.net/players_list/eng-premier-league-" + i + "/nach-name/" + str(j) for i in seasons for j in range(0,20)
        ]

        self.handle_httpstatus_list = [404]

    def parse(self, response):
        logging.info("response.status:%s" % response.status)
        for idx, post in enumerate(response.css("div[class='white'] table[class='standard_tabelle'] tr")):
            season = response.css("select option[selected='selected'] ::text").getall()[0]
            if idx != 0:
                print(post)
                name = post.css("td ::text").getall()[0].strip()
                player_url = 'https://www.worldfootball.net' + post.css("td a::attr(href)").getall()[0]
                team = post.css("td ::text").getall()[3]
                team_url = 'https://www.worldfootball.net' + post.css("td a::attr(href)").getall()[1]
                birth = post.css("td ::text").getall()[4]
                height = post.css("td ::text").getall()[5]
                pos = post.css("td ::text").getall()[6]

                yield {
                    'name' : name,
                    'player_url' : player_url,
                    'season' : season,
                    'team' : team,
                    'team_url' : team_url,
                    'DateOfBirth' : birth,
                    'height' : height,
                    'Position' : pos
                }
