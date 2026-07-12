import os
import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup


# Mapping from book abbreviations to full English names
BOOK_ABBREVIATIONS = {
    # Old Testament
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numbers",
    "DEU": "Deuteronomy",
    "JOS": "Joshua",
    "JDG": "Judges",
    "RUT": "Ruth",
    "1SA": "1 Samuel",
    "2SA": "2 Samuel",
    "1KI": "1 Kings",
    "2KI": "2 Kings",
    "1CH": "1 Chronicles",
    "2CH": "2 Chronicles",
    "EZR": "Ezra",
    "NEH": "Nehemiah",
    "EST": "Esther",
    "JOB": "Job",
    "PSA": "Psalms",
    "PRO": "Proverbs",
    "ECC": "Ecclesiastes",
    "SNG": "Song of Songs",
    "ISA": "Isaiah",
    "JER": "Jeremiah",
    "LAM": "Lamentations",
    "EZK": "Ezekiel",
    "DAN": "Daniel",
    "HOS": "Hosea",
    "JOL": "Joel",
    "AMO": "Amos",
    "OBA": "Obadiah",
    "JON": "Jonah",
    "MIC": "Micah",
    "NAH": "Nahum",
    "HAB": "Habakkuk",
    "ZEP": "Zephaniah",
    "HAG": "Haggai",
    "ZEC": "Zechariah",
    "MAL": "Malachi",
    # New Testament
    "MAT": "Matthew",
    "MRK": "Mark",
    "LUK": "Luke",
    "JHN": "John",
    "ACT": "Acts",
    "ROM": "Romans",
    "1CO": "1 Corinthians",
    "2CO": "2 Corinthians",
    "GAL": "Galatians",
    "EPH": "Ephesians",
    "PHP": "Philippians",
    "COL": "Colossians",
    "1TH": "1 Thessalonians",
    "2TH": "2 Thessalonians",
    "1TI": "1 Timothy",
    "2TI": "2 Timothy",
    "TIT": "Titus",
    "PHM": "Philemon",
    "HEB": "Hebrews",
    "JAS": "James",
    "1PE": "1 Peter",
    "2PE": "2 Peter",
    "1JN": "1 John",
    "2JN": "2 John",
    "3JN": "3 John",
    "JUD": "Jude",
    "REV": "Revelation",
}


def get_book_name_from_filename(filename: str) -> str:
    """
    Extract book name from filename and convert to full English name.

    Args:
        filename (str): Filename like "1CH.1.ASW.json"

    Returns:
        str: Full book name like "1 Chronicles"
    """
    # Extract book abbreviation from filename
    book_abbr = filename.split(".")[0]

    # Return full book name or original if not found
    book_name = BOOK_ABBREVIATIONS.get(book_abbr, book_abbr)

    print("Found book name: ", book_name, " for ", book_abbr)
    return book_name


def extract_verses_from_html(
    html_content: str, book_name: str, chapter: str
) -> List[Dict[str, str]]:
    """
    Extract verses from HTML content using BeautifulSoup.

    Args:
        html_content (str): HTML content containing verses
        book_name (str): Full book name
        chapter (str): Chapter number

    Returns:
        List[Dict[str, str]]: List of verse dictionaries with 'id' and 'english' keys
    """
    verses = []

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all verse spans with data-usfm attribute
        verse_spans = soup.find_all("span", {"data-usfm": True})

        for span in verse_spans:
            # Extract verse number from data-usfm attribute
            data_usfm = span.get("data-usfm", "")
            # Format: BOOK.CH.VERSE (e.g., "1CH.1.1")
            parts = data_usfm.split(".")
            if len(parts) >= 3:
                verse_num = parts[2]

                # Extract verse content
                verse_content = ""

                # Get all text content, excluding footnotes and cross-references
                for element in span.find_all(["span"]):
                    # Skip footnote and cross-reference spans
                    if element.get("class"):
                        classes = element.get("class", [])
                        if any(
                            cls in ["note", "x", "f", "ft", "fr", "fq", "body"]
                            for cls in classes
                        ):
                            continue

                    # Get text content
                    if element.string:
                        verse_content += element.string
                    else:
                        verse_content += element.get_text()

                # Also get direct text content from the span
                if span.string:
                    verse_content += span.string
                else:
                    # Get text content excluding child elements we already processed
                    direct_text = span.get_text()
                    if direct_text:
                        verse_content += direct_text

                # Clean up the verse content
                verse_content = verse_content.strip()

                # Remove extra whitespace and clean up
                verse_content = re.sub(r"\s+", " ", verse_content)

                # Remove common artifacts
                verse_content = re.sub(
                    r"^\d+\s*", "", verse_content
                )  # Remove leading verse numbers
                verse_content = re.sub(r"^#\s*", "", verse_content)  # Remove leading #

                if (
                    verse_content and len(verse_content) > 3
                ):  # Only include substantial content
                    verse_id = f"{book_name} {chapter}:{verse_num}"
                    verses.append({"id": verse_id, "english": verse_content})

    except Exception as e:
        print(f"Error parsing HTML content: {e}")

    return verses


