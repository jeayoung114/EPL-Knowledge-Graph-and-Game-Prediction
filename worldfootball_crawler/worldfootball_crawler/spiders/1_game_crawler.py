import scrapy
import logging
import re

class name_crawler(scrapy.Spider):
    name = "game"

    def __init__(self, date='', **kwargs):
        super().__init__(**kwargs)
        self.allowed_domain = ['http://www.worldfootball.net']
        seasons = [str(i) + "-" + str(i+1) for i in range(2009, 2021)]
        rounds = [i for i in range(40)]
        # self.start_urls = [
            #     "https://www.worldfootball.net/schedule/eng-premier-league-2000-2001-spieltag/1/"
        # ]
        self.start_urls = [
            "https://www.worldfootball.net/schedule/eng-premier-league-" + i + "-spieltag/" + str(j) for i in seasons for j in rounds
        ]

        self.handle_httpstatus_list = [404]

    def parse(self, response):
        res_dict = dict()
        logging.info("response.status:%s" % response.status)
        tmp = response.css("div[class='box'] table[class='standard_tabelle']")[0]
        #for idx, post in enumerate(response.css("div[class='box'] table[class='standard_tabelle'] tr")):
        for idx, post in enumerate(tmp.css("tr")):
            selected = response.css("select option[selected='selected'] ::text").getall()
            season = selected[0]
            round = re.sub("[^0-9]", "", selected[1])
            line = post.css("td ::text").getall()
            url = "https://www.worldfootball.net" + post.css("td a ::attr(href)").getall()[-1]
            print(url)
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

            request = scrapy.Request(url, callback=self.game_info_page, dont_filter=True)
            request.meta['season'] = season
            request.meta['round'] = round
            request.meta['date'] = date
            request.meta['time'] = time
            request.meta['home_team'] = home_team
            request.meta['away_team'] = away_team
            request.meta['score'] = score

            yield request

    def game_info_page(self, response):
        res_dict = dict()
        res_dict["season"] = response.meta['season']
        res_dict["round"] = response.meta['round']
        res_dict["data"] = response.meta['date']
        res_dict["time"] = response.meta['time']
        res_dict["home_team"] = response.meta['home_team']
        res_dict["away_team"] = response.meta['away_team']
        res_dict["score"] = response.meta['score']


        tmp = response.css("table[class = 'standard_tabelle']")[1]
        goal_player = tmp.css("td ::text").getall()
        goal_player = [i for i in goal_player if "\t" not in i and i[0] not in "0123456789"][1:]

        if goal_player[0] == "none":
            goal_player = []
        res_dict["goal_player"] = goal_player

        goal_player_urls = tmp.css("td a ::attr(href)").getall()
        goal_player_urls = ["https://www.worldfootball.net" + i for i in goal_player_urls]
        res_dict["goal_player_url"] = goal_player_urls

        tmp = response.css("table[class = 'standard_tabelle']")[2]
        tmp = tmp.css("tr")
        home_team_players = []
        for player in tmp:
            try:
                player_list = player.css("td ::text").getall()
                player_list = [i for i in player_list if '\t' not in i and '\n' not in i]
                if re.sub("[0-9]", "", player_list[0]) == "":
                    player_number = player_list[0]
                    player_name = player_list[1]
                else:
                    player_number = ""
                    player_name = player_list[0]
                player_url = "https://www.worldfootball.net" + player.css("td a ::attr(href)").getall()[0]
                home_team_players.append({'player_number' : player_number, 'player_name' : player_name, 'player_url' : player_url})
            except:
                continue
        res_dict["home_team_players"] = home_team_players


        tmp = response.css("table[class = 'standard_tabelle']")[3]
        tmp = tmp.css("tr")
        away_team_players = []
        for player in tmp:
            try:
                player_list = player.css("td ::text").getall()
                player_list = [i for i in player_list if '\t' not in i and '\n' not in i]
                if re.sub("[0-9]", "", player_list[0]) == "":
                    player_number = player_list[0]
                    player_name = player_list[1]
                else:
                    player_number = ""
                    player_name = player_list[0]
                player_url = "https://www.worldfootball.net" + player.css("td a ::attr(href)").getall()[0]
                away_team_players.append({'player_number' : player_number, 'player_name' : player_name, 'player_url' : player_url})
            except:
                continue
        res_dict["away_team_players"] = away_team_players

        tmp = response.css("table[class = 'standard_tabelle']")[4]
        tmp = tmp.css("td")
        home_team_manager = tmp[0].css("b ::text").getall()[1]
        home_team_manager_url = "https://www.worldfootball.net" + tmp[0].css("b ::attr(href)").get()
        away_team_manager = tmp[1].css("b ::text").getall()[1]
        away_team_manager_url = "https://www.worldfootball.net" + tmp[1].css("b ::attr(href)").get()
        res_dict["home_team_manager"] = home_team_manager
        res_dict["home_team_manager_url"] = home_team_manager_url
        res_dict["away_team_manager"] = away_team_manager
        res_dict["away_team_manager_url"] = away_team_manager_url




        tmp = response.css("table[class = 'standard_tabelle']")[-1]
        stadium_url = "https://www.worldfootball.net" + tmp.css("a ::attr(href)").getall()[0]
        refree_url = "https://www.worldfootball.net" + tmp.css("a ::attr(href)").getall()[1]
        k = tmp.css("td ::text").getall()[2]
        num_audience = re.sub("[\n\t.]", "", k)
        tmp = tmp.css("::text").getall()
        tmp = [i for i in tmp if "\t" not in i]
        stadium = tmp[0]
        stadium_country = re.sub("[()]", "", tmp[1]).strip()
        refree_name = tmp[2]
        refree_country = re.sub("[()]", "", tmp[3]).strip()

        res_dict["stadium"] = stadium
        res_dict["stadium_country"] = stadium_country
        res_dict["stadium_url"] = stadium_url
        res_dict["refree_name"] = refree_name
        res_dict["refree_country"] = refree_country
        res_dict["refree_url"] = refree_url
        res_dict["num_audience"] = num_audience




        yield res_dict












