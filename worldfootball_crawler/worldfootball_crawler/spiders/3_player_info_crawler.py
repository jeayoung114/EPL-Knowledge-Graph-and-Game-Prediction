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
        seasons = [str(i) + "-" + str(i+1) for i in range(2000, 2021)]

        df = pd.DataFrame()
        with fileinput.input(
                files='/Users/jaeyoungkim/Desktop/usc/DSCI - 558/project/github/Untitled/worldfootball_crawler/player_worldfootball.jl') as file:
            for line in file:
                conv = json.loads(line)
                df = df.append(conv, ignore_index=True)

        self.start_urls = list(df["player_url"].drop_duplicates())
        # self.start_urls = ["https://www.worldfootball.net/player_summary/darren-anderton/"]

        self.handle_httpstatus_list = [404]

    def parse(self, response):
        logging.info("response.status:%s" % response.status)
        res_dict = dict()
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