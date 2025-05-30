import pytest
from src.util.detector import detect_duplicates

def make_bib(entries):
    chunks = []
    for key, doi in entries:
        chunk = "@article{" + key + ",\n"
        if doi is not None:
            chunk += f"doi = {{{doi}}},\n"
        chunk += "}\n"
        chunks.append(chunk)
    return "\n".join(chunks)

@pytest.mark.unit
def test_empty_input_raises():
    with pytest.raises(ValueError):
        detect_duplicates("")

@pytest.mark.unit
def test_single_article_no_duplicates():
    data = make_bib([("A", None)])
    assert detect_duplicates(data) == []

@pytest.mark.unit
@pytest.mark.parametrize("entries, expected_keys", [
    # TC-3: two different keys, no DOIs → no duplicates
    ([("A", None), ("B", None)], []),
    # TC-4: same key, no DOIs → duplicate
    ([("A", None), ("A", None)], ["A"]),
    # TC-5: same key + same DOI → duplicate (parser drops DOI)
    ([("A", "10/x"), ("A", "10/x")], ["A"]),
    # TC-6: same key + different DOI → duplicate (parser ignores DOI)
    ([("A", "10/x"), ("A", "10/y")], ["A"]),
    # TC-7: different keys + same DOI → no duplicates
    ([("A", "10/x"), ("B", "10/x")], []),
])
def test_pairwise_duplicates(entries, expected_keys):
    result = detect_duplicates(make_bib(entries))
    assert [a.key for a in result] == expected_keys

@pytest.mark.unit
def test_three_entries_single_duplicate():
    # TC-8: three entries with A twice → only one duplicate flagged
    entries = [("A", None), ("B", None), ("A", None)]
    result = detect_duplicates(make_bib(entries))
    assert [a.key for a in result] == ["A"]
