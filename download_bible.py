import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor

base_url = "https://www.bible.com/_next/data/xSqbM9AC5EIJiwhJy4ifB/en/audio-bible/59/{book}.{chapter}.{prefix}.json?versionId=59&usfm={book}.{chapter}.{prefix}"
# base_url = "https://www.bible.com/_next/data/pvT9iWj6ikw5-xN880q1-/en/bible/59/{book}.{chapter}.{prefix}.json?versionId=59&usfm={book}.{chapter}.{prefix}"
books_of_the_bible = [
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
]

# Creating a list of the first three letters of each book, capitalized
books_short = [book.replace(" ", "")[:3].upper() for book in books_of_the_bible]

print(books_short)
base_prefix = "ASW"


def download(book, chapter, prefix):
    response = requests.get(base_url.format(book=book, chapter=chapter, prefix=prefix))
    if response.status_code == 404:
        print("404 Error downloading %s.%s.%s" % (book, chapter, prefix))
        return False
    data = response.json()
    if not data.get("pageProps", {}).get("chapterInfo"):
        print("No chapter info found, exiting. empty chapter.%s.%s.%s" % (book, chapter, prefix))
        return False
    if response.status_code == 200:
        with open(f"./twi/bibles/{prefix}/{book}.{chapter}.{prefix}.json", "w") as f:
            json.dump(response.json(), f)
    else:
        print(f"Failed to download {book}.{chapter}.{prefix}")

    return True


def download_book(
    book,
):
    for i in range(1, 600):
        results = download(book, i, base_prefix)
        if not results:
            break


def download_all(prefix=base_prefix):
    try:
        os.mkdir(
            f"./twi/bibles/{prefix}",
        )
    except:
        pass

    with ThreadPoolExecutor(max_workers=24) as executor:
        results = executor.map(
            download_book,
            books_short,
        )
        for i in results:
            print(i)


download_all()
