#!/usr/bin/env python3
import langextract as lx
import textwrap
import sys
import os
import time

if len(sys.argv) != 2:
    print("Usage: ./langExtractScript_batched.py <input_text_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print("File not found.")
    sys.exit(1)

print(f"Document length: {len(text)} characters\n")

if "GOOGLE_API_KEY" not in os.environ and "LANGEXTRACT_API_KEY" not in os.environ:
    print("Error: GOOGLE_API_KEY or LANGEXTRACT_API_KEY environment variable not set")
    print("Set it with: export LANGEXTRACT_API_KEY='your-key-here'")
    sys.exit(1)

print("=" * 100)
print("BATCHED EXTRACTION: Processing 51 variables in 5 batches")
print("=" * 100)
print()

# Define 5 batches of variables
batches = [
    {
        "name": "BATCH 1: General Info & Legal Custody (13 variables)",
        "prompt": textwrap.dedent("""
        Extract these 13 fields from this California Family Law document.
        Only extract if explicitly present.
        
        GENERAL INFORMATION:
        1. Case Number - Case identifier (e.g., 17CHFL00863)
        2. Child Identifier - Which child if multiple (Kid 1, Kid 2, etc.)
        3. Birth Year of Child - Year only (YYYY format)
        4. Gender of Petitioner - Male or Female
        5. Gender of Respondent - Male or Female
        
        LEGAL CUSTODY:
        6. Legal Custody Award Type - Joint / Sole, Petitioner / Sole, Respondent
        7. Tie-Breaker Clause - Who breaks ties in joint custody (Petitioner has tie-break / Absent)
        8. Consultation Requirement - Must consult before decisions (Present / Absent)
        9. Education Domain - Who decides education (Mutually Agreed / Specified for Petitioner / Specified for Respondent / Absent)
        10. Health Domain - Who decides health matters (Mutually Agreed / Specified for Petitioner / Specified for Respondent / Absent)
        11. Extracurriculars Domain - Who decides activities (Mutually Agreed / Specified for Petitioner / Specified for Respondent / Absent)
        12. Religion Domain - Who decides religion (Mutually Agreed / Specified for Petitioner / Specified for Respondent / Absent)
        13. Documents Domain - Who accesses records (Mutually Agreed / Specified for Petitioner / Specified for Respondent / Absent)
        
        Extract exact text. Use standardized values shown in parentheses.
        """).strip(),
        "example_text": """
        CASE NUMBER: 17CHFL00863
        Child: Jordan Alexander (born 03/08/2012)
        PETITIONER: Miguel Angel Castaneda Soltero (Male)
        RESPONDENT: Cecilia Jeannet Gonzales (Female)
        
        LEGAL CUSTODY: Joint (Petitioner & Respondent)
        Petitioner shall have tie-breaking authority.
        Parents must consult before major decisions.
        Education: Mutually agreed
        Health: Mutually agreed
        Extracurriculars: Mutually agreed
        """,
        "extractions": [
            ("Case Number", "17CHFL00863"),
            ("Child Identifier", "Kid 1"),
            ("Birth Year of Child", "2012"),
            ("Gender of Petitioner", "Male"),
            ("Gender of Respondent", "Female"),
            ("Legal Custody Award Type", "Joint"),
            ("Tie-Breaker Clause", "Petitioner has tie-break"),
            ("Consultation Requirement", "Present"),
            ("Education Domain", "Mutually Agreed"),
            ("Health Domain", "Mutually Agreed"),
            ("Extracurriculars Domain", "Mutually Agreed"),
            ("Religion Domain", "Absent"),
            ("Documents Domain", "Mutually Agreed"),
        ]
    },
    {
        "name": "BATCH 2: Physical Custody & Regular Schedule (13 variables)",
        "prompt": textwrap.dedent("""
        Extract these 13 fields about physical custody and schedules.
        
        PHYSICAL CUSTODY:
        1. Other Decision Domains - Any other domains specified (Present / Absent)
        2. Primary Residence - Where child lives (Petitioner / Respondent / Joint / Absent)
        3. Timeshare Percentage - Custody split (e.g., 70/30%, 50/50%)
        4. Child-Specific Variation - Different schedules per child (Yes / No / Only one child)
        
        REGULAR SCHEDULE:
        5. Weekday Schedule Exists - Is weekday schedule specified (Yes / No / Reasonable right to visitation)
        6. Weekly Schedule Rotation - Does it alternate weeks (Yes / No)
        7. Weekdays with Petitioner - Out of 10 weekdays per 2 weeks, how many with petitioner (0-10)
        8. Weekdays with Respondent - Out of 10 weekdays, how many with respondent (0-10)
        9. Weekend Days with Petitioner - Out of 4 weekend days per 2 weeks (0-4)
        10. Weekend Days with Respondent - Out of 4 weekend days (0-4)
        11. Exchange Times - Pickup/dropoff times specified (Present / Absent)
        12. Exchange Location - Where exchanges happen (Present / Absent / Mutually Agreed)
        13. Transportation Responsibility - Who transports (Petitioner / Respondent / Split / Mutually Agreed / Absent)
        
        Use exact standardized values.
        """).strip(),
        "example_text": """
        PHYSICAL CUSTODY: Respondent (70% time)
        Approximate percentage: 70% Respondent, 30% Petitioner
        This is the only child.
        
        VISITATION:
        Petitioner: Every Tuesday and Thursday 6pm-9pm (2 weekdays/week)
        Alternate weekends Friday 5pm to Sunday 9pm (2 weekend days per 2 weeks)
        
        Exchange times: specified at 5:00pm and 9:00pm
        Exchanges at Respondent's residence
        Transportation: Petitioner provides both directions
        """,
        "extractions": [
            ("Other Decision Domains", "Absent"),
            ("Primary Residence", "Respondent"),
            ("Timeshare Percentage", "70/30%"),
            ("Child-Specific Variation", "Only one child"),
            ("Weekday Schedule Exists", "Yes"),
            ("Weekly Schedule Rotation", "Yes"),
            ("Weekdays with Petitioner", "4"),
            ("Weekdays with Respondent", "6"),
            ("Weekend Days with Petitioner", "2"),
            ("Weekend Days with Respondent", "2"),
            ("Exchange Times", "Present"),
            ("Exchange Location", "Present"),
            ("Transportation Responsibility", "Petitioner"),
        ]
    },
    {
        "name": "BATCH 3: Holidays, Vacation & Visitation Conditions (11 variables)",
        "prompt": textwrap.dedent("""
        Extract these 11 fields about holidays, vacation, and visitation rules.
        
        SCHEDULE DETAILS:
        1. Make-up Policy - Policy for missed visits (Present / Absent)
        
        HOLIDAY & VACATION:
        2. Holiday List - Specific holidays listed (Present / Absent / Mutually Agreed)
        3. Holiday Rotation - Holidays alternate yearly (Present / Absent)
        4. Vacation Provision - Extended vacation rules (Present / Absent)
        5. Travel Restrictions - Travel limitations (Present / Absent)
        
        VISITATION CONDITIONS:
        6. Supervised Visitation - Must visits be supervised (Professional / Non-professional / Absent)
        7. Conditions for Visitation - Special requirements (No Conditions Mentioned / Conditions Mentioned - No Verification Required / Conditions Present)
        8. Behavioral Restrictions - Rules during visits (Symmetric / Asymmetric / Absent)
        9. No-Contact Clause - Third parties excluded (Present / Absent)
        10. Restraining Order - Active restraining orders (Present / Absent)
        
        Use standardized values.
        """).strip(),
        "example_text": """
        Make-up visitation: Missed time may be made up within 30 days.
        
        HOLIDAYS: Thanksgiving, Christmas, New Year's alternate annually
        Each parent: 2-week summer vacation with 60 days notice
        Travel outside California requires written consent.
        
        VISITATION CONDITIONS:
        No supervision required.
        No special conditions for visitation.
        No restraining orders in effect.
        """,
        "extractions": [
            ("Make-up Policy", "Present"),
            ("Holiday List", "Present"),
            ("Holiday Rotation", "Present"),
            ("Vacation Provision", "Present"),
            ("Travel Restrictions", "Present"),
            ("Supervised Visitation", "Absent"),
            ("Conditions for Visitation", "No Conditions Mentioned"),
            ("Behavioral Restrictions", "Absent"),
            ("No-Contact Clause", "Absent"),
            ("Restraining Order", "Absent"),
        ]
    },
    {
        "name": "BATCH 4: Communication & Relocation (7 variables)",
        "prompt": textwrap.dedent("""
        Extract these 7 fields about communication and relocation rules.
        
        COMMUNICATION & INFORMATION:
        1. Parent-Parent Contact Protocol - How parents communicate (Protocol Specified / Absent)
        2. Parent-Child Contact - Rules for phone/video (Mentioned / Absent)
        3. Records Access - Access to school/medical records (Present / Mutually Agreed / Absent)
        4. Non-Disparagement Clause - Cannot speak badly of other parent (Present / Absent)
        
        RELOCATION:
        5. Notice Requirement - Must notify before moving (Present / Absent)
        6. Distance/Radius Rule - Cannot move beyond X miles (Present / Absent / LA County / Specify distance)
        7. Consent Requirement - Need permission to relocate (Present / Absent)
        
        Use exact values shown.
        """).strip(),
        "example_text": """
        COMMUNICATION:
        Parents communicate via email/text for scheduling.
        Each parent may have reasonable phone contact with child.
        Both parents have equal access to school and medical records.
        Neither parent shall disparage the other to the child.
        
        RELOCATION:
        45 days advance written notice required for any move.
        Cannot relocate more than 50 miles without consent.
        Consent required for relocation beyond 50 miles.
        """,
        "extractions": [
            ("Parent-Parent Contact Protocol", "Protocol Specified"),
            ("Parent-Child Contact", "Mentioned"),
            ("Records Access", "Present"),
            ("Non-Disparagement Clause", "Present"),
            ("Notice Requirement", "Present"),
            ("Distance/Radius Rule", "Present"),
            ("Consent Requirement", "Present"),
        ]
    },
    {
        "name": "BATCH 5: Dispute Resolution & Financial (7 variables)",
        "prompt": textwrap.dedent("""
        Extract these 7 fields about dispute resolution and finances.
        
        DISPUTE RESOLUTION & MODIFICATION:
        1. Mediation Step - Must mediate before court (Generic Mediation Clause / Mediator is specified / Absent)
        2. Material Change Clause - Conditions for modifying custody (Present / Absent)
        
        FINANCIAL INFORMATION:
        3. Petitioner Monthly Income - Gross monthly income (numeric value only)
        4. Respondent Monthly Income - Gross monthly income (numeric value only)
        5. Child Support Payer - Who pays (Petitioner / Respondent / Absent / Reserved / Previously established in another case)
        6. Child Support Amount - Monthly amount (numeric value only)
        7. Taxes Clause - Who claims child on taxes (Petitioner / Respondent / Split / Absent)
        8. Asset Division - Property division (In Document / Mentioned Elsewhere / Absent)
        
        For income/support: extract only the number (e.g., 2700, not $2,700)
        """).strip(),
        "example_text": """
        DISPUTE RESOLUTION:
        Parties shall attempt mediation before court filings.
        Custody modifiable upon material change in circumstances.
        
        CHILD SUPPORT:
        Petitioner gross monthly income: $2,700
        Respondent gross monthly income: $2,500
        Petitioner pays Respondent $450.00 per month
        Tax dependent: Alternates yearly between parents
        
        Property division detailed in separate settlement agreement.
        """,
        "extractions": [
            ("Mediation Step", "Generic Mediation Clause"),
            ("Material Change Clause", "Present"),
            ("Petitioner Monthly Income", "2700"),
            ("Respondent Monthly Income", "2500"),
            ("Child Support Payer", "Petitioner"),
            ("Child Support Amount", "450"),
            ("Taxes Clause", "Split"),
            ("Asset Division", "Mentioned Elsewhere"),
        ]
    }
]

# Run extraction for each batch
all_results = []
failed_batches = []

for i, batch in enumerate(batches, 1):
    print(f"\n{'=' * 100}")
    print(f"{batch['name']}")
    print(f"{'=' * 100}")
    
    # Create example
    example = lx.data.ExampleData(
        text=batch["example_text"],
        extractions=[
            lx.data.Extraction(extraction_class=cls, extraction_text=txt)
            for cls, txt in batch["extractions"]
        ]
    )
    
    try:
        print(f"Processing... ", end='', flush=True)
        result = lx.extract(
            text_or_documents=text,
            prompt_description=batch["prompt"],
            examples=[example],
            model_id="gemini-2.5-flash",
            model_url=None,
            fence_output=True,
            use_schema_constraints=False,  # Disabled to avoid complexity limits
            temperature=0.0,
            max_workers=1,
            batch_length=1,
        )
        
        print(f"✓ Extracted {len(result.extractions)} items")
        all_results.extend(result.extractions)
        
        # Small delay between batches to avoid rate limits
        if i < len(batches):
            time.sleep(2)
            
    except Exception as e:
        print(f"✗ FAILED")
        print(f"  Error: {str(e)[:200]}")
        failed_batches.append(batch["name"])
        continue

print(f"\n\n{'=' * 100}")
print(f"EXTRACTION COMPLETE")
print(f"{'=' * 100}")

# Deduplication
seen = {}
filtered = []

for e in all_results:
    if not e.extraction_text or e.extraction_text.strip() == '':
        continue
    
    text_upper = e.extraction_text.upper()
    if any(p in text_upper for p in ['NOT EXPLICITLY PRESENT', 'NOT PRESENT', 'NOT MENTIONED']):
        continue
    
    key = e.extraction_class
    if key not in seen:
        seen[key] = True
        filtered.append(e)

# Organize results by category
print("\n" + "=" * 100)
print("COMPREHENSIVE FAMILY LAW CUSTODY EXTRACTION - ALL 51 VARIABLES")
print("=" * 100)

categories = {
    "GENERAL INFORMATION": [
        "Case Number", "Child Identifier", "Birth Year of Child", 
        "Gender of Petitioner", "Gender of Respondent"
    ],
    "LEGAL CUSTODY": [
        "Legal Custody Award Type", "Tie-Breaker Clause", "Consultation Requirement",
        "Education Domain", "Health Domain", "Extracurriculars Domain",
        "Religion Domain", "Documents Domain", "Other Decision Domains"
    ],
    "PHYSICAL CUSTODY": [
        "Primary Residence", "Timeshare Percentage", "Child-Specific Variation"
    ],
    "REGULAR SCHEDULE": [
        "Weekday Schedule Exists", "Weekly Schedule Rotation",
        "Weekdays with Petitioner", "Weekdays with Respondent",
        "Weekend Days with Petitioner", "Weekend Days with Respondent",
        "Exchange Times", "Exchange Location", "Transportation Responsibility", "Make-up Policy"
    ],
    "HOLIDAY & VACATION": [
        "Holiday List", "Holiday Rotation", "Vacation Provision", "Travel Restrictions"
    ],
    "VISITATION CONDITIONS": [
        "Supervised Visitation", "Conditions for Visitation", "Behavioral Restrictions",
        "No-Contact Clause", "Restraining Order"
    ],
    "COMMUNICATION & INFORMATION": [
        "Parent-Parent Contact Protocol", "Parent-Child Contact",
        "Records Access", "Non-Disparagement Clause"
    ],
    "RELOCATION": [
        "Notice Requirement", "Distance/Radius Rule", "Consent Requirement"
    ],
    "DISPUTE RESOLUTION": [
        "Mediation Step", "Material Change Clause"
    ],
    "FINANCIAL INFORMATION": [
        "Petitioner Monthly Income", "Respondent Monthly Income",
        "Child Support Payer", "Child Support Amount",
        "Taxes Clause", "Asset Division"
    ]
}

if filtered:
    for category, fields in categories.items():
        print(f"\n{category}")
        print("-" * 100)
        found_any = False
        for field in fields:
            matching = [e for e in filtered if e.extraction_class == field]
            if matching:
                found_any = True
                e = matching[0]
                print(f"  {e.extraction_class:45s} {e.extraction_text}")
        if not found_any:
            print("  (No data found)")
else:
    print("\nNo data extracted.")

print(f"\n{'=' * 100}")
print(f"SUMMARY:")
print(f"  Total batches: {len(batches)}")
print(f"  Successful batches: {len(batches) - len(failed_batches)}")
print(f"  Failed batches: {len(failed_batches)}")
if failed_batches:
    for fb in failed_batches:
        print(f"    - {fb}")
print(f"  Variables extracted: {len(filtered)}/51")
print(f"  Completion rate: {len(filtered)/51*100:.1f}%")
print(f"{'=' * 100}")
