// Testing and Documentation in Rust

/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// let result = testing::add(2, 2);
/// assert_eq!(result, 4);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Greets a person by name.
///
/// # Arguments
///
/// * `name` - A string slice that holds the name of the person
///
/// # Examples
///
/// ```
/// let greeting = testing::greet("Alice");
/// assert_eq!(greeting, "Hello, Alice!");
/// ```
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Test module
#[cfg(test)]
mod tests {
    use super::*;

    // Basic test
    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    // Test with negative numbers
    #[test]
    fn test_add_negative() {
        assert_eq!(add(-1, -2), -3);
    }

    // Test for the greet function
    #[test]
    fn test_greet() {
        assert_eq!(greet("World"), "Hello, World!");
    }

    // Test that expects a panic
    #[test]
    #[should_panic(expected = "Panic message")]
    fn test_panic() {
        panic!("Panic message");
    }

    // Test that returns a Result
    #[test]
    fn test_result() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }
}

fn main() {
    println!("This file is mainly for testing and documentation.");
    println!("Run 'cargo test' to execute the tests.");
    println!("Run 'cargo doc' to generate the documentation.");
}

/*
Typical usage:
- Unit tests: Test individual functions or small components
- Integration tests: Test how multiple parts of the library work together
- Documentation tests: Ensure examples in documentation are correct and up-to-date
- Benchmark tests: Measure performance of code (requires nightly Rust)

Error-prone mistakes for new learners:
1. Forgetting to use the #[cfg(test)] attribute for the test module
2. Not using assert! or assert_eq! macros in tests
3. Overlooking edge cases in tests
4. Writing tests that depend on external state or each other
5. Not testing both success and failure cases
6. Forgetting to run tests frequently during development

Advanced testing concepts:
- Test organization: Separating unit tests and integration tests
- Test helpers: Writing helper functions to reduce duplication in tests
- Conditional compilation: Using cfg attributes to compile code only for tests
- Ignoring tests: Using #[ignore] attribute for long-running tests

Remember: Tests are crucial for maintaining code quality and preventing regressions.
Write tests as you develop features to catch issues early and document expected behavior.
*/
