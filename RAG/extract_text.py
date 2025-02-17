import os
import sys
import json
import argparse
from pathlib import Path

from pypdf import PdfReader
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    print(f"[INFO] Extracting PDF: {pdf_path}")
    text_pages = []
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page_index, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_pages.append(page_text)
            print(f"  -> Page {page_index} length: {len(page_text)} chars")

    full_text = "\n".join(text_pages)
    print(
        f"[INFO] Total PDF text length for '{pdf_path.name}': {len(full_text)} chars\n"
    )
    return full_text


def extract_text_from_epub(epub_path):
    """Extract text from an EPUB file."""
    print(f"[INFO] Extracting EPUB: {epub_path}")
    # Some older ebooklib versions don't support ignore_ncx
    # If you see a TypeError, remove ignore_ncx=True
    book = epub.read_epub(epub_path)
    text_chapters = []

    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.content, "html.parser")
            chapter_text = soup.get_text()
            text_chapters.append(chapter_text)

    full_text = "\n".join(text_chapters)
    print(
        f"[INFO] Total EPUB text length for '{epub_path.name}': {len(full_text)} chars\n"
    )
    return full_text


def find_surrogates(text):
    """Return a list of all surrogate characters in 'text'."""
    return [ch for ch in text if 0xD800 <= ord(ch) <= 0xDFFF]


def remove_surrogates(text):
    """
    Remove surrogate characters entirely.
    Alternatively, you can use .encode('utf-8', 'replace').decode('utf-8')
    if you'd prefer to replace them with � instead.
    """
    return "".join(ch for ch in text if not (0xD800 <= ord(ch) <= 0xDFFF))


def process_files(input_folder, output_json):
    """Process all PDF and EPUB files in 'input_folder' and save text as JSON."""
    # 1. Load existing data if output_json already exists
    if os.path.isfile(output_json):
        with open(output_json, "r", encoding="utf-8") as f:
            extracted_data = json.load(f)
        print(
            f"[INFO] Loaded existing data from '{output_json}' with {len(extracted_data)} entries."
        )
    else:
        extracted_data = {}

    # 2. Iterate over files in the input folder
    for file_path in Path(input_folder).rglob("*"):
        if file_path.suffix.lower() not in [".pdf", ".epub"]:
            continue  # Skip non-PDF/EPUB files

        # 2a. Check if already processed
        if file_path.name in extracted_data:
            print(f"[INFO] Skipping '{file_path.name}' (already processed).")
            continue

        # 2b. Extract text
        if file_path.suffix.lower() == ".pdf":
            raw_text = extract_text_from_pdf(file_path)
        else:  # .epub
            raw_text = extract_text_from_epub(file_path)

        # 2c. Debug: Check surrogates before cleaning
        surrogates_found = find_surrogates(raw_text)
        print(
            f"[DEBUG] '{file_path.name}' => Surrogates found (before cleaning): {len(surrogates_found)}"
        )

        # 2d. Remove surrogate characters
        cleaned_text = remove_surrogates(raw_text)

        # 2e. Debug: Check surrogates after cleaning
        surrogates_after = find_surrogates(cleaned_text)
        print(
            f"[DEBUG] '{file_path.name}' => Surrogates found (after cleaning): {len(surrogates_after)}"
        )

        # 2f. Store result in dictionary
        extracted_data[file_path.name] = cleaned_text
        print(
            f"[INFO] Processed '{file_path.name}', final length: {len(cleaned_text)} chars\n"
        )

    # 3. Write to JSON
    print(f"[INFO] Saving extracted text to '{output_json}'...")
    try:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        print(f"[INFO] ✅ Done! Data saved to {output_json}")
    except UnicodeEncodeError as e:
        print(f"[ERROR] UnicodeEncodeError while writing JSON: {e}")
        print(
            "[TIP] Surrogate removal might not have caught every issue. Consider using 'replace' instead."
        )


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF & EPUB files.")
    parser.add_argument("input_folder", help="Folder containing PDF & EPUB files")
    parser.add_argument("output_json", help="Output JSON file to save extracted text")
    args = parser.parse_args()

    process_files(args.input_folder, args.output_json)


if __name__ == "__main__":
    main()
