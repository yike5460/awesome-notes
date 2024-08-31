# Comprehensive Rust Tutorial

This tutorial covers all core features of Rust, following the official Rust Developer Guide. Each section includes explanations and links to sample code files for hands-on practice.

## 1. Introduction to Rust
- What is Rust?
- Why use Rust?
- Installation and setup

[See introduction.rs for a "Hello, World!" example](introduction.rs)

## 2. Basic Syntax and Concepts
- Variables and mutability
- Data types
- Functions
- Control flow (if, else, loops)
- Comments

[Explore basic syntax in basics.rs](basics.rs)

## 3. Ownership and Borrowing
- Ownership rules
- References and borrowing
- The slice type

[Practice ownership concepts in ownership.rs](ownership.rs)

## 4. Structs and Enums
- Defining and instantiating structs
- Method syntax
- Enums and pattern matching

[See structs_enums.rs for examples](structs_enums.rs)

## 5. Modules and Packages
- Organizing code with modules
- Creating a package with Cargo

[Explore module organization in modules_example/](modules_example/)

## 6. Common Collections
- Vectors
- Strings
- Hash maps

[Practice using collections in collections.rs](collections.rs)

## 7. Error Handling
- panic! and unwinding
- Result<T, E> for recoverable errors
- Propagating errors with ?

[See error handling examples in error_handling.rs](error_handling.rs)

## 8. Generic Types and Traits
- Generic data types
- Traits: defining shared behavior
- Trait bounds

[Explore generics and traits in generics_traits.rs](generics_traits.rs)

## 9. Lifetimes
- Lifetime annotation syntax
- Lifetime elision

[Practice lifetimes in lifetimes.rs](lifetimes.rs)

## 10. Closures and Iterators
- Defining and using closures
- Iterators and the Iterator trait

[See closure and iterator examples in closures_iterators.rs](closures_iterators.rs)

## 11. Smart Pointers
- Box<T> for heap allocation
- Rc<T> for multiple ownership
- RefCell<T> and interior mutability

[Explore smart pointers in smart_pointers.rs](smart_pointers.rs)

## 12. Concurrency
- Threads and spawn
- Message passing with channels
- Shared state concurrency

[Practice concurrency in concurrency.rs](concurrency.rs)

## 13. Unsafe Rust
- When and why to use unsafe
- Unsafe functions and methods
- Raw pointers

[See unsafe Rust examples in unsafe_rust.rs](unsafe_rust.rs)

## 14. Advanced Features
- Advanced traits
- Advanced types
- Advanced functions and closures

[Explore advanced features in advanced.rs](advanced.rs)

## 15. Testing and Documentation
- Writing and running tests
- Documenting your code with rustdoc

[See testing examples in testing.rs](testing.rs)

To run any of these examples, use the command:
```
rustc filename.rs
./filename
```

Or if