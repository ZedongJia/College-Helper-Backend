import py2neo
import json

LABELS = [
    "university", "person", "main_branch", "sub_branch", "major", "special"
]

_dict = []
mapper = {}

graph = py2neo.Graph("http://localhost:7474",
                     name="collegehelper-update",
                     password="hxm200307250693@")
for label in LABELS:
    cursor = graph.run("match (a:%s) return a.name" % label)
    data = cursor.data()
    for item in data:
        name = item["a.name"]
        _dict.append(name)
        mapper[name] = label

with open("./dict.txt", "w", encoding="utf8") as w:
    w.write("\n".join(_dict))

with open("./mapper.json", "w", encoding="utf8") as w:
    w.write(json.dumps(mapper))
