import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor

# base_url = "https://www.bible.com/audio-bible/1861/{book}.{chapter}.{prefix}.json?versionId=1861&usfm={book}.{chapter}.{prefix}"
# base_url = "https://www.bible.com/_next/data/pvT9iWj6ikw5-xN880q1-/en/bible/59/{book}.{chapter}.{prefix}.json?versionId=59&usfm={book}.{chapter}.{prefix}"

base_url = "https://www.bible.com/_next/data/9su_rXNs9ssXM9qYjdWxG/en/audio-bible/1861/{book}.{chapter}.{prefix}.json?versionId=1861&usfm={book}.{chapter}.{prefix}"
other_url = "https://www.bible.com/_next/data/9su_rXNs9ssXM9qYjdWxG/en/audio-bible/1461/{book}.{chapter}.{prefix}.json?versionId=1461&usfm={book}.{chapter}.{prefix}"
other_url_2 = "https://www.bible.com/_next/data/9su_rXNs9ssXM9qYjdWxG/en/audio-bible/2094/{book}.{chapter}.{prefix}.json?versionId=2094&usfm={book}.{chapter}.{prefix}.ASNA"
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


TWI_NAME_MAPPING = {
    "Gyenesis": "GEN",
    "Eksodɔs": "EXO",
    "Lewitikɔs": "LEV",
    "Numeri": "NUM",
    "Deuteronomium": "DEU",
    "Yosua": "JOS",
    "Atemmufoɔ": "JDG",
    "Rut": "RUT",
    "1 Samuel": "1SA",
    "2 Samuel": "2SA",
    "1 Ahemfo": "1KI",
    "2 Ahemfo": "2KI",
    "1 Berɛsosɛm": "1CH",
    "2 Berɛsosɛm": "2CH",
    "Esra": "EZR",
    "Nehemia": "NEH",
    "Ester": "EST",
    "Hiob": "JOB",
    "Nnwom": "PSA",
    "Mmebusɛm": "PRO",
    "Ɔsɛnkafoɔ": "ECC",
    "Nnwom mu dwom": "SNG",
    "Yesaia": "ISA",
    "Yeremia": "JER",
    "Kwadwom": "LAM",
    "Hesekiel": "EZK",
    "Daniel": "DAN",
    "Hosea": "HOS",
    "Yoel": "JOL",
    "Amos": "AMO",
    "Obadia": "OBA",
    "Yona": "JON",
    "Mika": "MIC",
    "Nahum": "NAM",
    "Habakuk": "HAB",
    "Sefania": "ZEP",
    "Hagai": "HAG",
    "Sakaria": "ZEC",
    "Malaki": "MAL",
    "Mateo": "MAT",
    "Marko": "MRK",
    "Luka": "LUK",
    "Yohane": "JHN",
    "Asomafoɔ": "ACT",
    "Romafoɔ": "ROM",
    "1 Korintofoɔ": "1CO",
    "2 Korintofoɔ": "2CO",
    "Galatifoɔ": "GAL",
    "Efesofoɔ": "EPH",
    "Filipifoɔ": "PHP",
    "Kolosefoɔ": "COL",
    "1 Tesalonikafoɔ": "1TH",
    "2 Tesalonikafoɔ": "2TH",
    "1 Timoteo": "1TI",
    "2 Timoteo": "2TI",
    "Tito": "TIT",
    "Filemon": "PHM",
    "Hebrifoɔ": "HEB",
    "Yakobo": "JAS",
    "1 Petro": "1PE",
    "2 Petro": "2PE",
    "1 Yohane": "1JN",
    "2 Yohane": "2JN",
    "3 Yohane": "3JN",
    "Yuda": "JUD",
    "Adiyisɛm": "REV",
}
# Creating a list of the first three letters of each book, capitalized
books_short = [book.replace(" ", "")[:3].upper() for book in TWI_NAME_MAPPING.values()]

print(books_short)
base_prefix = "ASW"
other_prefix = "ASWDC"
other_prefix_2 = "ASNA"


def download(book, chapter, prefix):
    url = base_url.format(book=book, chapter=chapter, prefix=prefix)

    print(url)
    response = requests.get(url)
    if response.status_code == 404:
        print("1. 404 Error downloading %s.%s.%s %s" % (book, chapter, prefix, url))
        response = requests.get(
            other_url.format(book=book, chapter=chapter, prefix=other_prefix)
        )
        print("using alternative url.")
        if response.status_code == 404:
            print("2. 404 Error downloading %s.%s.%s %s" % (book, chapter, prefix, url))
            response = requests.get(
                other_url.format(book=book, chapter=chapter, prefix=other_prefix)
            )
            print("using alternative url.")
            if response.status_code == 404:
                print(
                    "2. 404 Error downloading %s.%s.%s %s"
                    % (book, chapter, prefix, url)
                )
                if response.status_code == 404:
                    print(
                        "2. 404 Error downloading %s.%s.%s %s"
                        % (book, chapter, prefix, url)
                    )
                    response = requests.get(
                        other_url_2.format(
                            book=book, chapter=chapter, prefix=other_prefix
                        )
                    )
                    print("using alternative url.")
                    if response.status_code == 404:
                        print(
                            "3. 404 Error downloading %s.%s.%s %s"
                            % (book, chapter, prefix, url)
                        )
                        return False

    data = response.json()
    if not data.get("pageProps", {}).get("chapterInfo"):
        print(
            "No chapter info found, exiting. empty chapter.%s.%s.%s"
            % (book, chapter, prefix)
        )

        print(data)
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
