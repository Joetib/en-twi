#!/usr/bin/env python3
"""
Script to merge NIV and Twi Bible verses into paired dataset.

This script takes two input files:
- niv_bible_verses.json: English Bible verses with format {"id": "Book Chapter:Verse", "english": "text"}
- twi_bible_verses.json: Twi Bible verses with format {"id": "TwiBook Chapter:Verse", "twi": "text"}

And creates a merged dataset with format:
{"id": "EnglishBook Chapter:Verse", "twi_id": "TwiBook Chapter:Verse", "twi": "text", "english": "text"}

The script uses a mapping dictionary to match Twi book names to English book names.
"""

import json
import sys
from typing import Dict, List, Any, Optional


def load_mapping() -> Dict[str, str]:
    """
    Load the book name mapping from Twi to English.

    Returns:
        Dictionary mapping Twi book names to English book names
    """
    return {
        "2 Beresosɛm": "2 Chronicles",
        "Yesaia": "Isaiah",
        "Hosea": "Hosea",
        "Yosua": "Joshua",
        "2 Samuel": "2 Samuel",
        "Yohane": "John",
        "1 Ahemfo": "1 Kings",
        "Hesekiel": "Ezekiel",
        "Nnwom": "Psalm",
        "2 Korintofo": "2 Corinthians",
        "1 Samuel": "1 Samuel",
        "Asomafo": "Acts",
        "1 Mose": "Genesis",
        "2 Ahemfo": "2 Kings",
        "Adiyisɛm": "Revelation",
        "Nehemia": "Nehemiah",
        "5 Mose": "Deuteronomy",
        "3 Mose": "Leviticus",
        "Ɔsɛnkafo": "Ecclesiastes",
        "Yeremia": "Jeremiah",
        "Mmebusɛm": "Proverbs",
        "4 Mose": "Numbers",
        "Luka": "Luke",
        "Sakaria": "Zechariah",
        "1 Petro": "1 Peter",
        "Marko": "Mark",
        "Yakobo": "James",
        "Filemon": "Philemon",
        "Ɛster": "Esther",
        "2 Mose": "Exodus",
        "Nahum": "Nahum",
        "Hiob": "Job",
        "Habakuk": "Habakkuk",
        "Yuda": "Jude",
        "Amos": "Amos",
        "Nnwom Mu Dwom": "Song of Solomon",
        "Mateo": "Matthew",
        "Atemmufo": "Judges",
        "2 Petro": "2 Peter",
        "Hebrifo": "Hebrews",
        "1 Tesalonikafo": "1 Thessalonians",
        "Malaki": "Malachi",
        "2 Tesalonikafo": "2 Thessalonians",
        "Rut": "Ruth",
        "Kwadwom": "Lamentations",
        "Kolosefo": "Colossians",
        "2 Yohane": "2 John",
        "1 Korintofo": "1 Corinthians",
        "Romafo": "Romans",
        "Ɛsra": "Ezra",
        "3 Yohane": "3 John",
        "1 Yohane": "1 John",
        "Obadia": "Obadiah",
        "1 Beresosɛm": "1 Chronicles",
        "Hagai": "Haggai",
        "Mika": "Micah",
        "Galatifo": "Galatians",
        "Yoɛl": "Joel",
        "1 Timoteo": "1 Timothy",
        "2 Timoteo": "2 Timothy",
        "Efesofo": "Ephesians",
        "Sefania": "Zephaniah",
        "Tito": "Titus",
        "Yona": "Jonah",
    }


