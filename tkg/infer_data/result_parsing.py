# 4835,469,Liverpool FC,Aston Villa,lose,2021/2022,16
# timestamp,home_team,away_team,score,season,round
entity_id_dict = {}
relation_id_dict = {}

entity_id = open('entity2id.txt', 'r')
relation_id = open('relation2id.txt', 'r')

for line in entity_id.readlines():
    entity_id_dict[line.split('\t')[1].strip()] = line.split('\t')[0]

for line in relation_id.readlines():
    relation_id_dict[line.split('\t')[1].strip()] = line.split('\t')[0]

print(entity_id_dict)
print(relation_id_dict)

result_file = open('result.txt', 'r')

import csv
f = open("future.csv", "w")
writer = csv.DictWriter(f, fieldnames=["timestamp", "home_team", "away_team", "score"])

for line in result_file.readlines():
    elements = line.split('\t')

    writer.writerow({
        'timestamp': int(elements[3].strip()),
        'home_team': entity_id_dict[elements[0]],
        'away_team': entity_id_dict[elements[2]],
        'score': relation_id_dict[elements[1]],
    })

    print(line.split('\t'))
