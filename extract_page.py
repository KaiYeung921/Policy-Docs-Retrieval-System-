#!/usr/bin/env python3

import sys
from pypdf import PdfReader

if len(sys.argv) != 3:
    print("Usage: python extract_page.py <pdf_file> <page_number>")
    sys.exit(1)

pdf_file = sys.argv[1]
page_number = int(sys.argv[2])

reader = PdfReader(pdf_file)

# pypdf uses 0-based indexing
if page_number < 1 or page_number > len(reader.pages):
    print("Invalid page number.")
    sys.exit(1)

text = reader.pages[page_number - 1].extract_text()

output_file = f"extracted{page_number}.txt"

with open(output_file, "w") as f:
    f.write(text)

print(f"Extracted page {page_number} to {output_file}")

