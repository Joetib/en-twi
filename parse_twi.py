import os
import json
import re
from typing import List, Dict, Any


def parse_twi_bible_files(directory_path: str) -> List[Dict[str, str]]:
    """
    Parse all TWI-BIBLE text files and convert them to a JSON list structure.

    Each file contains verses in the format:
    /// [Book Name] [Chapter]:[Verse]
    [Twi text content]

    Args:
        directory_path (str): Path to the TWI-BIBLE directory containing .txt files

    Returns:
        List[Dict[str, str]]: List of dictionaries with 'id' and 'twi' keys
    """
    verses = []

    # Get all .txt files in the directory
    txt_files = [f for f in os.listdir(directory_path) if f.endswith(".txt")]
    txt_files.sort()  # Sort for consistent ordering

    for filename in txt_files:
        file_path = os.path.join(directory_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()

                # Skip empty files
                if not content:
                    continue

                # Split content into lines
                lines = content.split("\n")

                i = 0
                while i < len(lines):
                    line = lines[i].strip()

                    # Check if this line is a verse header (starts with ///)
                    if line.startswith("///"):
                        # Extract book name, chapter, and verse from header
                        # Format: /// [Book Name] [Chapter]:[Verse]
                        header_match = re.match(r"///\s+(.+?)\s+(\d+):(\d+)", line)

                        if header_match:
                            book_name = header_match.group(1).strip()
                            chapter = header_match.group(2)
                            verse_num = header_match.group(3)

                            # Create the ID in the format used in the files
                            verse_id = f"{book_name} {chapter}:{verse_num}"

                            # Get the verse content (next line)
                            if i + 1 < len(lines):
                                verse_content = lines[i + 1].strip()

                                # Add to verses list
                                verses.append({"id": verse_id, "twi": verse_content})

                                # Move to next verse (skip the content line)
                                i += 2
                            else:
                                # No content found, skip
                                i += 1
                        else:
                            # Invalid header format, skip
                            i += 1
                    else:
                        # Not a verse header, skip
                        i += 1

        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            continue

    return verses


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
    Main function to parse TWI-BIBLE files and create JSON output.
    """
    # Path to the TWI-BIBLE directory
    twi_bible_dir = "/Users/joetib/Desktop/projects/graduation/TWI-BIBLE"
    output_file = "/Users/joetib/Desktop/projects/graduation/twi_bible_verses.json"

    print("Parsing TWI-BIBLE files...")
    verses = parse_twi_bible_files(twi_bible_dir)

    print(f"Found {len(verses)} verses")

    # Save to JSON file
    save_verses_to_json(verses, output_file)
    print(f"Saved verses to {output_file}")

    # Print first few verses as example
    if verses:
        print("\nFirst 3 verses:")
        for i, verse in enumerate(verses[:3]):
            print(f"{i + 1}. ID: {verse['id']}")
            print(
                f"   Twi: {verse['twi'][:100]}..."
                if len(verse["twi"]) > 100
                else f"   Twi: {verse['twi']}"
            )
            print()


if __name__ == "__main__":
    main()

