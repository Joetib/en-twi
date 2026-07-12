import json

with open("twi-data.json") as f:
    twi_data: dict[str, dict[str, dict[str, str]]] = json.load(f)


with open("KJV.json") as f:
    english_data: dict[str, dict[str, dict[str, str]]] = json.load(f)

with open("mapping.json") as f:
    mapping: dict[str, str] = json.load(f)
data = {}
for book, chapters in twi_data.items():
    english = mapping[book]
    english_book = english_data[english]
    data[english] = {}

    for chapter, verses in chapters.items():
        data[english][chapter] = {}
        for verse, text in verses.items():
            
            try:
                data[english][chapter][verse] = {
                "twi": text,
                "english": english_book[chapter][verse],
            }
            except Exception as e:
                print(e)
                print("Error: ", book, english, chapter, verse)


with open("final.json", "w") as f:
    json.dump(data, f)
