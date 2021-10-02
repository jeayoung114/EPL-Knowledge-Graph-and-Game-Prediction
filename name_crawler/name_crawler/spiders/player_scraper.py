import scrapy
import re

class name_crawler(scrapy.Spider):
    name = "player"

    start_urls = [
        "https://www.worldfootball.net/players_list/eng-premier-league-2000-2001/nach-name/1/"
        "https://www.worldfootball.net/players_list/eng-premier-league-2000-2001/nach-name/2"
    ]


    def parse(self, response):
        for post in response.css("div[class='white'] table[class='standard_tabelle']"):
            name = post.css("td[nowrap] ::text").get()
            team = post.css("td ::text")[3].get()
            birth = post.css("td ::text")[4].get()
            height = post.css("td ::text")[5].get()
            pos = post.css("td ::text")[6].get()

            yield{
                'name' : name,
                'team' : team,
                'DateOfBirth' : birth,
                'height' : height,
                'Position' : pos
            }