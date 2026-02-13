#!/usr/bin/env python3

import langextract as lx
import textwrap
import sys

if len(sys.argv) != 2:
    print("Usage: ./extract.py <input_text_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)


prompt = textwrap.dedent("""
You are extracting structured data from a California FL-180 Judgment form.

Extract ONLY the following entities if explicitly present:

1. Case Number
   - Appears near top right
   - Often labeled "CASE NUMBER:"
   - Example: 17CHFL00863

2. Petitioner Name
   - Appears after "PETITIONER:"

3. Respondent Name
   - Appears after "RESPONDENT:"

4. Jurisdiction Date
   - Appears after:
     "The court acquired jurisdiction of the respondent on (date):"

5. Judgment Type
   - One of:
       Dissolution
       Legal Separation
       Nullity
   - Based only on which option is selected.

6. Termination Date
   - Appears after:
       "Date marital or domestic partnership status ends:"
       OR
       "(1) on (specify date):"

STRICT RULES:
- Extract exact text from the document.
- Do not paraphrase.
- Do not infer.
- If not clearly present, do not extract.
- Do not combine multiple fields.
- Output only valid structured extractions.
""")


examples = [
    lx.data.ExampleData(
        text="""
        PETITIONER: John Smith
        RESPONDENT: Jane Smith
        CASE NUMBER: 19FL12345
        The court acquired jurisdiction of the respondent on (date): 03/15/2019
        Dissolution
        Date marital or domestic partnership status ends: 05/01/2020
        """,
        extractions=[
            lx.data.Extraction(
                extraction_class="Case Number",
                extraction_text="19FL12345",
                attributes={}
            ),
            lx.data.Extraction(
                extraction_class="Petitioner Name",
                extraction_text="John Smith",
                attributes={}
            ),
            lx.data.Extraction(
                extraction_class="Respondent Name",
                extraction_text="Jane Smith",
                attributes={}
            ),
            lx.data.Extraction(
                extraction_class="Jurisdiction Date",
                extraction_text="03/15/2019",
                attributes={}
            ),
            lx.data.Extraction(
                extraction_class="Judgment Type",
                extraction_text="Dissolution",
                attributes={}
            ),
            lx.data.Extraction(
                extraction_class="Termination Date",
                extraction_text="05/01/2020",
                attributes={}
            ),
        ]
    )
]


result = lx.extract(
    text_or_documents=text,
    prompt_description=prompt,
    examples=examples,
    model_id="llama3",
    model_url="http://localhost:11434",
    fence_output=False,
    use_schema_constraints=True,
    temperature=0.0,
    extraction_passes=3,
    max_workers=20,
    max_char_buffer=1000
)


for e in result.extractions:
    print(f"{e.extraction_class}: '{e.extraction_text}'")

