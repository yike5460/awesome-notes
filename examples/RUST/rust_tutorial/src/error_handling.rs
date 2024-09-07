use std::fs::File;
use std::io::{self, Read};

fn main() {
    // Using panic!
    // panic!("crash and burn");

    // Using Result for recoverable errors
    let f = File::open("hello.txt");
    let f = match f {
        Ok(file) => file,
        Err(error) => {
            println!("Error opening file: {:?}", error);
            return;
        }
    };

    // Using the ? operator for error propagation
    match read_username_from_file() {
        Ok(username) => println!("Username: {}", username),
        Err(error) => println!("Error reading username: {:?}", error),
    }
}

fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}