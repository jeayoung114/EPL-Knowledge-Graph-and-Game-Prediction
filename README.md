# EPL-Knowledge-Graph-and-Game-Prediction
DSCI558 Building Knowledge Graph Project

## 1. Crawler

### WorldFootball.net (https://www.worldfootball.net)

cd KG_generation/worldfootball_crawler
game: `scrapy crawl game -o game_worldfootball.jl'<br />
player_name: 'scrapy crawl player -o player_worldfootball.jl'<br />
player_info: 'scrapy crawl player_info -o player_info_worldfootball.jl'<br />
team_info: 'scrapy crawl team_info -o team_info_worldfootball.jl'<br />

### Whoscored.com
cd ../whoscored_crawler<br />
run whoscored_Crawler.ipynb

### Wikipedia
cd ../wikipedia_crawler<br />
scrapy crawl team_info team_info_wikipedia.jl


## 2. Entity Resolution

cd ../Entity Resolution<br />
run 1. [Player Entity Resolution.ipynb](https://github.com/jeayoung114/EPL-Knowledge-Graph-and-Game-Prediction/blob/main/KG_generation/Entity%20Resolution/1.%20Player%20Entity%20Resolution.ipynb)<br />
run 2. [Player PSL.ipynb](https://github.com/jeayoung114/EPL-Knowledge-Graph-and-Game-Prediction/blob/main/KG_generation/Entity%20Resolution/2.%20Player%20PSL.ipynb)<br />
run 3. [Team Entity Resolution.ipynb](https://github.com/jeayoung114/EPL-Knowledge-Graph-and-Game-Prediction/blob/main/KG_generation/Entity%20Resolution/3.%20Team%20Entity%20Resolution.ipynb)<br />
run 4. [Game Entity Resolution.ipynb](https://github.com/jeayoung114/EPL-Knowledge-Graph-and-Game-Prediction/blob/main/KG_generation/Entity%20Resolution/4.%20Game%20Entity%20Resolution.ipynb)<br />

## 3. KG Construction

cd ../KG Construction<br />
run 5. [KG Construction.ipynb](https://github.com/jeayoung114/EPL-Knowledge-Graph-and-Game-Prediction/blob/main/KG_generation/KG%20Construction/5.%20KG%20Construction.ipynb)


## 4. Neo4j

1. Install Neo4j Desktop -- w/ Neosemantics Plugin.
2. Upload RDF file (data.ttl) into Neo4J desktop.
3. Run Neo4J desktop.

```
DATABASE_USERNAME="neo4j"
DATABASE_PASSWORD="dsci558!"
DATABASE_URL="bolt://localhost:7687"
```

## 5. Flask

```
cd backend
conda create -n neo4j python=3.7
conda activate neo4j
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```
```
FLASK_URL="http://localhost:5000"
```

## 6. Frontend
```
npm install
npm run serve
```

## 5. Contributor
  - 1. Jae Young Kim : [jkim2458@usc.edu]
  - 2. Dong Ho Lee : [dongho.lee@usc.edu]

