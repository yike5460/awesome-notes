// Define a generic struct
struct Point<T> {
    x: T,
    y: T,
}

// Implement methods for the generic struct
impl<T> Point<T> {
    fn new(x: T, y: T) -> Self {
        Point { x, y }
    }
}

// Define a trait
trait Summary {
    fn summarize(&self) -> String;
}

// Implement the trait for a struct
struct NewsArticle {
    headline: String,
    location: String,
    author: String,
    content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

// Generic function with trait bounds
fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}

fn main() {
    let integer_point = Point::new(5, 10);
    let float_point = Point::new(1.0, 4.0);

    let article = NewsArticle {
        headline: String::from("Rust 1.0 Released"),
        location: String::from("San Francisco"),
        author: String::from("Jane Doe"),
        content: String::from("Rust 1.0 has been released with exciting new features..."),
    };

    notify(&article);
}