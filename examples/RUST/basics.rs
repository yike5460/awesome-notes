fn main() {
    // Variables and mutability
    let x = 5;
    let mut y = 10;
    y += 1;

    // Data types
    let integer: i32 = 42;
    let float: f64 = 3.14;
    let boolean: bool = true;
    let character: char = 'A';

    // Function call
    let sum = add(5, 10);

    // Control flow
    if sum > 10 {
        println!("Sum is greater than 10");
    } else {
        println!("Sum is not greater than 10");
    }

    for i in 0..5 {
        println!("Loop iteration: {}", i);
    }

    // Printing variables
    println!("x: {}, y: {}, sum: {}", x, y, sum);
    println!("integer: {}, float: {}, boolean: {}, character: {}", integer, float, boolean, character);
}

// Function definition
fn add(a: i32, b: i32) -> i32 {
    a + b // Implicit return
}