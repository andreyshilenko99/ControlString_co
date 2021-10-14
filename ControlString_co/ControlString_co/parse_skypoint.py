import json

with open('log-2021-10-12.txt', 'r') as reader:
    file = reader.readlines()
    for line in file:
        d = json.loads(line)
        print(d)