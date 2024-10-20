#![allow(dead_code)]

// Advanced Features in Rust

/*
Advanced traits: Associated types
Associated types allow you to specify placeholder types in trait definitions
*/
trait Iterator {
    type Item; // Associated type
    fn next(&mut self) -> Option<Self::Item>;
}

/*
Default type parameters
You can specify default types for generic type parameters
*/
trait Add<RHS=Self> {
    type Output;
    fn add(self, rhs: RHS) -> Self::Output;
}

// Fully qualified syntax for disambiguation
trait Animal {
    fn baby_name() -> String;
}

struct Dog;

impl Dog {
    fn baby_name() -> String {
        String::from("Spot")
    }
}

impl Animal for Dog {
    fn baby_name() -> String {
        String::from("puppy")
    }
}

/*
Supertraits: Requiring one trait's functionality within another trait
*/
trait OutlinePrint: std::fmt::Display {
    fn outline_print(&self) {
        let output = self.to_string();
        let len = output.len();
        println!("{}", "*".repeat(len + 4));
        println!("*{}*", " ".repeat(len + 2));
        println!("* {} *", output);
        println!("*{}*", " ".repeat(len + 2));
        println!("{}", "*".repeat(len + 4));
    }
}

// Newtype pattern: Creating a new type for external trait implementation
struct Wrapper(Vec<String>);

impl std::fmt::Display for Wrapper {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}

// The Never type: For functions that never return
fn bar() -> ! {
    panic!("This call never returns!");
}

// Function pointers
fn add_one(x: i32) -> i32 {
    x + 1
}

fn do_twice(f: fn(i32) -> i32, arg: i32) -> i32 {
    f(arg) + f(arg)
}

// Returning closures
fn returns_closure() -> Box<dyn Fn(i32) -> i32> {
    Box::new(|x| x + 1)
}

// Type aliases for improved readability
struct Kilometers(i32);

fn main() {
    // Using fully qualified syntax
    println!("Dog's baby name: {}", <Dog as Animal>::baby_name());

    // Using the newtype pattern
    let w = Wrapper(vec![String::from("hello"), String::from("world")]);
    println!("w = {}", w);

    // Using the Kilometers newtype
    let kilometers = Kilometers(5);
    println!("5 kilometers is {} kilometers", kilometers.0);

    // Using function pointers
    let answer = do_twice(add_one, 5);
    println!("The answer is: {}", answer);

    // Using returned closures
    let closure = returns_closure();
    println!("Closure result: {}", closure(5));
}

/*
Typical usage:
- Associated types: When a trait has a type that's determined by the implementor
- Default type parameters: For reducing boilerplate in common cases
- Fully qualified syntax: When you need to disambiguate between multiple implementations
- Supertraits: When one trait depends on another trait's functionality
- Newtype pattern: For implementing external traits on external types
- Never type: For functions that are intended to never return (e.g., continuous loops, panics)
- Function pointers: When you want to pass functions as arguments
- Returning closures: When you need to return a function-like object from a function

Error-prone mistakes for new learners:
1. Forgetting to use fully qualified syntax when there are naming conflicts
2. Misusing the newtype pattern and losing the functionality of the wrapped type
3. Incorrectly implementing supertraits
4. Misunderstanding the behavior of the Never type
5. Confusing function pointers with closures
6. Not using the correct trait bounds when returning closures
7. Overusing advanced features when simpler solutions would suffice

Remember: These advanced features are powerful but can make code more complex.
Use them judiciously and only when they provide clear benefits to your code structure.
*/
