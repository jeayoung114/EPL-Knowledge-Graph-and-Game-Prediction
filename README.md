# EPL-Knowledge-Graph-and-Game-Prediction
DSCI558 Building Knowledge Graph Project

## 1. Crawler

### WorldFootball.net (https://www.worldfootball.net)
game: `scrapy crawl game -o game_worldfootball.jl'<br />
player_name: 'scrapy crawl player -o player_worldfootball.jl'<br />
player_info: 'scrapy crawl player_info -o player_info_worldfootball.jl'<br />
team_info: 'scrapy crawl team_info -o team_info_worldfootball.jl'<br />


## 2. Neo4j

1. Install Neo4j Desktop -- w/ Neosemantics Plugin.
2. Upload RDF file (data.ttl) into Neo4J desktop.
3. Run Neo4J desktop.

```
DATABASE_USERNAME="neo4j"
DATABASE_PASSWORD="dsci558!"
DATABASE_URL="bolt://localhost:7687"
```

## 3. Flask

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

## 4. Frontend


## 5. Contributor
  - 1. Jae Young Kim : [jkim2458@usc.edu]
  - 2. Dong Ho Lee : [dongho.lee@usc.edu]

