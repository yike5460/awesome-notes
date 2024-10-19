// Basic Syntax and Concepts in Rust

fn main() {
    // Variables and mutability
    let x = 5; // Immutable by default
    let mut y = 10; // Mutable variable
    y += 1; // This is allowed because y is mutable
    // x += 1; // This would cause a compile-time error

    // Data types
    let integer: i32 = 42; // 32-bit signed integer
    let float: f64 = 3.14; // 64-bit floating point
    let boolean: bool = true; // Boolean type
    let character: char = 'A'; // Unicode scalar value

    // Function call
    let sum = add(5, 10);

    // Control flow
    if sum > 10 {
        println!("Sum is greater than 10");
    } else {
        println!("Sum is not greater than 10");
    }

    // Loop (for loop with range)
    // Range 0..5 is exclusive of 5
    for i in 0..5 {
        println!("Loop iteration: {}", i);
    }

    // Printing variables
    // The {} in the format string are placeholders for the variables
    println!("x: {}, y: {}, sum: {}", x, y, sum);
    println!("integer: {}, float: {}, boolean: {}, character: {}", integer, float, boolean, character);
}

// Function definition
// The -> i32 specifies the return type
fn add(a: i32, b: i32) -> i32 {
    a + b // Implicit return (no semicolon)
}

// Typical usage:
// - Variables: Use 'let' for declaration, 'mut' for mutable variables
// - Data types: Rust has a strong, static type system. Type annotations are often optional due to type inference
// - Functions: Define with 'fn', specify parameter types and return type
// - Control flow: Use 'if', 'else', 'for', 'while', and 'loop' for program flow
// - Printing: Use 'println!' macro for formatted output

// Error-prone mistakes for new learners:
// 1. Forgetting to make variables mutable when they need to be changed
// 2. Misunderstanding the difference between statements and expressions
//    (e.g., forgetting to omit semicolon for implicit return)
// 3. Incorrect use of ranges in for loops (e.g., confusing 0..5 with 0..=5)
// 4. Forgetting to specify the type when type inference isn't possible
// 5. Misusing the println! macro format strings
// 6. Attempting to use variables before they're initialized
// 7. Shadowing variables unintentionally
