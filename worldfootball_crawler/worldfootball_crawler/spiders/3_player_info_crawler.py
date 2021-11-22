import scrapy
import logging
import pandas as pd
import fileinput
import json
import re

class name_crawler(scrapy.Spider):
    name = "player_info"

    def __init__(self, date='', **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = ['http://www.worldfootball.net']
        seasons = [str(i) + "-" + str(i+1) for i in range(2009, 2021)]

        df = pd.DataFrame()
        with fileinput.input(
                files='./player_worldfootball.jl') as file:
            for line in file:
                conv = json.loads(line)
                df = df.append(conv, ignore_index=True)

        self.start_urls = list(df["player_url"].drop_duplicates())
        # self.start_urls = ["https://www.worldfootball.net/player_summary/darren-anderton/"]

        self.handle_httpstatus_list = [404]

    def parse(self, response):
        logging.info("response.status:%s" % response.status)
        res_dict = dict()

        club_history = dict()
        k = response.css("div[class='portfolio spec'] div[class='box']")[0]
        k = k.css("div[class='data'] tr")
        for idx, line in enumerate(k):
            try:
                l = line.css("tr ::text").getall()
                l = [re.sub("\t", "", i) for i in l]
                l = [re.sub("\n", "", i) for i in l]
                team_url = 'https://www.worldfootball.net' + line.css("a ::attr(href)").get()

                period = l[1]
                team = l[6]
                position = l[11]


                club_history[idx] = {"period" : period, "team" : team, "position" : position, "team_url" : team_url}
            except:
                continue

        res_dict["team_history"] = club_history




        res_dict["player_url"] = str(response).split("200 ")[1].split(">")[0]
        res = response.css("div[class='sidebar'] table[class='standard_tabelle yellow'] tr")
        name = response.css("div[class='sidebar'] div[class='box'] div[class='head'] h2[itemprop='name'] ::text").getall()[0].strip()
        res_dict["name"] = name

        for idx, post in enumerate(response.css("div[class='sidebar'] table[class='standard_tabelle yellow'] tr")):
            # print(post)
            tmp = post.css("::text").getall()
            tmp = [re.sub("[\n\t, :]", "", i) for i in tmp]
            if len(tmp) == 0:
                pass
            else:
                key_val = [i for i in tmp if i != ""]
                if key_val[1:] != []:
                    res_dict[key_val[0]] = key_val[1:]

            if idx == len(res)-1:
                yield res_dict