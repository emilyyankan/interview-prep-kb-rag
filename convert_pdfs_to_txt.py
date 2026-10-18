"""
Recursively walk a folder (including all subfolders) and convert every PDF
found into a plain-text .txt file, saved alongside the original PDF.
"""

import os
import sys
import pdfplumber


def convert_pdf_to_txt(pdf_path: str, txt_path: str) -> bool:
    # Extract text from a single PDF and write it to txt_path. Returns True on success.
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    all_text.append(text)
                else:
                    all_text.append(f"[Page {i + 1}: no extractable text — likely scanned/image-based]")

        full_text = "\n\n".join(all_text)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        return True
    except Exception as e:
        print(f"  ERROR converting {pdf_path}: {e}")
        return False


def walk_and_convert(root_dir: str, skip_existing: bool = True):
    """
    Walk root_dir and all subfolders, converting every .pdf found.
    If skip_existing is True, PDFs that already have a matching .txt
    file (based on filename) will be skipped, useful for re-runs
    when you add new documents over time.
    """
    converted = 0
    skipped = 0
    failed = 0

    for current_root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(current_root, filename)
                txt_filename = os.path.splitext(filename)[0] + ".txt"
                txt_path = os.path.join(current_root, txt_filename)

                if skip_existing and os.path.exists(txt_path):
                    print(f"Skipping (already converted): {pdf_path}")
                    skipped += 1
                    continue

                print(f"Converting: {pdf_path}")
                success = convert_pdf_to_txt(pdf_path, txt_path)
                if success:
                    converted += 1
                else:
                    failed += 1

    print("\n--- Summary ---")
    print(f"Converted: {converted}")
    print(f"Skipped (already existed): {skipped}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_pdfs_to_txt.py /path/to/root/folder")
        sys.exit(1)

    root_folder = sys.argv[1]

    if not os.path.isdir(root_folder):
        print(f"Error: {root_folder} is not a valid directory")
        sys.exit(1)

    walk_and_convert(root_folder)
