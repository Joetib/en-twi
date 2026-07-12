#!/usr/bin/env python3
"""
Script to parse NIV_bible.json into a list of verses with id and english text.

The input format is:
{
  "Book Name": {
    "Chapter": {
      "Verse": "Verse text"
    }
  }
}

The output format is:
[
  {
    "id": "Book Chapter:Verse",
    "english": "Verse text"
  }
]
"""

import json
import sys
from typing import List, Dict, Any


def parse_niv_bible(input_file: str, output_file: str) -> None:
    """
    Parse NIV Bible JSON file into a list of verses.

    Args:
        input_file: Path to the input NIV_bible.json file
        output_file: Path to the output niv_bible_verses.json file
    """
    try:
        # Load the NIV Bible data
        with open(input_file, "r", encoding="utf-8") as f:
            niv_data = json.load(f)

        verses = []

        # Iterate through each book
        for book_name, chapters in niv_data.items():
            # Iterate through each chapter
            for chapter_num, verses_in_chapter in chapters.items():
                # Iterate through each verse
                for verse_num, verse_text in verses_in_chapter.items():
                    # Create the ID in format "Book Chapter:Verse"
                    verse_id = f"{book_name} {chapter_num}:{verse_num}"

                    # Create the verse entry
                    verse_entry = {"id": verse_id, "english": verse_text}

                    verses.append(verse_entry)

        # Write the parsed verses to output file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(verses, f, ensure_ascii=False, indent=2)

        print(f"Successfully parsed {len(verses)} verses from {input_file}")
        print(f"Output saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file '{input_file}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main function to run the NIV Bible parser."""
    input_file = "NIV_bible.json"
    output_file = "niv_bible_verses.json"

    parse_niv_bible(input_file, output_file)


if __name__ == "__main__":
    main()


