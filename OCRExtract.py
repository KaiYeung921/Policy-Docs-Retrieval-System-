#!/usr/bin/env python3

from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import sys
from pathlib import Path


if len(sys.argv) != 2:
    print("Usage: ./ocr_script.py <input_pdf>")
    sys.exit(1)

input_pdf = sys.argv[1]


model = ocr_predictor(pretrained=True)

doc = DocumentFile.from_pdf(input_pdf)
result = model(doc)

full_text=result.render()

input_path = Path(input_pdf)
output_filename = input_path.stem + "_extracted.txt"

with open(output_filename, "w", encoding="utf-8") as f:
    f.write(full_text)

print("OCR extraction complete. Output")
