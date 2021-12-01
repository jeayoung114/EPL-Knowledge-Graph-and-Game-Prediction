import pandas as pd
import fileinput
import json

world_game = pd.DataFrame()
with fileinput.input(files="game_worldfootball.jl") as file:
    for line in file:
        conv = json.loads(line)
        world_game = world_game.append(conv, ignore_index=True)
world_game.head()

def f(x):
    return str(x.season) + str(int(x["round"]) + 100)
world_game["time"] = world_game.apply(lambda x : f(x), axis = 1)

time_list = sorted(list(world_game["time"].drop_duplicates()))

time2idx = dict()
for idx, time in enumerate(time_list):
    time2idx[time] = idx

world_game["timestamp"] = world_game['time'].apply(lambda x : time2idx[x])
world_game = world_game.sort_values(by = "timestamp")[["timestamp", "home_team", "away_team", "score", "season", "round", "time"]]
world_game.to_csv("TKG_input_data.csv")

