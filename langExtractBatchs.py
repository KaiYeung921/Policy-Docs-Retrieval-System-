#!/usr/bin/env python3
import langextract as lx
import textwrap
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# 1. Setup and Argument Validation
if len(sys.argv) != 2:
    print("Usage: ./langExtractBatchs.py <input_text_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print(f"Error: {input_file} not found.")
    sys.exit(1)

if "GOOGLE_API_KEY" not in os.environ:
    print("Error: GOOGLE_API_KEY environment variable not set in .env or system")
    sys.exit(1)

print("=" * 100)
print(f"PIPELINE START: Partitioned Extraction for {os.path.basename(input_file)}")
print("=" * 100)

# 2. Define the Optimized Configuration (with PERFECTLY aligned examples)
batches = [
    {
        "name": "PASS 1: Case Identity & Parties",
        "prompt": "Extract case metadata. Identify Case Number, child identifiers, birth years, and parent genders.",
        "example_text": "The Case Number is 17STFL03130. The Child Identifier is Kid 1. The Birth Year of Child is 2015. The Gender of Petitioner is Female. The Gender of Respondent is Male.",
        "vars": [
            ("Case Number", "17STFL03130"),
            ("Child Identifier", "Kid 1"),
            ("Birth Year of Child", "2015"),
            ("Gender of Petitioner", "Female"),
            ("Gender of Respondent", "Male")
        ]
    },
    {
        "name": "PASS 2: Legal Custody & Decision Making",
        "prompt": "Analyze Legal Custody. Determine if Joint or Sole. Identify tie-breaker authority and decision domains.",
        "example_text": "The Legal Custody Award Type is Joint. The Tie-Breaker Clause is Petitioner has tie-break. The Consultation Requirement is Present. The Education Domain is Specified for Petitioner. The Health Domain is Mutually Agreed. The Extracurriculars Domain is Mutually Agreed. The Religion Domain is Absent. The Documents Domain is Mutually Agreed.",
        "vars": [
            ("Legal Custody Award Type", "Joint"),
            ("Tie-Breaker Clause", "Petitioner has tie-break"),
            ("Consultation Requirement", "Present"),
            ("Education Domain", "Specified for Petitioner"),
            ("Health Domain", "Mutually Agreed"),
            ("Extracurriculars Domain", "Mutually Agreed"),
            ("Religion Domain", "Absent"),
            ("Documents Domain", "Mutually Agreed")
        ]
    },
    {
        "name": "PASS 3: The Physical Schedule",
        "prompt": "Calculate the custody split based on the weekly schedule. Count days in a 14-day cycle.",
        "example_text": "The Other Decision Domains is Absent. The Primary Residence is Respondent. The Timeshare Percentage is 70/30%. The Child-Specific Variation is Only one child. The Weekday Schedule Exists is Yes. The Weekly Schedule Rotation is Yes. The Weekdays with Petitioner is 4. The Weekdays with Respondent is 6. The Weekend Days with Petitioner is 2. The Weekend Days with Respondent is 2.",
        "vars": [
            ("Other Decision Domains", "Absent"),
            ("Primary Residence", "Respondent"),
            ("Timeshare Percentage", "70/30%"),
            ("Child-Specific Variation", "Only one child"),
            ("Weekday Schedule Exists", "Yes"),
            ("Weekly Schedule Rotation", "Yes"),
            ("Weekdays with Petitioner", "4"),
            ("Weekdays with Respondent", "6"),
            ("Weekend Days with Petitioner", "2"),
            ("Weekend Days with Respondent", "2")
        ]
    },
    {
        "name": "PASS 4: Logistics & Conduct Rules",
        "prompt": "Find exchange locations, transportation, and behavioral restrictions.",
        "example_text": "The Exchange Times is Present. The Exchange Location is Present. The Transportation Responsibility is Petitioner. The Make-up Policy is Absent. The Supervised Visitation is Absent. The Conditions for Visitation is No Conditions Mentioned. The Behavioral Restrictions is Symmetric. The No-Contact Clause is Absent. The Restraining Order is Absent.",
        "vars": [
            ("Exchange Times", "Present"),
            ("Exchange Location", "Present"),
            ("Transportation Responsibility", "Petitioner"),
            ("Make-up Policy", "Absent"),
            ("Supervised Visitation", "Absent"),
            ("Conditions for Visitation", "No Conditions Mentioned"),
            ("Behavioral Restrictions", "Symmetric"),
            ("No-Contact Clause", "Absent"),
            ("Restraining Order", "Absent")
        ]
    },
    {
        "name": "PASS 5: Communication, Travel & Holidays",
        "prompt": "Extract rules for holidays, travel, and communication protocols.",
        "example_text": "The Holiday List is Present. The Holiday Rotation is Present. The Vacation Provision is Present. The Travel Restrictions is Present. The Parent-Parent Contact Protocol is Protocol Specified. The Parent-Child Contact is Mentioned. The Records Access is Present. The Non-Disparagement Clause is Present. The Notice Requirement is Present. The Distance/Radius Rule is Present. The Consent Requirement is Present.",
        "vars": [
            ("Holiday List", "Present"),
            ("Holiday Rotation", "Present"),
            ("Vacation Provision", "Present"),
            ("Travel Restrictions", "Present"),
            ("Parent-Parent Contact Protocol", "Protocol Specified"),
            ("Parent-Child Contact", "Mentioned"),
            ("Records Access", "Present"),
            ("Non-Disparagement Clause", "Present"),
            ("Notice Requirement", "Present"),
            ("Distance/Radius Rule", "Present"),
            ("Consent Requirement", "Present")
        ]
    },
    {
        "name": "PASS 6: Financials & Disputes",
        "prompt": "Extract income, support amounts, and dispute resolution steps.",
        "example_text": "The Mediation Step is Generic Mediation Clause. The Material Change Clause is Present. The Petitioner Monthly Income is 3200. The Respondent Monthly Income is 4500. The Child Support Payer is Respondent. The Child Support Amount is 850. The Taxes Clause is Split. The Asset Division is In Document.",
        "vars": [
            ("Mediation Step", "Generic Mediation Clause"),
            ("Material Change Clause", "Present"),
            ("Petitioner Monthly Income", "3200"),
            ("Respondent Monthly Income", "4500"),
            ("Child Support Payer", "Respondent"),
            ("Child Support Amount", "850"),
            ("Taxes Clause", "Split"),
            ("Asset Division", "In Document")
        ]
    }
]

# 3. Execution Loop
all_results = []
start_time = time.time()
MODEL_ID = "gemini-2.5-flash"

for i, batch in enumerate(batches, 1):
    print(f"\n[{i}/{len(batches)}] {batch['name']}")
    
    # Using the pre-aligned example text directly from the config
    example = lx.data.ExampleData(
        text=batch["example_text"], 
        extractions=[lx.data.Extraction(extraction_class=k, extraction_text=str(v)) for k, v in batch['vars']]
    )

    try:
        full_prompt = f"{batch['prompt']}\n\nRULES:\n- Use standard values provided in examples.\n- If not present, skip."
        
        result = lx.extract(
            text_or_documents=text,
            prompt_description=full_prompt,
            examples=[example],
            model_id=MODEL_ID,
            temperature=0.0,
            fence_output=False
        )
        
        print(f"  ✓ Extracted {len(result.extractions)} variables.")
        all_results.extend(result.extractions)
        time.sleep(2) 
        
    except Exception as e:
        print(f"  ✗ Pass {i} failed: {str(e)[:150]}")

# 4. Final Processing and Cleanup
seen = {}
final_list = []
for e in all_results:
    if e.extraction_class not in seen and e.extraction_text:
        seen[e.extraction_class] = True
        final_list.append(e)

# 5. Output Summary
print("\n" + "=" * 100)
print(f"EXTRACTION COMPLETE | TOTAL TIME: {int(time.time() - start_time)}s")
print(f"Variables successfully captured: {len(final_list)} / 51")
print("=" * 100)

for e in final_list:
    print(f"{e.extraction_class:40} | {e.extraction_text}")
