use std::collections::HashMap;

fn main() {
    // Vector example
    // Vectors are resizable arrays stored on the heap
    let mut numbers = vec![1, 2, 3, 4, 5];
    numbers.push(6); // Adds an element to the end of the vector
    println!("Vector: {:?}", numbers);

    // Accessing elements
    let third = &numbers[2]; // Indexing starts at 0
    println!("The third element is {}", third);

    // Safe access with get() method
    // get() returns an Option<&T>, which is safer than direct indexing
    match numbers.get(100) {
        Some(value) => println!("The 101st element is {}", value),
        None => println!("There is no 101st element"),
    }

    // Iterating over a vector
    // This creates an immutable reference to each element
    for number in &numbers {
        println!("{}", number);
    }

    // String example
    // String is a growable, UTF-8 encoded text type stored on the heap
    let mut s = String::from("Hello");
    s.push_str(", world!"); // Appends a string slice
    println!("{}", s);

    // Concatenation
    // Note: + operator takes ownership of the first string
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");
    let s3 = s1 + &s2; // s1 has been moved here and can no longer be used
    println!("{}", s3);

    // HashMap example
    // HashMaps store key-value pairs with O(1) average case lookup time
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    // Accessing values
    let team_name = String::from("Blue");
    let score = scores.get(&team_name); // get() returns an Option<&V>

    match score {
        Some(s) => println!("Blue team's score: {}", s),
        None => println!("Blue team not found"),
    }

    // Updating a HashMap
    // entry() and or_insert() provide a convenient way to update values
    scores.entry(String::from("Yellow")).or_insert(50); // Only inserts if the key isn't present
    scores.entry(String::from("Blue")).or_insert(50); // This won't change the existing value

    println!("{:?}", scores);
}

// Typical usage:
// - Vectors: For storing lists of the same type that can grow or shrink
// - Strings: For storing and manipulating UTF-8 encoded text
// - HashMaps: For storing key-value pairs with efficient lookups

// Error-prone mistakes for new learners:
// 1. Forgetting that indexing a vector can panic if the index is out of bounds
// 2. Not understanding the ownership rules when working with Strings (e.g., using + operator)
// 3. Forgetting to handle the Option returned by HashMap's get() method
// 4. Mistakenly using String literals instead of String types as HashMap keys
// 5. Not considering the performance implications of different collection types
// 6. Trying to modify a collection while iterating over it without using proper methods
