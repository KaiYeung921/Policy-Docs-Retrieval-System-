#!/usr/bin/env python3


import langextract as lx
import textwrap
import sys


if len(sys.argv) != 2:
    print("Usage: ./extract.py <input_text_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, "r") as f:
        text = f.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)



# Define extraction task
prompt = textwrap.dedent("""
    Extract only specfically listed variables in this legal family court document. The legal custody will always come first and then the phyiscal custody.
    The variables being:
    Legal Custody
    Physical Custody

    Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context
""")

# Provide example
examples = [
    lx.data.ExampleData(
        text="5. Custody. Custody of the minor children of the parlies is awarded as follows: ChiId's name Date of birlh Leal custod t_o Phsical custod to (Person who makes decIs/ons about (person with whom the child /ives) health, education, etc.) Jordan Alexander 03/08/2012 Joint (Petitioner & Respondent) Respondent. Castaneda Gonzales",
        extractions=[
            lx.data.Extraction(
                extraction_class="Legal Custody",
                extraction_text="Joint (Petitioner & Respondent)",
		attributes={"type": "joint"}
            ),
            lx.data.Extraction(
                extraction_class="Physical Custody",
                extraction_text="Respondent",
		attributes={"type": "sole"}
            ),
        ]
    )
]

# Run extraction
result = lx.extract(
    text_or_documents=text,
    prompt_description=prompt,
    examples=examples,
    model_id="llama3",                  # Change to your model
    model_url="http://localhost:11434",    # Ollama default endpoint
    fence_output=False,
    use_schema_constraints=True,
)

# Print results
for e in result.extractions:
    print(f"{e.extraction_class}: '{e.extraction_text}' → {e.attributes}")
