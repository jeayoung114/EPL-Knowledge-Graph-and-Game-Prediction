import scrapy
import logging
import pandas as pd
import fileinput
import json
import re

class name_crawler(scrapy.Spider):
    name = "team_info"

    def __init__(self, date='', **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = ['http://www.wikipedia.org/']
        seasons = [str(i) + "-" + str(i+1) for i in range(2000, 2021)]

        df = pd.DataFrame()
        with fileinput.input(
                files='../worldfootball_crawler/player_worldfootball.jl') as file:
            for line in file:
                conv = json.loads(line)
                df = df.append(conv, ignore_index=True)

        teams_original = list(df["team"].drop_duplicates())
        teams = [re.sub(" ", "_", i) for i in teams_original]
        self.start_urls = ["http://en.wikipedia.org/wiki/" + i for i in teams] + ["https://en.wikipedia.org/wiki/Crystal_Palace_F.C."]

        self.handle_httpstatus_list = [404]

    def parse(self, response):
        logging.info("response.status:%s" % response.status)
        res_dict = dict()
        res = response.css("div[class='mw-parser-output'] table[class='infobox vcard'] tr")
        name = response.css("div[class='mw-parser-output'] table[class='infobox vcard'] caption[class='infobox-title fn org'] ::text").get().strip()
        res_dict["name"] = name

        for idx, post in enumerate(response.css("div[class='mw-parser-output'] table[class='infobox vcard'] tr")):
            # print(post)
            tmp = post.css("::text").getall()
            tmp = [re.sub("[\n\t, :]", "", i) for i in tmp]
            if len(tmp) == 0:
                pass
            else:
                key_val = [i for i in tmp if i != "" and i != "[1]" and i != "[2]" and i != "[3]"]
                if key_val[1:] != []:
                    res_dict[key_val[0]] = key_val[1:]
                    if key_val[1:] == ["Clubwebsite"]:
                        res_dict[key_val[0]] = post.css("::attr(href)").get()
                    if key_val[0] == "Capacity":
                        if len(key_val)==2:
                            if "(" in key_val[1]:
                                key_val[1] = key_val[1].split("(")[0]
                        res_dict[key_val[0]] = key_val[1]
                    if key_val[0] == "Chairman":
                        res_dict[key_val[0]] = key_val[1]





            if idx == len(res)-1:
                yield res_dict