from typing import List, Set, Any

from backend.HelperFunctions import HelperFunctions as hf

def test_findsubsets():
    subsets : List[Set[Any]] = hf.findsubsets("a")
    assert len(subsets) == 2
    assert subsets[0] == set()
    assert subsets[-1] == set("a")

    subsets : List[Set[Any]] = hf.findsubsets(set("a"))
    assert len(subsets) == 2
    assert subsets[0] == set()
    assert subsets[-1] == set("a")

    subsets : List[Set[Any]] = hf.findsubsets(["a", "b"])
    assert len(subsets) == 4
    assert subsets[-1] == set("ab")

def test_subsets_minus_one():
    s = set(["A", "B", "C"])
    subsets = hf.subsets_minus_one(s)

    assert len(subsets) == len(s)

    assert set(["A", "B"]) in subsets
    assert set(["A", "C"]) in subsets
    assert set(["B", "C"]) in subsets

    # Check that it also works for frozenset
    s = frozenset(["A", "B", "C"])
    subsets = hf.subsets_minus_one(s)

    assert len(subsets) == len(s)

    assert set(["A", "B"]) in subsets
    assert set(["A", "C"]) in subsets
    assert set(["B", "C"]) in subsets