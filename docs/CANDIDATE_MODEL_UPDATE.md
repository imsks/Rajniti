# Candidate Model Update - Detailed Information Fields

This document describes the enhancements made to the Candidate model to support comprehensive candidate profiles.

## Overview

The Candidate model has been enhanced to store detailed information about candidates including:
1. **Education Background** - Academic qualifications
2. **Political Background** - Electoral history
3. **Family Background** - Family members and their professions
4. **Assets** - Financial and commercial assets

## New Fields

All new fields are **optional** to allow incremental data population and maintain backward compatibility.

### 1. Education Background

Stores academic qualifications of the candidate.

**Fields:**
- `graduation_year` (int, optional): Year of graduation
- `stream` (str, optional): Field of study/stream
- `college_or_school` (str, optional): Name of educational institution

**Example:**
```python
education = EducationBackground(
    graduation_year=2000,
    stream="Political Science",
    college_or_school="Delhi University"
)
```

### 2. Political Background

Stores complete electoral history of the candidate.

**Structure:**
- `elections` (list): List of PoliticalElectionHistory objects

**PoliticalElectionHistory Fields:**
- `election_year` (int, optional): Year of election
- `election_type` (str, optional): Type (MP, MLA, etc.)
- `constituency` (str, optional): Constituency name
- `party` (str, optional): Party represented
- `status` (str, optional): Result (WON/LOST)

**Example:**
```python
political_bg = PoliticalBackground(
    elections=[
        PoliticalElectionHistory(
            election_year=2019,
            election_type="MP",
            constituency="Varanasi",
            party="Bharatiya Janata Party",
            status="WON"
        )
    ]
)
```

### 3. Family Background

Stores information about family members.

**Fields:**
- `father` (FamilyMember, optional): Father's information
- `mother` (FamilyMember, optional): Mother's information
- `spouse` (FamilyMember, optional): Spouse's information
- `children` (list, optional): List of children

**FamilyMember Fields:**
- `name` (str, optional): Name of family member
- `profession` (str, optional): Profession of family member

**Example:**
```python
family_bg = FamilyBackground(
    father=FamilyMember(name="Father Name", profession="Businessman"),
    mother=FamilyMember(name="Mother Name", profession="Teacher"),
    spouse=FamilyMember(name="Spouse Name", profession="Doctor"),
    children=[
        FamilyMember(name="Child 1", profession="Student")
    ]
)
```

### 4. Assets

Stores financial and commercial asset information.

**Fields:**
- `commercial_assets` (str, optional): Description of commercial assets
- `cash_assets` (str, optional): Description of cash assets
- `bank_details` (list, optional): List of BankDetails objects

**BankDetails Fields:**
- `bank_name` (str, optional): Name of the bank
- `account_number` (str, optional): Account number
- `branch` (str, optional): Branch name

**Example:**
```python
assets = Assets(
    commercial_assets="2 shops in Commercial Complex",
    cash_assets="Rs. 50,00,000 in savings",
    bank_details=[
        BankDetails(
            bank_name="State Bank of India",
            account_number="XXXX1234",
            branch="Delhi Main"
        )
    ]
)
```

## Database Schema

New JSON columns have been added to the `candidates` table:

```sql
ALTER TABLE candidates ADD COLUMN education_background JSON;
ALTER TABLE candidates ADD COLUMN political_background JSON;
ALTER TABLE candidates ADD COLUMN family_background JSON;
ALTER TABLE candidates ADD COLUMN assets JSON;
```

These columns use JSON type for flexibility and are compatible with both PostgreSQL (JSONB) and SQLite.

## API Usage

### Creating a Candidate with Detailed Information

```python
from app.database.models import Candidate
from app.database.session import get_db_session

education_data = {
    "graduation_year": 2000,
    "stream": "Political Science",
    "college_or_school": "Delhi University"
}

political_data = {
    "elections": [
        {
            "election_year": 2019,
            "election_type": "MP",
            "constituency": "Delhi-1",
            "party": "Party A",
            "status": "WON"
        }
    ]
}

with get_db_session() as session:
    candidate = Candidate.create(
        session=session,
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status="WON",
        type="MP",
        education_background=education_data,
        political_background=political_data
    )
    session.commit()
```

### Updating Candidate Information

```python
with get_db_session() as session:
    candidate = Candidate.get_by_id(session, "C001")
    
    family_data = {
        "father": {"name": "Father Name", "profession": "Businessman"}
    }
    
    candidate.update(session, family_background=family_data)
    session.commit()
```

### Querying Candidates

All existing queries work unchanged. The new fields are simply additional optional data:

```python
with get_db_session() as session:
    # Get candidate
    candidate = Candidate.get_by_id(session, "C001")
    
    # Access new fields
    if candidate.education_background:
        print(f"Graduated: {candidate.education_background['graduation_year']}")
    
    if candidate.political_background:
        elections = candidate.political_background.get('elections', [])
        print(f"Contested {len(elections)} elections")
```

## Migration

To apply the database migration:

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"

# Run migrations
alembic upgrade head
```

The migration is idempotent - it can be run multiple times safely.

## Testing

Run the standalone test suite:

```bash
python tests/test_candidate_models_standalone.py
```

See the example script for Perplexity agent integration:

```bash
python scripts/example_populate_candidate_data.py
```

## Integration with Perplexity Agent

The new fields are designed for population by the Perplexity AI agent. See `scripts/example_populate_candidate_data.py` for the recommended pattern:

1. **Incremental Population**: Populate fields one at a time
2. **Graceful Failures**: If data not found, field remains None
3. **Logging**: All operations are logged for visibility
4. **No Breaking Changes**: Existing code continues to work

Example workflow:
```python
# Try to populate education
try:
    education_data = fetch_from_perplexity(f"education of {candidate_name}")
    candidate.update(education_background=education_data)
    logger.info("✅ Education data updated")
except Exception as e:
    logger.warning(f"⚠️  Could not fetch education: {e}")
    # Continue to next field - no problem!
```

## Benefits

1. **Comprehensive Profiles**: Users can access detailed candidate information
2. **Flexible Schema**: JSON fields allow schema evolution without migrations
3. **Easy Vectorization**: JSON data can be easily vectorized for ML/search
4. **API Friendly**: Simple to update via API endpoints
5. **Backward Compatible**: Existing code works without changes
6. **Logging**: Built-in logging provides visibility

## Future Enhancements

Potential future additions:
- Criminal records
- Property details
- Social media profiles
- Public appearances
- Parliamentary performance (for MPs)
- Assembly performance (for MLAs)

All can be added as additional optional JSON fields following the same pattern.