def parse_bible_translation(
    translation_dir: str, translation_name: str
) -> List[Dict[str, str]]:
    """
    Parse all files in a Bible translation directory.

    Args:
        translation_dir (str): Path to translation directory
        translation_name (str): Name of the translation (e.g., "NIV", "ESV")

    Returns:
        List[Dict[str, str]]: List of all verses from the translation
    """
    all_verses = []

    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(translation_dir) if f.endswith(".json")]
    json_files.sort()  # Sort for consistent ordering

    print(f"Processing {len(json_files)} files for {translation_name}...")

    for filename in json_files:
        file_path = os.path.join(translation_dir, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Extract book name and chapter from filename
            parts = filename.replace(".json", "").split(".")
            if len(parts) >= 2:
                book_name = get_book_name_from_filename(filename)
                chapter = parts[1]

                # Extract HTML content from the JSON structure
                html_content = ""
                if "pageProps" in data and "chapterInfo" in data["pageProps"]:
                    chapter_info = data["pageProps"]["chapterInfo"]
                    if "content" in chapter_info:
                        html_content = chapter_info["content"]

                if html_content:
                    # Extract verses from HTML
                    verses = extract_verses_from_html(html_content, book_name, chapter)
                    all_verses.extend(verses)

                    if verses:
                        print(f"  {filename}: {len(verses)} verses")
                else:
                    print(f"  {filename}: No content found")
            else:
                print(f"  {filename}: Invalid filename format")

        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            continue

    return all_verses


def save_verses_to_json(verses: List[Dict[str, str]], output_path: str) -> None:
    """
    Save the parsed verses to a JSON file.

    Args:
        verses (List[Dict[str, str]]): List of verse dictionaries
        output_path (str): Path where to save the JSON file
    """
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(verses, file, ensure_ascii=False, indent=2)


def main():
    """
    Main function to parse all Bible translations and create JSON outputs.
    """
    bibles_dir = "/Users/joetib/Desktop/projects/graduation/bibles/"

    # List of translations to process
    translations = [
        "ASW",
    ]  # "ESV", "NIV", "NLT"]

    for translation in translations:
        translation_dir = os.path.join(bibles_dir, translation)

        if os.path.exists(translation_dir):
            print(f"\n=== Processing {translation} ===")

            # Parse the translation
            verses = parse_bible_translation(translation_dir, translation)

            # Save to JSON file
            output_file = f"/Users/joetib/Desktop/projects/graduation/eng-{translation.lower()}_bible_verses.json"
            save_verses_to_json(verses, output_file)

            print(f"Saved {len(verses)} verses to {output_file}")

            # Print first few verses as example
            if verses:
                print(f"\nFirst 3 verses from {translation}:")
                for i, verse in enumerate(verses[:3]):
                    print(f"{i + 1}. ID: {verse['id']}")
                    print(
                        f"   English: {verse['english'][:100]}..."
                        if len(verse["english"]) > 100
                        else f"   English: {verse['english']}"
                    )
                    print()
        else:
            print(f"Directory not found: {translation_dir}")


if __name__ == "__main__":
    main()
