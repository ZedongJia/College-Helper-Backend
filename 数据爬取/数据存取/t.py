import json
with open('./data/t.json') as r:
    data = json.load(r)[0]
print(data)