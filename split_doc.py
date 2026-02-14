#!/usr/bin/env python3
import sys

if len(sys.argv) != 3:
    print("Usage: ./split_doc.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Read the full document
with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

# Calculate 1/4th position
quarter_length = len(text) // 4

# Extract first quarter
first_quarter = text[:quarter_length]

# Write to output file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(first_quarter)

print(f"Original length: {len(text)} characters")
print(f"First quarter length: {len(first_quarter)} characters")
print(f"Saved to: {output_file}")
