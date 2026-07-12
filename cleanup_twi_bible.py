#!/usr/bin/env python3
"""
Script to clean up twi-asw_bible_verses.json by removing:
1. Text starting from '#' (cross-references)
2. Repeating verse numbers and duplicate text

The pattern in the data is: {text} {optional # similar verses} {verse number} {repeating text}
"""

import json
import re


def clean_verse_text(text: str) -> str:
    """
    Clean a single verse text by removing cross-references and duplicate content.

    Args:
        text (str): The original verse text

    Returns:
        str: The cleaned verse text
    """
    if not text:
        return text

    # Remove everything starting from '#' (cross-references)
    # This handles patterns like "# Gye 5" or "# Gye 10.2-5"
    text = re.sub(r"\s*#.*$", "", text)

    # Handle complex repeating patterns with multiple repetitions
    # Split by common separators and look for repeated segments
    original_text = text

    # First, try to find the longest non-repeating segment
    # Look for patterns where text is repeated multiple times with numbers in between

    # Pattern 1: Handle cases like "text.text.22" or "text text 22"
    # Remove trailing verse numbers that are just numbers
    text = re.sub(r"\s+\d+\s*$", "", text)

    # Pattern 2: Handle multiple repetitions of the same text
    # Look for text that appears multiple times with numbers or punctuation in between
    words = text.split()
    if len(words) > 3:
        # Try to find repeated segments
        for i in range(1, len(words) // 2 + 1):
            segment = " ".join(words[:i])
            # Check if this segment appears multiple times
            if text.count(segment) > 1:
                # Find where the repetition starts
                first_occurrence = text.find(segment)
                second_occurrence = text.find(segment, first_occurrence + len(segment))
                if second_occurrence != -1:
                    # Take only the first occurrence
                    text = text[:second_occurrence].strip()
                    break

    # Pattern 3: Handle cases where text is repeated with punctuation and numbers
    # Look for patterns like "text.text.22" or "text,text,22"
    pattern3 = r"^(.+?)([.,;:])\1.*$"
    match3 = re.match(pattern3, text)
    if match3:
        return (match3.group(1) + match3.group(2)).strip()

    # Pattern 4: Handle cases where text is repeated with numbers in between
    # Look for patterns like "text 22 text" where the same text appears twice
    pattern4 = r"^(.+?)\s+\d+\s+\1.*$"
    match4 = re.match(pattern4, text)
    if match4:
        return match4.group(1).strip()

    # Pattern 5: Handle cases where text is repeated multiple times with numbers
    # Look for patterns like "text.text.text.22" or "text text text 22"
    # Find the longest segment that doesn't repeat
    segments = re.split(r"[.,;:\s]+", text)
    if len(segments) > 2:
        # Try to find where repetition starts
        for i in range(1, len(segments) // 2 + 1):
            if i < len(segments):
                segment = segments[i]
                # Check if this segment appears earlier
                for j in range(i):
                    if segments[j] == segment and not segment.isdigit():
                        # Found repetition, take everything before this point
                        return " ".join(segments[:i]).strip()

    # Pattern 6: Handle cases where the same phrase appears multiple times
    # Split by common punctuation and look for repeated phrases
    phrases = re.split(r"[.!?]+", text)
    if len(phrases) > 1:
        first_phrase = phrases[0].strip()
        for phrase in phrases[1:]:
            phrase = phrase.strip()
            if phrase and first_phrase in phrase:
                # Found repetition, return only the first phrase
                return first_phrase

    # If no pattern matches, return the text as is (after removing # references)
    return text.strip()


def clean_bible_verses(input_file: str, output_file: str) -> None:
    """
    Clean the entire Bible verses dataset.

    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to the output JSON file
    """
    print(f"Loading data from {input_file}...")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        return

    print(f"Processing {len(data)} verses...")

    cleaned_data = []
    processed_count = 0

    for item in data:
        if "twi" in item:
            original_text = item["twi"]
            cleaned_text = clean_verse_text(original_text)

            # Create new item with cleaned text
            cleaned_item = {"id": item.get("id", ""), "twi": cleaned_text}

            cleaned_data.append(cleaned_item)
            processed_count += 1

            # Show progress for every 1000 verses
            if processed_count % 1000 == 0:
                print(f"Processed {processed_count} verses...")

    print(f"Saving cleaned data to {output_file}...")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {len(cleaned_data)} cleaned verses to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")


def main():
    """Main function to run the cleanup process."""
    input_file = "twi-asw_bible_verses.json"
    output_file = "cleaned-twi-bible-asw.json"

    print("Twi Bible Verses Cleanup Script")
    print("=" * 40)

    # Show some examples before cleaning
    print("\nSample verses before cleaning:")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            sample_data = json.load(f)[:5]  # First 5 verses

        for i, item in enumerate(sample_data, 1):
            print(f"{i}. {item.get('twi', '')}")
    except Exception as e:
        print(f"Could not load sample data: {e}")

    # Run the cleanup
    clean_bible_verses(input_file, output_file)

    # Show some examples after cleaning
    print("\nSample verses after cleaning:")
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            cleaned_sample = json.load(f)[:5]  # First 5 verses

        for i, item in enumerate(cleaned_sample, 1):
            print(f"{i}. {item.get('twi', '')}")
    except Exception as e:
        print(f"Could not load cleaned sample data: {e}")


if __name__ == "__main__":
    main()