def parse_verse_id(verse_id: str) -> tuple[str, str, str]:
    """
    Parse a verse ID into book, chapter, and verse components.

    Args:
        verse_id: Verse ID in format "Book Chapter:Verse"

    Returns:
        Tuple of (book, chapter, verse)
    """
    # Split by the last space to separate book from "Chapter:Verse"
    parts = verse_id.rsplit(" ", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid verse ID format: {verse_id}")

    book = parts[0]
    chapter_verse = parts[1]

    # Split chapter:verse
    if ":" not in chapter_verse:
        raise ValueError(f"Invalid chapter:verse format: {chapter_verse}")

    chapter, verse = chapter_verse.split(":", 1)
    return book, chapter, verse


def create_verse_key(book: str, chapter: str, verse: str) -> str:
    """
    Create a standardized key for verse matching.

    Args:
        book: Book name
        chapter: Chapter number
        verse: Verse number

    Returns:
        Standardized key for matching
    """
    return f"{book}|{chapter}|{verse}"


def build_verse_index(
    verses: List[Dict[str, str]], is_twi: bool, mapping: Dict[str, str]
) -> Dict[str, Dict[str, str]]:
    """
    Build an index of verses for efficient lookup.

    Args:
        verses: List of verse dictionaries
        is_twi: Whether these are Twi verses (need mapping) or English verses
        mapping: Book name mapping from Twi to English

    Returns:
        Dictionary with standardized keys mapping to verse data
    """
    index = {}

    for verse in verses:
        verse_id = verse["id"]
        book, chapter, verse_num = parse_verse_id(verse_id)

        # Map Twi book names to English book names
        if is_twi:
            if book not in mapping:
                print(f"Warning: No mapping found for Twi book '{book}'")
                continue
            english_book = mapping[book]
        else:
            english_book = book

        # Create standardized key
        key = create_verse_key(english_book, chapter, verse_num)

        # Store verse data
        verse_data = {
            "original_id": verse_id,
            "book": english_book,
            "chapter": chapter,
            "verse": verse_num,
        }

        if is_twi:
            verse_data["twi"] = verse["twi"]
        else:
            verse_data["english"] = verse["english"]

        index[key] = verse_data

    return index


def merge_verses(niv_file: str, twi_file: str, output_file: str) -> None:
    """
    Merge NIV and Twi Bible verses into paired dataset.

    Args:
        niv_file: Path to NIV Bible verses JSON file
        twi_file: Path to Twi Bible verses JSON file
        output_file: Path to output merged dataset JSON file
    """
    try:
        # Load mapping
        mapping = load_mapping()

        # Load NIV verses
        with open(niv_file, "r", encoding="utf-8") as f:
            niv_verses = json.load(f)

        # Load Twi verses
        with open(twi_file, "r", encoding="utf-8") as f:
            twi_verses = json.load(f)

        print(f"Loaded {len(niv_verses)} NIV verses and {len(twi_verses)} Twi verses")

        # Build indices
        print("Building verse indices...")
        niv_index = build_verse_index(niv_verses, is_twi=False, mapping=mapping)
        twi_index = build_verse_index(twi_verses, is_twi=True, mapping=mapping)

        print(
            f"Built indices: {len(niv_index)} NIV entries, {len(twi_index)} Twi entries"
        )

        # Merge verses
        merged_verses = []
        matched_count = 0
        unmatched_niv = 0
        unmatched_twi = 0

        # Find all unique keys
        all_keys = set(niv_index.keys()) | set(twi_index.keys())

        for key in all_keys:
            niv_verse = niv_index.get(key)
            twi_verse = twi_index.get(key)

            if niv_verse and twi_verse:
                # Both verses found - create merged entry
                merged_entry = {
                    "id": f"{niv_verse['book']} {niv_verse['chapter']}:{niv_verse['verse']}",
                    "twi_id": twi_verse["original_id"],
                    "twi": twi_verse["twi"],
                    "english": niv_verse["english"],
                }
                merged_verses.append(merged_entry)
                matched_count += 1
            elif niv_verse:
                # Only NIV verse found
                unmatched_niv += 1
                print(
                    f"Warning: No Twi match for NIV verse: {niv_verse['original_id']}"
                )
            elif twi_verse:
                # Only Twi verse found
                unmatched_twi += 1
                print(
                    f"Warning: No NIV match for Twi verse: {twi_verse['original_id']}"
                )

        # Sort merged verses by book, chapter, verse
        def sort_key(verse):
            book, chapter, verse_num = parse_verse_id(verse["id"])
            # Create a sortable key (you might want to implement proper book ordering)
            return (book, int(chapter), int(verse_num))

        merged_verses.sort(key=sort_key)

        # Write output
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(merged_verses, f, ensure_ascii=False, indent=2)

        print(f"\nMerge completed:")
        print(f"- Matched verses: {matched_count}")
        print(f"- Unmatched NIV verses: {unmatched_niv}")
        print(f"- Unmatched Twi verses: {unmatched_twi}")
        print(f"- Total merged verses: {len(merged_verses)}")
        print(f"Output saved to {output_file}")

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main function to run the Bible verse merger."""
    niv_file = "niv_bible_verses.json"
    twi_file = "twi_bible_verses.json"
    output_file = "bible_verses.json"

    merge_verses(niv_file, twi_file, output_file)


if __name__ == "__main__":
    main()
