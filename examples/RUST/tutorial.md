# Comprehensive Rust Tutorial

This tutorial covers all core features of Rust, following the official Rust Developer Guide. Each section includes detailed explanations, typical usage scenarios, and links to sample code files for hands-on practice.

## 1. Introduction to Rust
- What is Rust? A systems programming language focused on safety, concurrency, and performance.
- Why use Rust? Memory safety without garbage collection, zero-cost abstractions, and modern language features.
- Installation and setup: Using rustup to install and manage Rust versions.

Typical usage: Systems programming, web assembly, command-line tools, and more.

[See introduction.rs for a "Hello, World!" example](introduction.rs)

## 2. Basic Syntax and Concepts
- Variables and mutability: Understanding let, mut, and constants.
- Data types: Integers, floating-point numbers, booleans, characters, and compound types.
- Functions: Defining functions, parameters, return values, and expressions.
- Control flow: if/else expressions, loops (for, while, loop), and match expressions.
- Comments: Line comments (//) and block comments (/* */).

Typical usage: These concepts form the foundation of any Rust program.

[Explore basic syntax in basics.rs](basics.rs)

## 3. Ownership and Borrowing
- Ownership rules: Each value has an owner, only one owner at a time, owner goes out of scope, value is dropped.
- References and borrowing: Creating references (&T) and mutable references (&mut T).
- The slice type: References to contiguous sequences in collections.

Typical usage: Managing memory safely without a garbage collector, preventing data races at compile time.

[Practice ownership concepts in ownership.rs](ownership.rs)

## 4. Structs and Enums
- Defining and instantiating structs: Custom data types to group related data.
- Method syntax: Implementing behavior for structs and enums.
- Enums and pattern matching: Defining types that can be one of several variants.

Typical usage: Creating custom types to model domain-specific data and behavior.

[See structs_enums.rs for examples](structs_enums.rs)

## 5. Modules and Packages
- Organizing code with modules: Controlling scope and privacy.
- Creating a package with Cargo: Managing dependencies and building projects.

Typical usage: Structuring large codebases, creating reusable libraries.

[Explore module organization in modules_example/](modules_example/)

## 6. Common Collections
- Vectors: Growable arrays (Vec<T>).
- Strings: Text stored as UTF-8 encoded bytes.
- Hash maps: Key-value stores (HashMap<K, V>).

Typical usage: Storing and manipulating collections of data efficiently.

[Practice using collections in collections.rs](collections.rs)

## 7. Error Handling
- panic! and unwinding: For unrecoverable errors.
- Result<T, E> for recoverable errors: Handling potential failures gracefully.
- Propagating errors with ?: Simplifying error handling in functions.

Typical usage: Robust error handling in applications, preventing crashes, and providing meaningful error messages.

[See error handling examples in error_handling.rs](error_handling.rs)

## 8. Generic Types and Traits
- Generic data types: Writing code that works with multiple types.
- Traits: Defining shared behavior across types.
- Trait bounds: Specifying constraints on generic types.

Typical usage: Writing flexible, reusable code that works with multiple types while maintaining type safety.

[Explore generics and traits in generics_traits.rs](generics_traits.rs)

## 9. Lifetimes
- Lifetime annotation syntax: Expressing the scope of references.
- Lifetime elision: Compiler rules for inferring lifetimes.

Typical usage: Ensuring references are valid for the duration they're used, preventing dangling references.

[Practice lifetimes in lifetimes.rs](lifetimes.rs)

## 10. Closures and Iterators
- Defining and using closures: Anonymous functions that can capture their environment.
- Iterators and the Iterator trait: Working with sequences of data.

Typical usage: Functional programming patterns, data processing pipelines.

[See closure and iterator examples in closures_iterators.rs](closures_iterators.rs)

## 11. Smart Pointers
- Box<T> for heap allocation: Storing data on the heap instead of the stack.
- Rc<T> for multiple ownership: Reference counted smart pointer.
- RefCell<T> and interior mutability: Allowing mutable borrows checked at runtime.

Typical usage: Managing heap data, implementing complex data structures, interior mutability pattern.

[Explore smart pointers in smart_pointers.rs](smart_pointers.rs)

## 12. Concurrency
- Threads and spawn: Creating and managing threads.
- Message passing with channels: Communicating between threads.
- Shared state concurrency: Using mutex and atomic types for safe shared access.

Typical usage: Parallel processing, responsive applications, utilizing multi-core processors.

[Practice concurrency in concurrency.rs](concurrency.rs)

## 13. Unsafe Rust
- When and why to use unsafe: Performing operations that the compiler can't guarantee are safe.
- Unsafe functions and methods: Defining functions that require careful use.
- Raw pointers: Direct memory access and manipulation.

Typical usage: Interfacing with C libraries, implementing low-level optimizations, building safe abstractions.

[See unsafe Rust examples in unsafe_rust.rs](unsafe_rust.rs)

## 14. Advanced Features
- Advanced traits: Associated types, default type parameters, fully qualified syntax.
- Advanced types: Newtype pattern, type aliases, the Never type, dynamically sized types.
- Advanced functions and closures: Function pointers and returning closures.

Typical usage: Building complex libraries, advanced API design, metaprogramming.

[Explore advanced features in advanced.rs](advanced.rs)

## 15. Testing and Documentation
- Writing and running tests: Unit tests, integration tests, and test organization.
- Documenting your code with rustdoc: Writing helpful documentation and generating HTML docs.

Typical usage: Ensuring code correctness, maintaining large codebases, creating user-friendly libraries.

[See testing examples in testing.rs](testing.rs)

To run any of these examples, use the command:
```
rustc filename.rs
./filename
```

Or if you have cargo installed
```
cargo run
```