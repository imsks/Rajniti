#!/usr/bin/env python3
"""
Standalone test script for the enhanced Candidate model.
This script validates all the new fields without requiring database setup.
"""

import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import only the models module to avoid database initialization
import importlib.util

spec = importlib.util.spec_from_file_location(
    "candidate_models", project_root / "app" / "models" / "candidate.py"
)
candidate_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate_models)

# Import the classes we need
Candidate = candidate_models.Candidate
CandidateStatus = candidate_models.CandidateStatus
CandidateType = candidate_models.CandidateType
EducationBackground = candidate_models.EducationBackground
PoliticalBackground = candidate_models.PoliticalBackground
PoliticalElectionHistory = candidate_models.PoliticalElectionHistory
FamilyBackground = candidate_models.FamilyBackground
FamilyMember = candidate_models.FamilyMember
Assets = candidate_models.Assets
BankDetails = candidate_models.BankDetails


def test_basic_candidate():
    """Test basic candidate creation"""
    print("🧪 Test 1: Basic candidate creation...")
    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        type=CandidateType.MP,
    )
    assert candidate.id == "C001"
    assert candidate.name == "Test Candidate"
    assert candidate.education_background is None
    print("   ✅ PASSED")


def test_education_background():
    """Test candidate with education background"""
    print("🧪 Test 2: Education background...")
    education = EducationBackground(
        graduation_year=2000,
        stream="Political Science",
        college_or_school="Delhi University",
    )
    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        education_background=education,
    )
    assert candidate.education_background.graduation_year == 2000
    assert candidate.education_background.stream == "Political Science"
    print("   ✅ PASSED")


def test_political_background():
    """Test candidate with political background"""
    print("🧪 Test 3: Political background...")
    election1 = PoliticalElectionHistory(
        election_year=2019,
        election_type="MP",
        constituency="Delhi-1",
        party="Party A",
        status="WON",
    )
    election2 = PoliticalElectionHistory(
        election_year=2014,
        election_type="MLA",
        constituency="Delhi-1A",
        party="Party A",
        status="LOST",
    )
    political_bg = PoliticalBackground(elections=[election1, election2])
    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        political_background=political_bg,
    )
    assert len(candidate.political_background.elections) == 2
    assert candidate.political_background.elections[0].election_year == 2019
    print("   ✅ PASSED")


def test_family_background():
    """Test candidate with family background"""
    print("🧪 Test 4: Family background...")
    father = FamilyMember(name="Father Name", profession="Businessman")
    mother = FamilyMember(name="Mother Name", profession="Teacher")
    spouse = FamilyMember(name="Spouse Name", profession="Doctor")
    child1 = FamilyMember(name="Child 1", profession="Student")

    family_bg = FamilyBackground(
        father=father, mother=mother, spouse=spouse, children=[child1]
    )
    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        family_background=family_bg,
    )
    assert candidate.family_background.father.name == "Father Name"
    assert candidate.family_background.mother.profession == "Teacher"
    assert len(candidate.family_background.children) == 1
    print("   ✅ PASSED")


def test_assets():
    """Test candidate with assets"""
    print("🧪 Test 5: Assets information...")
    bank1 = BankDetails(
        bank_name="State Bank of India", account_number="XXXX1234", branch="Delhi Main"
    )
    assets = Assets(
        commercial_assets="2 shops in Commercial Complex",
        cash_assets="Rs. 50,00,000 in savings",
        bank_details=[bank1],
    )
    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        assets=assets,
    )
    assert candidate.assets is not None
    assert "shops" in candidate.assets.commercial_assets
    assert len(candidate.assets.bank_details) == 1
    print("   ✅ PASSED")


def test_complete_candidate():
    """Test candidate with all fields"""
    print("🧪 Test 6: Complete candidate with all fields...")
    education = EducationBackground(
        graduation_year=2000,
        stream="Political Science",
        college_or_school="Delhi University",
    )
    election = PoliticalElectionHistory(
        election_year=2019,
        election_type="MP",
        constituency="Delhi-1",
        party="Party A",
        status="WON",
    )
    political_bg = PoliticalBackground(elections=[election])
    family_bg = FamilyBackground(
        father=FamilyMember(name="Father Name", profession="Businessman"),
        mother=FamilyMember(name="Mother Name", profession="Teacher"),
    )
    assets = Assets(
        commercial_assets="Properties",
        cash_assets="Savings",
        bank_details=[BankDetails(bank_name="SBI", branch="Delhi")],
    )

    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        image_url="http://example.com/image.jpg",
        education_background=education,
        political_background=political_bg,
        family_background=family_bg,
        assets=assets,
    )

    assert candidate.id == "C001"
    assert candidate.education_background.graduation_year == 2000
    assert len(candidate.political_background.elections) == 1
    assert candidate.family_background.father.name == "Father Name"
    assert candidate.assets.commercial_assets == "Properties"
    print("   ✅ PASSED")


def test_json_serialization():
    """Test JSON serialization"""
    print("🧪 Test 7: JSON serialization...")
    education = EducationBackground(
        graduation_year=2000,
        stream="Political Science",
        college_or_school="Delhi University",
    )
    candidate = Candidate(
        id="C001",
        name="Test Candidate",
        party_id="P001",
        constituency_id="CON001",
        state_id="DL",
        status=CandidateStatus.WON,
        education_background=education,
    )

    json_data = candidate.model_dump()
    assert json_data["id"] == "C001"
    assert json_data["education_background"]["graduation_year"] == 2000

    json_str = candidate.model_dump_json()
    assert "C001" in json_str
    assert "Political Science" in json_str
    print("   ✅ PASSED")


def test_partial_fields():
    """Test partial field population"""
    print("🧪 Test 8: Partial field population...")
    education = EducationBackground(stream="Political Science")
    assert education.graduation_year is None
    assert education.college_or_school is None

    family = FamilyBackground(
        father=FamilyMember(name="Father Name"),
        spouse=FamilyMember(profession="Doctor"),
    )
    assert family.father.profession is None
    assert family.spouse.name is None
    assert family.mother is None
    assert len(family.children) == 0
    print("   ✅ PASSED")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Testing Enhanced Candidate Model")
    print("=" * 60 + "\n")

    try:
        test_basic_candidate()
        test_education_background()
        test_political_background()
        test_family_background()
        test_assets()
        test_complete_candidate()
        test_json_serialization()
        test_partial_fields()

        print("\n" + "=" * 60)
        print("✨ All tests passed successfully! ✨")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
