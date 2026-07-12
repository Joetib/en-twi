from pathlib import Path
import json

base_dir = Path(__file__).parent / "TWI-BIBLE"


def fetch_filenames():
    data = []
    for file in base_dir.glob("*.txt"):
        data.append(file.name.split(".txt")[0])

    with open("filenames.json", "w") as f:
        json.dump(data, f)


def parse_chapter(filename: Path):
    with open(filename, "r") as f:
        lines = f.readlines()
    data = {}
    verse: int = 0
    for line in lines:
        if line.startswith("///"):
            verse = line.split(":")[-1].strip()
        elif line:
            if verse not in data:
                data[verse] = line.strip()
            else:
                data[verse] += line.strip()
            
    return data


def parse_files():
    data = {}
    for file in base_dir.glob("*.txt"):
        filename = file.name.split(".txt")[0]
        parts = filename.split(" ")
        chapter = parts.pop()
        book = " ".join(parts)

        if book not in data:
            data[book] = {}
        data[book][chapter] = parse_chapter(file)

    with open("twi-data.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    parse_files()
