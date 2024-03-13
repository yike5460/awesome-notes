import sys
sys.path.append('ut_sample')

from foo import add

def test_add():
    assert add(1, 2) == 3
