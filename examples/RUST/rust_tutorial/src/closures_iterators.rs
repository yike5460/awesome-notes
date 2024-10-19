// Closures and Iterators in Rust

fn main() {
    // Closure example
    // Closures are anonymous functions that can capture their environment
    let add_one = |x| x + 1;
    println!("Add one to 5: {}", add_one(5));

    // Closure that captures its environment
    // This closure can access variables from its enclosing scope
    let x = 4;
    let equal_to_x = |z| z == x;
    let y = 4;
    println!("Is y equal to x? {}", equal_to_x(y));

    // Iterator example
    // Iterators are used to process sequences of elements
    let v1 = vec![1, 2, 3];
    let v1_iter = v1.iter(); // Creates an iterator over the vector

    // Using a for loop with an iterator
    // This is a common way to consume an iterator
    for val in v1_iter {
        println!("Got: {}", val);
    }

    // Using iterator adaptors
    // map() transforms each element, collect() consumes the iterator and creates a collection
    let v2: Vec<i32> = v1.iter().map(|x| x + 1).collect();
    println!("v2: {:?}", v2);

    // Using filter
    // filter() keeps elements that satisfy a predicate
    let v3: Vec<i32> = v1.into_iter().filter(|x| x % 2 == 0).collect();
    println!("v3: {:?}", v3);
}

// Typical usage:
// - Closures: For short, anonymous functions that can capture their environment
//   Often used with iterator methods like map, filter, and fold
// - Iterators: For processing sequences of data efficiently
//   Provide a uniform interface for working with various collections

// Error-prone mistakes for new learners:
// 1. Forgetting that closures capture their environment by reference by default
//    Use the 'move' keyword to force ownership of captured variables
// 2. Misunderstanding the difference between iter(), iter_mut(), and into_iter()
//    iter() borrows, iter_mut() mutably borrows, into_iter() takes ownership
// 3. Forgetting to collect() when you need to create a new collection from an iterator
// 4. Trying to use a moved value after it's been consumed by into_iter()
// 5. Overlooking the lazy evaluation nature of iterators
//    Iterator adaptors like map and filter don't do anything until the iterator is consumed
// 6. Not using iterator methods when they would be more efficient than manual loops
