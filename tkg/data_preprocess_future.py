import csv
from datetime import datetime

file_names = ["TKG_input_data.csv", "TKG_future_data.csv"]

relation_to_idx = {}
entity_to_idx = {}
def parse_events(file_name):
    events = []
    with open(file_name, newline='') as csvfile:
        eventreader = csv.DictReader(csvfile)
        for row in eventreader:
            if len(row['score'].split(':')) != 2:
                continue

            if row['score'].split(':')[0] > row['score'].split(':')[1]:
                relation = 'win'
            elif row['score'].split(':')[0] == row['score'].split(':')[1]:
                relation = 'draw'
            else:
                relation = 'lose'

            if relation not in relation_to_idx:
                relation_to_idx[relation] = len(relation_to_idx.keys())
            if row['home_team'] not in entity_to_idx:
                entity_to_idx[row['home_team']] = len(entity_to_idx.keys())
            if row['away_team'] not in entity_to_idx:
                entity_to_idx[row['away_team']] = len(entity_to_idx.keys())

            events.append((row['home_team'], relation, row['away_team'], row['timestamp']))

    return events

def parse_events_infer(file_name):
    events = []
    with open(file_name, newline='') as csvfile:
        eventreader = csv.DictReader(csvfile)
        for row in eventreader:
            if row['home_team'] not in entity_to_idx:
                entity_to_idx[row['home_team']] = len(entity_to_idx.keys())
            if row['away_team'] not in entity_to_idx:
                entity_to_idx[row['away_team']] = len(entity_to_idx.keys())

            events.append((row['home_team'], 'win', row['away_team'], row['timestamp']))
            events.append((row['home_team'], 'lose', row['away_team'], row['timestamp']))
            events.append((row['home_team'], 'draw', row['away_team'], row['timestamp']))

    return events

train_events = parse_events(file_names[0])
infer_events = parse_events_infer(file_names[1])

train_events.sort(key = lambda x: int(x[3]))
infer_events.sort(key = lambda x: int(x[3]))


with open('infer_data/entity2id.txt', 'w') as file:
    for key in entity_to_idx:
        file.write(key + '\t' + str(entity_to_idx[key]))
        file.write('\n')

with open('infer_data/relation2id.txt', 'w') as file:
    for key in relation_to_idx:
        file.write(key + '\t' + str(relation_to_idx[key]))
        file.write('\n')

train = train_events[:int(len(train_events)*0.9)]
dev = train_events[int(len(train_events)*0.9):]

with open('infer_data/train.txt', 'w') as file:
    for instance in train:
        file.write(str(entity_to_idx[instance[0]]) + '\t' + str(relation_to_idx[instance[1]]) + '\t' + str(entity_to_idx[instance[2]]) + '\t' + str(instance[3]) + '\t' + '0')
        file.write('\n')

with open('infer_data/valid.txt', 'w') as file:
    for instance in dev:
        file.write(str(entity_to_idx[instance[0]]) + '\t' + str(relation_to_idx[instance[1]]) + '\t' + str(entity_to_idx[instance[2]]) + '\t' + str(instance[3]) + '\t' + '0')
        file.write('\n')

with open('infer_data/test.txt', 'w') as file:
    for instance in infer_events:
        file.write(str(entity_to_idx[instance[0]]) + '\t' + str(relation_to_idx[instance[1]]) + '\t' + str(entity_to_idx[instance[2]]) + '\t' + str(instance[3]) + '\t' + '0')
        file.write('\n')
