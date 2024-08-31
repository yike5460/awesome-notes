fn main() {
    // Ownership
    let s1 = String::from("hello");
    let s2 = s1; // s1 is moved to s2
    // println!("{}", s1); // This would cause an error
    println!("{}", s2);

    // Borrowing
    let s3 = String::from("world");
    let len = calculate_length(&s3);
    println!("The length of '{}' is {}.", s3, len);

    // Mutable borrowing
    let mut s4 = String::from("hello");
    change(&mut s4);
    println!("Changed string: {}", s4);

    // Slices
    let s5 = String::from("hello world");
    let hello = &s5[0..5];
    let world = &s5[6..11];
    println!("Slices: '{}' and '{}'", hello, world);
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn change(s: &mut String) {
    s.push_str(", world");
}