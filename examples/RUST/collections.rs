use std::collections::HashMap;

fn main() {
    // Vector example
    let mut numbers = vec![1, 2, 3, 4, 5];
    numbers.push(6);
    println!("Vector: {:?}", numbers);

    // Accessing elements
    let third = &numbers[2];
    println!("The third element is {}", third);

    match numbers.get(100) {
        Some(value) => println!("The 101st element is {}", value),
        None => println!("There is no 101st element"),
    }

    // Iterating over a vector
    for number in &numbers {
        println!("{}", number);
    }

    // String example
    let mut s = String::from("Hello");
    s.push_str(", world!");
    println!("{}", s);

    // Concatenation
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");
    let s3 = s1 + &s2; // Note: s1 has been moved here and can no longer be used
    println!("{}", s3);

    // HashMap example
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    // Accessing values
    let team_name = String::from("Blue");
    let score = scores.get(&team_name);

    match score {
        Some(s) => println!("Blue team's score: {}", s),
        None => println!("Blue team not found"),
    }

    // Updating a HashMap
    scores.entry(String::from("Yellow")).or_insert(50);
    scores.entry(String::from("Blue")).or_insert(50);

    println!("{:?}", scores);
}