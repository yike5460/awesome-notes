def add(a, b):
    return a + b

def cumulative_sum(numbers):
    total = 0
    for number in numbers:
        total = add(total, number)
    return total