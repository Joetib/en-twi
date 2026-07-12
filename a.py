import json
with open("KJV.json", "r") as f:
    data = json.load(f)

with open("english.json", "w") as f:
    json.dump(list(data.keys()), f)
