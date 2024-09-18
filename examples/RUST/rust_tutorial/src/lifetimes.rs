// Lifetime annotations in struct definitions
#[allow(dead_code)]
struct ImportantExcerpt<'a> {
    part: &'a str,
}

// Function with lifetime annotations
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let _i = ImportantExcerpt {
        part: first_sentence,
    };

    let s1 = String::from("short");
    let s2 = String::from("longer");
    let result = longest(&s1, &s2);
    println!("Longest string: {}", result);
}