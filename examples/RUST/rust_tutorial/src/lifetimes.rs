/* Lifetimes in Rust
Lifetimes are Rust's way of ensuring that references are valid for as long as they're used

Typical usage of lifetimes:
1. In struct definitions when the struct holds references
2. In function signatures when the function returns a reference
3. In impl blocks when implementing methods that use references

Lifetime elision rules:
Rust has some built-in rules for inferring lifetimes, which means you don't always need to write them explicitly:
1. Each parameter that is a reference gets its own lifetime parameter
2. If there is exactly one input lifetime parameter, that lifetime is assigned to all output lifetime parameters
3. If there are multiple input lifetime parameters, but one of them is &self or &mut self, the lifetime of self is assigned to all output lifetime parameters

Error-prone mistakes for new learners:
1. Forgetting to annotate lifetimes when necessary
2. Misunderstanding the relationship between lifetimes of different references
3. Trying to use a reference that outlives its referred value
4. Overcomplicating lifetime annotations when the elision rules would suffice
5. Not understanding that lifetimes are part of the type system and affect how long references can be used

Advanced concept: 'static lifetime
The 'static lifetime denotes that the reference can live for the entire duration of the program
let s: &'static str = "I have a static lifetime.";

Remember: The borrow checker in Rust uses lifetime annotations to ensure all borrows are valid
Lifetimes are typically inferred by the compiler, but sometimes need to be specified explicitly
*/

// Lifetime annotations in struct definitions
// The 'a is a lifetime parameter
#[allow(dead_code)]
struct ImportantExcerpt<'a> { // Removed generic type parameter T
    // The 'a specifies the lifetime of references within the struct
    part: &'a str, // This reference must live at least as long as the struct
}

// Function with lifetime annotations
// This function takes two string slices and returns a string slice
// The lifetime 'a indicates that the returned reference will be valid for the smaller of the lifetimes of x and y
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    // 'a is a lifetime parameter, used to ensure references are valid for the entire function
    // <T> would be a type parameter, allowing the function to work with different types
    // & indicates that x and y are references, not owned values
    // &'a str means a reference to a str with lifetime 'a
    // -> &'a str means the function returns a reference with the same lifetime 'a
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

    // Error-prone scenario: Attempting to use a reference that outlives its value
    // let result;
    // {
    //     let s3 = String::from("short-lived");
    //     result = longest(&s1, &s3);
    // } // s3 goes out of scope here
    // println!("Longest string: {}", result); // This would cause a compile-time error
}
