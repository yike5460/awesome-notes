/* Generics and Traits in Rust
Note: The above function allows for different types that implement Summary
to be used in the same collection, demonstrating dynamic dispatch.
This is useful when you need to work with multiple types that share a common trait
at runtime, but don't know the exact types at compile time.
The 'dyn' keyword is used to create a trait object, enabling dynamic dispatch.

Typical usage of generics and traits:
- Use generics when you want to write code that can work with multiple types
- Use traits to define shared behavior between different types
- Use trait bounds to specify what functionality a type must have
- Use trait objects when you need runtime polymorphism

Error-prone mistakes for new learners:
1. Forgetting to implement all required methods of a trait
2. Misunderstanding the difference between static and dynamic dispatch
3. Overcomplicating generic constraints when simpler bounds would suffice
4. Not considering performance implications of dynamic dispatch vs static dispatch
5. Forgetting that each generic parameter must be used at least once in the function signature
*/

/*
Generic struct definition
The <T> after the struct name indicates that T is a type parameter
The #[allow(dead_code)] attribute is an attribute macro in Rust.
It tells the compiler to suppress warnings about unused code (dead code) for the item it's attached to.
This is useful during development when you have code that isn't currently being used,
but you plan to use it in the future or want to keep it for reference.
*/
#[allow(dead_code)]
struct Point<T> {
    x: T,
    y: T,
}

/*
Implementing methods for a generic struct
Note: The impl block also needs to declare the type parameter <T>
*/
impl<T> Point<T> {
    // Generic constructor method
    // 'Self' is an alias for the type we're implementing methods for (Point<T> in this case)
    fn new(x: T, y: T) -> Self {
        Point { x, y }
    }
    
    /*
    You can add more methods here, potentially with constraints on T
    For example:
    fn distance(&self) -> f64 where T: Into<f64> + Copy {
        let x = self.x.into();
        let y = self.y.into();
        (x * x + y * y).sqrt()
    }
    This method would only be available for Points where T can be converted to f64
    */
}

/*
Trait definition
Traits define shared behavior across types, similar to interfaces in other languages
*/
trait Summary {
    // Trait methods can have a default implementation or be left unimplemented
    // Unimplemented methods act as abstract methods that must be defined by implementors
    fn summarize(&self) -> String;
    
    // Example of a default implementation
    // This can be overridden by implementors if needed
    fn default_summary(&self) -> String {
        String::from("(Read more...)")
    }
}

// Struct that will implement the Summary trait
#[allow(dead_code)]
struct NewsArticle {
    headline: String,
    location: String,
    author: String,
    content: String,
}

/*
Implementing the Summary trait for NewsArticle
This is how we define the behavior of the trait methods for a specific type
*/
impl Summary for NewsArticle {
    // Override the summarize method
    // We must implement this method as it has no default implementation
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location) // The '!' indicates that format! is a macro, not a regular function
    }
    // Note: We don't need to implement default_summary as it has a default implementation
    // However, we could override it here if we wanted to
}

// Generic function with trait bounds
// This function can work with any type T that implements the Summary trait
fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}

/*
Using trait bounds:
A trait bound is a constraint on a generic type parameter that specifies what traits the type must implement. It is used to ensure that the type has the necessary capabilities to be used in the context where the trait bound is specified.
Alternative syntax for multiple trait bounds:
<T: Display + Clone, U: Clone + Debug> specifies the trait bounds for T and U
- T must implement both Display and Clone traits
- U must implement both Clone and Debug traits

fn complex_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {
    // Display allows the type to be formatted as a string
    // Clone allows the type to be duplicated
    // Debug allows the type to be printed for debugging purposes

    // The function takes references to T and U (&T and &U)
    // This avoids taking ownership of the passed values

    // The function returns an i32 (32-bit signed integer)

    // Function body would go here
    // ...
}

// Alternative syntax using a where clause for improved readability:
fn complex_function_alt<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug
{
    // This achieves the same effect as the previous function
    // but separates the trait bounds from the function signature
    // This is often preferred when there are many or complex bounds

    // Function body would go here
    // ...
}
*/

fn main() {
    // Creating instances of the generic Point struct
    let _integer_point = Point::new(5, 10);
    let _float_point = Point::new(1.0, 4.0);
    
    /*
    Error-prone mistake: Mixing types in a Point
    let mixed_point = Point::new(5, 10.0); // This will not compile!
    Rust enforces that all instances of T in a single use of Point<T> are the same type
    To allow different types, you'd need to define Point with two type parameters: Point<T, U>
    */

    let article = NewsArticle {
        headline: String::from("Rust 1.0 Released"),
        location: String::from("San Francisco"),
        author: String::from("Jane Doe"),
        content: String::from("Rust 1.0 has been released with exciting new features..."),
    };

    // Using the generic function with a trait bound
    notify(&article);
    
    // We can also call the default implementation
    // This demonstrates how default implementations in traits work
    println!("Default summary: {}", article.default_summary());
    
    /*
    Error-prone mistake: Trying to use notify with a type that doesn't implement Summary
    let number = 42;
    notify(&number); // This will not compile!
    The notify function requires a type that implements Summary, which i32 does not
    This is a common mistake when working with trait bounds
    */
}

// Advanced usage: Trait objects for runtime polymorphism
fn _print_summaries(summaries: &[&dyn Summary]) {
    /*
    &[...] : Reference to a slice (dynamic-sized view into a contiguous sequence)
    &dyn Summary: Reference to a trait object of type Summary
    Combined: &[&dyn Summary] is a slice of trait object references
    This allows for a collection of different types that implement Summary
    */
    for item in summaries {
        println!("{}", item.summarize()); // The '!' is a macro invocation operator. println! is a macro, not a regular function.
    }
}
