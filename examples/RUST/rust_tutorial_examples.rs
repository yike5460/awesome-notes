// This file contains examples of core Rust concepts for beginners to explore

// 1. Variables and data types
fn variables_and_types() {
    let x = 5; // Immutable by default
    let mut y = 10; // Mutable variable
    y += 1;
    
    let float: f64 = 3.14;
    let boolean: bool = true;
    let character: char = 'A';
    
    println!("x: {}, y: {}, float: {}, boolean: {}, character: {}", x, y, float, boolean, character);
}

// 2. Functions
fn add(a: i32, b: i32) -> i32 {
    a + b // Implicit return
}

// 3. Control flow
fn control_flow(num: i32) {
    if num > 0 {
        println!("Positive");
    } else if num < 0 {
        println!("Negative");
    } else {
        println!("Zero");
    }

    for i in 0..5 {
        println!("Loop iteration: {}", i);
    }
}

// 4. Ownership and borrowing
fn ownership_example() {
    let s1 = String::from("hello");
    let s2 = s1; // s1 is moved to s2
    // println!("{}", s1); // This would cause an error
    println!("{}", s2);

    let s3 = String::from("world");
    let len = calculate_length(&s3); // Borrowing s3
    println!("The length of '{}' is {}.", s3, len);
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

// 5. Structs and methods
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

// 6. Enums and pattern matching
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

// 7. Error handling
use std::fs::File;

fn error_handling_example() {
    let f = File::open("hello.txt");
    
    let f = match f {
        Ok(file) => file,
        Err(error) => {
            panic!("Problem opening the file: {:?}", error)
        },
    };
}

// 8. Generics and traits
trait Summarizable {
    fn summary(&self) -> String;
}

struct NewsArticle {
    headline: String,
    location: String,
    author: String,
    content: String,
}

impl Summarizable for NewsArticle {
    fn summary(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

// Main function to demonstrate usage
fn main() {
    variables_and_types();
    
    let sum = add(5, 10);
    println!("Sum: {}", sum);
    
    control_flow(7);
    
    ownership_example();
    
    let rect = Rectangle { width: 30, height: 50 };
    println!("Rectangle area: {}", rect.area());
    
    let coin = Coin::Dime;
    println!("Coin value: {} cents", value_in_cents(coin));
    
    error_handling_example();
    
    let article = NewsArticle {
        headline: String::from("Rust 1.0 Released"),
        location: String::from("San Francisco"),
        author: String::from("Jane Doe"),
        content: String::from("Rust 1.0 has been released with exciting new features..."),
    };
    println!("Article summary: {}", article.summary());
}