#!/usr/bin/env python3
"""
Script to merge missing verses from cleaned-twi-bible-asw.json into twi-data.json.

This script:
1. Loads the existing twi-data.json structure
2. Loads the cleaned-twi-bible-asw.json data
3. Identifies missing verses in twi-data.json
4. Fills in the missing verses from cleaned-twi-bible-asw.json
5. Outputs the merged data in the same structure as twi-data.json
"""

import json
import re
from typing import Dict, Any, Set, Tuple


def parse_verse_id(verse_id: str) -> Tuple[str, int, int]:
    """
    Parse a verse ID like "Genesis 1:1" into book name, chapter, and verse number.
    Handles verse ranges like "Genesis 1:19-22" by taking the first verse number.

    Args:
        verse_id: The verse ID string (e.g., "Genesis 1:1" or "Genesis 1:19-22")

    Returns:
        Tuple of (book_name, chapter_number, verse_number)
    """
    # Handle different book name formats and verse ranges
    match = re.match(r"(.+?)\s+(\d+):(\d+(?:-\d+)?)", verse_id)
    if not match:
        raise ValueError(f"Could not parse verse ID: {verse_id}")

    book_name = match.group(1).strip()
    chapter = int(match.group(2))

    # Handle verse ranges (e.g., "19-22" -> 19)
    verse_str = match.group(3)
    if "-" in verse_str:
        verse = int(verse_str.split("-")[0])
    else:
        verse = int(verse_str)

    return book_name, chapter, verse


def get_existing_verses(twi_data: Dict[str, Any]) -> Set[Tuple[str, int, int]]:
    """
    Extract all existing verse identifiers from twi-data.json structure.

    Args:
        twi_data: The loaded twi-data.json structure

    Returns:
        Set of tuples (book_name, chapter, verse_number) for existing verses
    """
    existing_verses = set()

    for book_name, chapters in twi_data.items():
        for chapter_num, verses in chapters.items():
            try:
                chapter_int = int(chapter_num)
            except ValueError:
                print(
                    f"Warning: Invalid chapter number '{chapter_num}' in book '{book_name}', skipping"
                )
                continue

            for verse_num in verses.keys():
                try:
                    # Handle verse ranges in existing data
                    if "-" in verse_num:
                        verse_int = int(verse_num.split("-")[0])
                    else:
                        verse_int = int(verse_num)
                    existing_verses.add((book_name, chapter_int, verse_int))
                except ValueError:
                    print(
                        f"Warning: Invalid verse number '{verse_num}' in {book_name} {chapter_num}, skipping"
                    )
                    continue

    return existing_verses


def merge_verses(twi_data: Dict[str, Any], cleaned_data: list) -> Dict[str, Any]:
    """
    Merge missing verses from cleaned data into twi_data structure.

    Args:
        twi_data: The existing twi-data.json structure
        cleaned_data: The cleaned-twi-bible-asw.json data as a list

    Returns:
        Updated twi_data with missing verses filled in
    """
    # Get existing verses
    existing_verses = get_existing_verses(twi_data)

    # Track added verses for reporting
    added_count = 0
    skipped_count = 0

    for verse_entry in cleaned_data:
        try:
            verse_id = verse_entry["id"]
            verse_text = verse_entry["twi"]

            # Parse the verse ID
            book_name, chapter, verse_num = parse_verse_id(verse_id)

            # Check if this verse already exists
            if (book_name, chapter, verse_num) in existing_verses:
                skipped_count += 1
                continue

            # Add the missing verse
            if book_name not in twi_data:
                twi_data[book_name] = {}

            if str(chapter) not in twi_data[book_name]:
                twi_data[book_name][str(chapter)] = {}

            twi_data[book_name][str(chapter)][str(verse_num)] = verse_text
            added_count += 1

        except (KeyError, ValueError) as e:
            print(f"Warning: Skipping invalid verse entry: {verse_entry}, Error: {e}")
            continue

    print(f"Added {added_count} missing verses")
    print(f"Skipped {skipped_count} existing verses")

    return twi_data


def main():
    """Main function to execute the merge process."""
    try:
        # Load the existing twi-data.json
        print("Loading twi-data.json...")
        with open("twi-data.json", "r", encoding="utf-8") as f:
            twi_data = json.load(f)

        # Load the cleaned-twi-bible-asw.json
        print("Loading cleaned-twi-bible-asw.json...")
        with open("cleaned-twi-bible-asw.json", "r", encoding="utf-8") as f:
            cleaned_data = json.load(f)

        print(f"Loaded {len(twi_data)} books from twi-data.json")
        print(f"Loaded {len(cleaned_data)} verses from cleaned-twi-bible-asw.json")

        # Merge the verses
        print("Merging missing verses...")
        merged_data = merge_verses(twi_data, cleaned_data)

        # Save the merged data
        output_file = "merged-twi-data.json"
        print(f"Saving merged data to {output_file}...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        print(f"Successfully merged data and saved to {output_file}")

        # Print some statistics
        total_books = len(merged_data)
        total_chapters = sum(len(chapters) for chapters in merged_data.values())
        total_verses = sum(
            len(verses)
            for chapters in merged_data.values()
            for verses in chapters.values()
        )

        print("\nFinal statistics:")
        print(f"Total books: {total_books}")
        print(f"Total chapters: {total_chapters}")
        print(f"Total verses: {total_verses}")

    except FileNotFoundError as e:
        print(f"Error: Could not find required file: {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
