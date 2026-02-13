#!/usr/bin/env python3

from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import sys

if len(sys.argv) != 2:
    print("Usage: ./ocr_script.py <input_pdf>")
    sys.exit(1)

input_pdf = sys.argv[1]


model = ocr_predictor(pretrained=True)

doc = DocumentFile.from_pdf("LegalDocTest.pdf")
result = model(doc)

full_text=result.render()

with open("FullDocExtracted.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("OCR extraction complete. Output saved to FullDocExtracted.txt")
