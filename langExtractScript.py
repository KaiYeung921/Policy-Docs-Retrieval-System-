#!/usr/bin/env python3

import sys
import langextract as lx
import textwrap

if len(sys.argv) != 2:
    print("Usage: ./extract.py <input_text_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, "r") as f:
        input=f.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)




prompt = textwrap.dedent("""
    Extract only specfically listed variables in this legal family court document. The legal custody will always come first and then the phyiscal custody.
    The variables being:
    Legal Custody
    Physical Custody

    Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context
""")


examples = [
    lx.data.ExampleData(
        text=input
        extractions=[
            lx.data.Extraction(
                extraction_class="Legal Custody",
                extraction_text="Joint (Petitioner & Respondent)",
            ),
            lx.data.Extraction(
                extraction_class="Physical Custody",
                extraction_text="Respondent",
            ),
        ]
    )
]


result = lx.extract(
    text_or_documents=input,
    prompt_description=prompt,
    examples=examples,
    model_id="mistral",                  # Change to your model
    model_url="http://localhost:11434",    # Ollama default endpoint
    fence_output=False,
    use_schema_constraints=False,
)

# Print results
for e in result.extractions:
    print(f"{e.extraction_class}: '{e.extraction_text}' → {e.attributes}")
