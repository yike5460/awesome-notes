// Ownership is a key concept in Rust that ensures memory safety without a garbage collector

fn main() {
    // Ownership Rule 1: Each value in Rust has a variable that's called its owner.
    // Ownership Rule 2: There can only be one owner at a time.
    // Ownership Rule 3: When the owner goes out of scope, the value will be dropped.

    // Example of ownership and move semantics
    let s1 = String::from("hello"); // s1 owns the String
    let s2 = s1; // s1 is moved to s2, s1 is no longer valid
    // println!("{}", s1); // This would cause a compile-time error
    println!("{}", s2);

    // Borrowing: Allows you to refer to some value without taking ownership of it
    let s3 = String::from("world");
    let len = calculate_length(&s3); // &s3 creates a reference to s3
    println!("The length of '{}' is {}.", s3, len);

    // Mutable borrowing: Allows you to modify a borrowed value
    let mut s4 = String::from("hello");
    change(&mut s4);
    println!("Changed string: {}", s4);

    // Error-prone mistake: You can't have a mutable reference while you have an immutable one
    // let r1 = &s4;
    // let r2 = &s4;
    // let r3 = &mut s4; // This would cause a compile-time error
    // println!("{}, {}, and {}", r1, r2, r3);

    // Slices: References to a contiguous sequence of elements in a collection
    let s5 = String::from("hello world");
    let hello = &s5[0..5];
    let world = &s5[6..11];
    println!("Slices: '{}' and '{}'", hello, world);
}

// This function borrows s, which allows it to use the value without taking ownership
fn calculate_length(s: &String) -> usize {
    s.len()
} // s goes out of scope here, but since it doesn't have ownership of what
  // it refers to, nothing happens.

// This function takes a mutable reference, allowing it to modify the value it borrows
fn change(s: &mut String) {
    s.push_str(", world");
}

// Typical usage of ownership and borrowing:
// - Use ownership for functions that need to take ownership of values
// - Use borrowing for functions that only need to inspect values
// - Use mutable borrowing for functions that need to modify values without taking ownership
// - Use slices to operate on a portion of a collection without taking ownership

// Error-prone mistakes for new learners:
// 1. Trying to use a value after it has been moved
// 2. Forgetting to use & when you only need to borrow a value
// 3. Trying to modify a borrowed value without using &mut
// 4. Creating multiple mutable references to the same value in the same scope
// 5. Mixing mutable and immutable references in the same scope
// 6. Attempting to create dangling references (references that outlive the data they refer to)
// 7. Misunderstanding lifetimes and their impact on references
