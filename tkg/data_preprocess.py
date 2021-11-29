import csv
from datetime import datetime

file_names = ["TKG_input_data.csv"]

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

all_events = []
for file_name in file_names:
    all_events.extend(parse_events(file_name))
all_events.sort(key = lambda x: int(x[3]))

print(all_events)

with open('data/entity2id.txt', 'w') as file:
    for key in entity_to_idx:
        file.write(key + '\t' + str(entity_to_idx[key]))
        file.write('\n')

with open('data/relation2id.txt', 'w') as file:
    for key in relation_to_idx:
        file.write(key + '\t' + str(relation_to_idx[key]))
        file.write('\n')

train = all_events[:int(len(all_events)*0.8)]
print(len(train))
print(train[-1])
dev = all_events[int(len(all_events)*0.8):int(len(all_events)*0.9)]
print(len(dev))
print(dev[0], dev[-1])
test = all_events[int(len(all_events)*0.9):]
print(len(test))
print(test[0])

with open('data/train.txt', 'w') as file:
    for instance in train:
        file.write(str(entity_to_idx[instance[0]]) + '\t' + str(relation_to_idx[instance[1]]) + '\t' + str(entity_to_idx[instance[2]]) + '\t' + str(instance[3]) + '\t' + '0')
        file.write('\n')

with open('data/valid.txt', 'w') as file:
    for instance in dev:
        file.write(str(entity_to_idx[instance[0]]) + '\t' + str(relation_to_idx[instance[1]]) + '\t' + str(entity_to_idx[instance[2]]) + '\t' + str(instance[3]) + '\t' + '0')
        file.write('\n')

with open('data/test.txt', 'w') as file:
    for instance in test:
        file.write(str(entity_to_idx[instance[0]]) + '\t' + str(relation_to_idx[instance[1]]) + '\t' + str(entity_to_idx[instance[2]]) + '\t' + str(instance[3]) + '\t' + '0')
        file.write('\n')
