import sys
sys.path.append('ut_sample')

from foo import cumulative_sum

def test_cumulative_sum_integration():
    numbers = [1, 2, 3, 4, 5]
    # The cumulative sum of [1, 2, 3, 4, 5] should be 15
    assert cumulative_sum(numbers) == 15

    # Testing with an empty list should return 0 (edge case)
    assert cumulative_sum([]) == 0

    # Testing with a list containing a single item should return that item (edge case)
    assert cumulative_sum([100]) == 100
