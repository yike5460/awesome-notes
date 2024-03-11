import os
import sys

"""
This file includes several issues that ruff can automatically fix, such as:
    - Inconsistent indentation (mix of spaces and tabs)
    - Extra whitespace within and around parentheses
    - Missing whitespace around operators and after commas
    - Unnecessary imports (os and sys are imported but not used)
    - Unused variables (unused_var1 and unused_var2)
    - Long lines that exceed the recommended length
    - Unused function definitions (unused_function and messy_function)
"""


class ExampleClass:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def say_hello(self):
        greeting = "Hello, " + self.name + "!"
        print(greeting)


def calculate_sum(x, y):
    sum = x + y
    return sum


def unused_function():
    pass


# This is a poorly formatted function
def messy_function():
    x = {"a": 37, "b": 42, "c": 927}
    y = "hello " "world"
    z = "hello " + "world"
    a = "hello {}".format("world")

    class Foo(object):
        def f(self):
            return 37 * -+2

        def g(self, x, y=42):
            return y


def f(a):
    return 10


# Unused variables
unused_var1 = 123
unused_var2 = "Hello, World!"

# Long line
long_line = "This is a really really really really really really really really really really really long line."

if __name__ == "__main__":
    example = ExampleClass("John Doe", 42)
    example.say_hello()
    result = calculate_sum(5, 10)
    print("Sum is:", result)
