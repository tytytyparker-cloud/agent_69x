import pytest
import cloak
from unittest.mock import patch

@pytest.fixture
def mock_data():
    return [
        {
            "id": 10,
            "name": "Tactic 10",
            "description": "Description 10",
            "techniques": [
                {
                    "id": 101,
                    "name": "Technique 101",
                    "description": "Technical description here",
                    "type": "technical",
                    "procedures": [
                        {
                            "id": "P-101-1",
                            "name": "Procedure 101-1",
                            "description": "Step by step procedure"
                        }
                    ],
                    "subtechniques": [
                        {
                            "id": 1011,
                            "name": "Subtechnique 1011",
                            "description": "Detailed sub-description",
                            "type": "behavioral",
                            "procedures": [
                                {
                                    "id": "P-1011-1",
                                    "name": "Procedure 1011-1",
                                    "description": "Nested procedure"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": 102,
                    "name": "Technique 102",
                    "description": "Physical description here",
                    "type": "physical",
                    "subtechniques": []
                }
            ]
        }
    ]

@pytest.fixture(autouse=True)
def patch_load(mock_data):
    with patch("cloak._load", return_value=mock_data):
        # Reset cache if it exists to ensure mock data is used
        cloak._cache = None
        yield

def test_tactics():
    results = cloak.tactics()
    assert len(results) == 1
    assert results[0]["id"] == 10
    assert results[0]["name"] == "Tactic 10"

def test_search_technique_keyword():
    results = cloak.search("Technical")
    assert len(results) == 1
    assert results[0]["level"] == "technique"
    assert results[0]["name"] == "Technique 101"

def test_search_subtechnique_keyword():
    results = cloak.search("Detailed")
    assert len(results) == 1
    assert results[0]["level"] == "subtechnique"
    assert results[0]["name"] == "Subtechnique 1011"

def test_search_procedure_keyword():
    results = cloak.search("Step by step")
    assert len(results) == 1
    assert results[0]["level"] == "procedure"
    assert results[0]["name"] == "Procedure 101-1"

def test_search_case_insensitivity():
    results_lower = cloak.search("technical")
    results_upper = cloak.search("TECHNICAL")
    assert results_lower == results_upper
    assert len(results_lower) == 1

def test_search_type_filter_technical():
    results = cloak.search("Technique", type_filter="technical")
    assert len(results) == 1
    assert results[0]["name"] == "Technique 101"

def test_search_type_filter_behavioral():
    # Searching for something that exists but filtered out
    results = cloak.search("Subtechnique", type_filter="technical")
    assert len(results) == 0

    results = cloak.search("Subtechnique", type_filter="behavioral")
    assert len(results) == 1
    assert results[0]["name"] == "Subtechnique 1011"

def test_search_type_filter_physical():
    results = cloak.search("Technique", type_filter="physical")
    assert len(results) == 1
    assert results[0]["name"] == "Technique 102"

def test_tactic_detail():
    t = cloak.tactic_detail(10)
    assert t is not None
    assert t["name"] == "Tactic 10"

    assert cloak.tactic_detail(999) is None

def test_stats():
    s = cloak.stats()
    assert s["tactics"] == 1
    assert s["techniques"] == 2
    assert s["subtechniques"] == 1
    assert s["procedures"] == 2
    assert s["types"]["technical"] == 1
    assert s["types"]["behavioral"] == 1
    assert s["types"]["physical"] == 1
