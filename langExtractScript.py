#!/usr/bin/env python3
import langextract as lx
import textwrap
import sys
import os

if len(sys.argv) != 2:
    print("Usage: ./langExtractScript_20vars.py <input_text_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)

print(f"Document length: {len(text)} characters\n")

# Check if API key is set
if "GOOGLE_API_KEY" not in os.environ:
    print("Error: GOOGLE_API_KEY environment variable not set")
    print("Set it with: export GOOGLE_API_KEY='your-key-here'")
    sys.exit(1)

# Comprehensive prompt for FL-180 form extraction
prompt = textwrap.dedent("""
Extract the following 20 fields from this California FL-180 Judgment form.
Only extract if the information is explicitly present in the document.

CASE INFORMATION (4 fields):
1. Case Number - Format: letters+numbers (e.g., 17CHFL00863)
2. Petitioner Name - Full legal name after "PETITIONER:"
3. Respondent Name - Full legal name after "RESPONDENT:"
4. Court Location - County and courthouse name

DATES (3 fields):
5. Jurisdiction Date - Date court acquired jurisdiction
6. Judgment Date - Date judgment was entered
7. Termination Date - Date marital/domestic partnership ends

JUDGMENT TYPE (2 fields):
8. Judgment Type - One of: Dissolution, Legal Separation, Nullity
9. Hearing Type - Default, Contested, Agreement, or Declaration

CHILD INFORMATION (5 fields):
10. Child Name - Full name of child
11. Child Date of Birth - Format: MM/DD/YYYY
12. Legal Custody - Who makes decisions (Joint, Petitioner, Respondent)
13. Physical Custody - Who child lives with (Petitioner, Respondent)
14. Visitation Schedule - Days and times for parenting time

FINANCIAL INFORMATION (6 fields):
15. Monthly Child Support Amount - Dollar amount per month
16. Child Support Payable To - Name of receiving parent
17. Petitioner Monthly Income - Gross monthly income
18. Respondent Monthly Income - Gross monthly income
19. Percentage Time with Petitioner - Custody percentage
20. Percentage Time with Respondent - Custody percentage

EXTRACTION RULES:
- Extract exact text from document - do not paraphrase
- If field not present, skip it entirely
- Use proper date formats when specified
- For currency, include dollar sign and decimals
- For percentages, include % symbol
""").strip()

# Real example from the uploaded FL-180 document
examples = [
    lx.data.ExampleData(
        text="""
        CASE NUMBER: 17CHFL00863
        PETITIONER: Miguel Angel Castaneda Soltero
        RESPONDENT: Cecilia Jeannet Gonzales
        SUPERIOR COURT OF CALIFORNIA, COUNTY OF Los Angeles
        BRANCH NAME: Chatsworth Courthouse
        
        The court acquired jurisdiction of the respondent on (date): 09/25/2017
        Judgment of dissolution is entered. Date: NOV 1 9 2018
        
        This proceeding was heard as follows: Default or uncontested
        
        Custody of the minor children:
        Child's name: Jordan Alexander Castaneda Gonzales
        Date of birth: 03/08/2012
        Legal custody to: Joint (Petitioner & Respondent)
        Physical custody to: Respondent
        
        Visitation: Every Tuesday and Thursday from 6:00 p.m. until 9:00 p.m.
        Alternate weekends from Friday at 5:00 p.m. to Sunday at 9:0 p.m.
        
        Child support: $450.00 per month
        Payable to: Respondent
        
        Petitioner monthly income: $2,700
        Respondent monthly income: $2,500
        Approximate percentage of time with petitioner: 30%
        Approximate percentage of time with respondent: 70%
        """,
        extractions=[
            lx.data.Extraction(
                extraction_class="Case Number",
                extraction_text="17CHFL00863"
            ),
            lx.data.Extraction(
                extraction_class="Petitioner Name",
                extraction_text="Miguel Angel Castaneda Soltero"
            ),
            lx.data.Extraction(
                extraction_class="Respondent Name",
                extraction_text="Cecilia Jeannet Gonzales"
            ),
            lx.data.Extraction(
                extraction_class="Court Location",
                extraction_text="Los Angeles - Chatsworth Courthouse"
            ),
            lx.data.Extraction(
                extraction_class="Jurisdiction Date",
                extraction_text="09/25/2017"
            ),
            lx.data.Extraction(
                extraction_class="Judgment Date",
                extraction_text="NOV 1 9 2018"
            ),
            lx.data.Extraction(
                extraction_class="Termination Date",
                extraction_text="NOV 1 9 2018"
            ),
            lx.data.Extraction(
                extraction_class="Judgment Type",
                extraction_text="Dissolution"
            ),
            lx.data.Extraction(
                extraction_class="Hearing Type",
                extraction_text="Default or uncontested"
            ),
            lx.data.Extraction(
                extraction_class="Child Name",
                extraction_text="Jordan Alexander Castaneda Gonzales"
            ),
            lx.data.Extraction(
                extraction_class="Child Date of Birth",
                extraction_text="03/08/2012"
            ),
            lx.data.Extraction(
                extraction_class="Legal Custody",
                extraction_text="Joint (Petitioner & Respondent)"
            ),
            lx.data.Extraction(
                extraction_class="Physical Custody",
                extraction_text="Respondent"
            ),
            lx.data.Extraction(
                extraction_class="Visitation Schedule",
                extraction_text="Every Tuesday and Thursday from 6:00 p.m. until 9:00 p.m. Alternate weekends from Friday at 5:00 p.m. to Sunday at 9:0 p.m."
            ),
            lx.data.Extraction(
                extraction_class="Monthly Child Support Amount",
                extraction_text="$450.00"
            ),
            lx.data.Extraction(
                extraction_class="Child Support Payable To",
                extraction_text="Respondent"
            ),
            lx.data.Extraction(
                extraction_class="Petitioner Monthly Income",
                extraction_text="$2,700"
            ),
            lx.data.Extraction(
                extraction_class="Respondent Monthly Income",
                extraction_text="$2,500"
            ),
            lx.data.Extraction(
                extraction_class="Percentage Time with Petitioner",
                extraction_text="30%"
            ),
            lx.data.Extraction(
                extraction_class="Percentage Time with Respondent",
                extraction_text="70%"
            ),
        ]
    )
]

print("Running extraction with Gemini (this may take 1-2 minutes)...\n")

try:
    result = lx.extract(
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        model_id="gemini-2.5-flash",  # Use flash-latest for separate quota
        model_url=None,
        fence_output=False,  # Gemini native JSON
        use_schema_constraints=True,
        temperature=0.0,
        max_workers=1,  # Process sequentially to avoid rate limits
        batch_length=1,
    )
    
    print(f"Raw extractions: {len(result.extractions)}\n")

except Exception as e:
    print(f"Extraction failed: {e}")
    print("\nTry waiting a few minutes if you hit rate limits")
    sys.exit(1)

# Deduplication and filtering
seen = {}
filtered = []

for e in result.extractions:
    if not e.extraction_text or e.extraction_text.strip() == '':
        continue
    
    text_upper = e.extraction_text.upper()
    skip_phrases = [
        'NOT EXPLICITLY PRESENT',
        'NOT PRESENT',
        'NOT MENTIONED',
    ]
    
    if any(phrase in text_upper for phrase in skip_phrases):
        continue
    
    # Only keep first valid occurrence of each class
    key = e.extraction_class
    
    if key not in seen:
        seen[key] = True
        filtered.append(e)

# Print results organized by category
print("=" * 80)
print("EXTRACTED FL-180 FAMILY LAW JUDGMENT DATA")
print("=" * 80)

if filtered:
    # Group by category
    categories = {
        "CASE INFORMATION": [
            "Case Number", "Petitioner Name", "Respondent Name", "Court Location"
        ],
        "DATES": [
            "Jurisdiction Date", "Judgment Date", "Termination Date"
        ],
        "JUDGMENT TYPE": [
            "Judgment Type", "Hearing Type"
        ],
        "CHILD INFORMATION": [
            "Child Name", "Child Date of Birth", "Legal Custody", 
            "Physical Custody", "Visitation Schedule"
        ],
        "FINANCIAL INFORMATION": [
            "Monthly Child Support Amount", "Child Support Payable To",
            "Petitioner Monthly Income", "Respondent Monthly Income",
            "Percentage Time with Petitioner", "Percentage Time with Respondent"
        ]
    }
    
    for category, fields in categories.items():
        print(f"\n{category}:")
        print("-" * 80)
        found_any = False
        for field in fields:
            matching = [e for e in filtered if e.extraction_class == field]
            if matching:
                found_any = True
                e = matching[0]
                print(f"  {e.extraction_class}: {e.extraction_text}")
        if not found_any:
            print("  (No data found)")
else:
    print("\nNo data found in document.")

print(f"\n{'=' * 80}")
print(f"Fields extracted: {len(filtered)}/20")
print(f"Duplicates filtered: {len(result.extractions) - len(filtered)}")
print(f"{'=' * 80}")
