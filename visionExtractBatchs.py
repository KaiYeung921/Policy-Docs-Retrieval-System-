#!/usr/bin/env python3
import google.generativeai as genai
import sys
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

# 1. Setup and Argument Validation
if len(sys.argv) != 2:
    print("Usage: ./visionExtractBatchs.py <input_file.pdf>")
    sys.exit(1)

input_file = sys.argv[1]

if not input_file.lower().endswith('.pdf'):
    print("Error: This script requires a .pdf file, not a .txt file.")
    sys.exit(1)

try:
    with open(input_file, "rb") as f:
        pass # Just checking if file exists
except FileNotFoundError:
    print(f"Error: {input_file} not found.")
    sys.exit(1)

if "GOOGLE_API_KEY" not in os.environ:
    print("Error: GOOGLE_API_KEY environment variable not set in .env or system")
    sys.exit(1)

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("=" * 100)
print(f"PIPELINE START: Native Vision Extraction for {os.path.basename(input_file)}")
print("=" * 100)

# 2. Upload the PDF to Gemini's File API
print("Uploading PDF to Gemini (this may take a few seconds)...")
try:
    pdf_file = genai.upload_file(path=input_file, mime_type="application/pdf")
    
    # Wait for the file to process if it's large
    while pdf_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        pdf_file = genai.get_file(pdf_file.name)
    print("\nUpload complete & processed.")
    
except Exception as e:
    print(f"Failed to upload PDF: {e}")
    sys.exit(1)

# 3. Define the 6-Pass Configuration with JSON Schemas
batches = [
    {
        "name": "PASS 1: Case Identity & Parties",
        "prompt": "Extract case metadata from this document. Identify Case Number, child identifiers (e.g. Kid 1), birth years, and parent genders. If not present, use 'Absent'.",
        "keys": ["Case Number", "Child Identifier", "Birth Year of Child", "Gender of Petitioner", "Gender of Respondent"]
    },
    {
        "name": "PASS 2: Legal Custody & Decision Making",
        "prompt": "Analyze Legal Custody checkboxes. Determine if Joint or Sole. Identify tie-breaker authority and who has decision-making power for specific domains.",
        "keys": ["Legal Custody Award Type", "Tie-Breaker Clause", "Consultation Requirement", "Education Domain", "Health Domain", "Extracurriculars Domain", "Religion Domain", "Documents Domain"]
    },
    {
        "name": "PASS 3: The Physical Schedule",
        "prompt": "Analyze the physical custody schedule and tables. CAREFULLY read tables left-to-right to keep child names and schedules aligned. Count days in a 14-day cycle.",
        "keys": ["Other Decision Domains", "Primary Residence", "Timeshare Percentage", "Child-Specific Variation", "Weekday Schedule Exists", "Weekly Schedule Rotation", "Weekdays with Petitioner", "Weekdays with Respondent", "Weekend Days with Petitioner", "Weekend Days with Respondent"]
    },
    {
        "name": "PASS 4: Logistics & Conduct Rules",
        "prompt": "Find exchange locations, transportation responsibilities, and behavioral restrictions (e.g., no alcohol, no contact). Read checkboxes carefully.",
        "keys": ["Exchange Times", "Exchange Location", "Transportation Responsibility", "Make-up Policy", "Supervised Visitation", "Conditions for Visitation", "Behavioral Restrictions", "No-Contact Clause", "Restraining Order"]
    },
    {
        "name": "PASS 5: Communication, Travel & Holidays",
        "prompt": "Extract rules for holidays, travel restrictions, distance/radius rules for moving, and communication protocols.",
        "keys": ["Holiday List", "Holiday Rotation", "Vacation Provision", "Travel Restrictions", "Parent-Parent Contact Protocol", "Parent-Child Contact", "Records Access", "Non-Disparagement Clause", "Notice Requirement", "Distance/Radius Rule", "Consent Requirement"]
    },
    {
        "name": "PASS 6: Financials & Disputes",
        "prompt": "Extract numeric income, child support amounts, who pays support, and dispute resolution steps (like mediation).",
        "keys": ["Mediation Step", "Material Change Clause", "Petitioner Monthly Income", "Respondent Monthly Income", "Child Support Payer", "Child Support Amount", "Taxes Clause", "Asset Division"]
    }
]

# 4. Execution Loop
all_results = {}
start_time = time.time()
model = genai.GenerativeModel("gemini-2.5-flash")

for i, batch in enumerate(batches, 1):
    print(f"\n[{i}/{len(batches)}] {batch['name']}")
    
    # We force the model to return a JSON object with exactly the keys we want
    expected_json_format = {key: "Extracted Value or 'Absent'" for key in batch["keys"]}
    
    full_prompt = (
        f"{batch['prompt']}\n\n"
        f"You MUST respond ONLY with a valid JSON object matching this exact structure:\n"
        f"{json.dumps(expected_json_format, indent=2)}"
    )

    try:
        response = model.generate_content(
            [pdf_file, full_prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0,
            )
        )
        
        # Parse the JSON string returned by the model
        batch_data = json.loads(response.text)
        
        valid_keys_found = 0
        for k, v in batch_data.items():
            if k in batch["keys"] and str(v).lower() not in ["absent", "none", "null", "not specified", ""]:
                all_results[k] = v
                valid_keys_found += 1
                
        print(f"  ✓ Extracted {valid_keys_found} variables from this section.")
        time.sleep(2) # Safety delay
        
    except Exception as e:
        print(f"  ✗ Pass {i} failed: {str(e)[:150]}")

# Clean up the file from Google's servers after we're done
try:
    genai.delete_file(pdf_file.name)
except Exception:
    pass

# 5. Output Summary
print("\n" + "=" * 100)
print(f"EXTRACTION COMPLETE | TOTAL TIME: {int(time.time() - start_time)}s")
print(f"Variables successfully captured: {len(all_results)} / 51")
print("=" * 100)

for k, v in all_results.items():
    print(f"{k:40} | {v}")
