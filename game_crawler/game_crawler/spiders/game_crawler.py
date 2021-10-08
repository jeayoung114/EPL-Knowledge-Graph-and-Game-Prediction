import scrapy
import logging
import re

class name_crawler(scrapy.Spider):
    name = "game"

    def __init__(self, date='', **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = ['http://www.worldfootball.net']
        seasons = [str(i) + "-" + str(i+1) for i in range(2000, 2021)]
        rounds = [i for i in range(40)]
        # self.start_urls = [
        #     "https://www.worldfootball.net/schedule/eng-premier-league-2000-2001-spieltag/1/"
        # ]
        self.start_urls = [
            "https://www.worldfootball.net/schedule/eng-premier-league-" + i + "-spieltag/" + str(j) for i in seasons for j in rounds
        ]

        self.handle_httpstatus_list = [404]

    def parse(self, response):
        logging.info("response.status:%s" % response.status)
        tmp = response.css("div[class='box'] table[class='standard_tabelle']")[0]
        #for idx, post in enumerate(response.css("div[class='box'] table[class='standard_tabelle'] tr")):
        for idx, post in enumerate(tmp.css("tr")):
            selected = response.css("select option[selected='selected'] ::text").getall()
            season = selected[0]
            round = re.sub("[^0-9]", "", selected[1])
            line = post.css("td ::text").getall()
            if len(line) == 13:
                date = line[0]
                time = line[1]
                home_team = line[3]
                away_team = line[7]
                score = line[10].split(" ")[0]
            if len(line) == 12:
                time = line[0]
                home_team = line[2]
                away_team = line[6]
                score = line[9].split(" ")[0]

            yield {
                'season': season,
                'round' : round,
                'date' : date,
                'time' : time,
                'home_team': home_team,
                'away_team': away_team,
                'score': score
            }
