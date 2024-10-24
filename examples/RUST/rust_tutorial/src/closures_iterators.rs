/* Closures and Iterators in Rust

Typical usage:
- Closures: For short, anonymous functions that can capture their environment
  Often used with iterator methods like map, filter, and fold
- Iterators: For processing sequences of data efficiently
  Provide a uniform interface for working with various collections

Error-prone mistakes for new learners:
1. Forgetting that closures capture their environment by reference by default
   Use the 'move' keyword to force ownership of captured variables
2. Misunderstanding the difference between iter(), iter_mut(), and into_iter()
   iter() borrows, iter_mut() mutably borrows, into_iter() takes ownership
3. Forgetting to collect() when you need to create a new collection from an iterator
4. Trying to use a moved value after it's been consumed by into_iter()
5. Overlooking the lazy evaluation nature of iterators
   Iterator adaptors like map and filter don't do anything until the iterator is consumed
6. Not using iterator methods when they would be more efficient than manual loops
*/

fn main() {

    // Closures are anonymous functions that can capture their environment, definition schema:
    // let closure_name = |parameters| -> return_type { body };

    // Examples:
    let add_one = |x| x + 1; // Implicit return type and single expression body
    let _multiply = |x: i32, y: i32| -> i32 { x * y }; // Explicit parameter types and return type
    let _greet = || println!("Hello!"); // No parameters
    // Closure that captures a variable from its environment
    let y = 10;
    let capture_var = |x| x + y; // Captures 'y' from the environment
    println!("capture_var(5) = {}", capture_var(5)); // Outputs: capture_var(5) = 15

    // Closure that takes ownership of captured variables
    let z = String::from("Hello");
    let move_capture = move |x: &str| x.to_string() + &z; // Takes ownership of 'z'
    println!("move_capture(\"World\") = {}", move_capture("World")); // Outputs: move_capture("World") = WorldHello

    // After this point, 'z' is no longer accessible in this scope
    // Uncommenting the following line would result in a compile error:
    // println!("z = {}", z);

    /*
      Key differences:
      1. Without 'move': The closure borrows 'count', allowing it to be used outside the closure
      2. With 'move': The closure takes ownership of 'move_count', creating a separate instance
         inside the closure. The original variable remains unchanged in the outer scope.
      3. Use 'move' when you need the closure to own its captured variables, 
         such as when the closure outlives the current scope (e.g., in threads or async code)
      Example of how 'move' affects variable capture
    */

    // Without 'move': Closure borrows the variable
    let mut count = 0;
    let mut inc = || {
        count += 1; // Borrows 'count' mutably
        println!("Count: {}", count);
    };

    inc(); // Count: 1
    inc(); // Count: 2
    println!("Count after inc(): {}", count); // Count: 2
    // We can still use 'count' here because it was only borrowed, not moved

    // Using 'move': Closure takes ownership of the variable
    let mut move_count = 0;
    let mut move_inc = move || {
        move_count += 1; // 'move_count' is now owned by the closure
        println!("Move count: {}", move_count);
    };

    move_inc(); // Move count: 1
    move_inc(); // Move count: 2

    // The original 'move_count' is unchanged and still accessible
    println!("Original move_count: {}", move_count); // Original move_count: 0
    println!("Add one to 5: {}", add_one(5));

    // Closure that captures its environment
    // This closure can access variables from its enclosing scope
    let x = 4;
    let equal_to_x = |z| z == x;
    let y = 4;
    println!("Is y equal to x? {}", equal_to_x(y));

    // Iterator example
    // Iterators are used to process sequences of elements
    let v1 = vec![1, 2, 3]; // vec! is a macro that creates a new Vec with the given elements
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
    // Example: If v1 is [1, 2, 3], v2 will be [2, 3, 4]

    // Using filter
    // Use &&x or &x with iter() (borrowing)
    // Use &x with into_iter() (ownership)
    // Use &mut x with iter_mut() (mutable borrowing)
    let v3: Vec<i32> = v1.iter().filter(|&&x| x % 2 == 0).cloned().collect();
    println!("v3: {:?}", v3);
    // Example: If v1 is [1, 2, 3, 4], v3 will be [2, 4]

    // Using fold (reduce) to sum all elements
    let sum: i32 = v1.iter().fold(0, |acc, &x| acc + x);
    println!("Sum of v1: {}", sum);
    // Example: If v1 is [1, 2, 3], sum will be 6

    // Chaining multiple operations
    let v4: Vec<i32> = v1.iter()
        .map(|&x| x * 2)
        .filter(|&x| x > 3)
        .collect();
    println!("v4: {:?}", v4);
    // Example: If v1 is [1, 2, 3], v4 will be [4, 6]
}
