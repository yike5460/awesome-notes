use std::rc::Rc;
use std::cell::RefCell;

/* Smart Pointers in Rust

Typical usage of smart pointers:
- Box<T>: When you have a type whose size can't be known at compile time and you want to use it in a context that requires an exact size
- Rc<T>: When you need multiple ownership of data
- RefCell<T>: When you need mutable access to data that's behind a shared reference

Error-prone mistakes for new learners:
1. Forgetting that Box<T> is for single ownership scenarios
2. Creating reference cycles with Rc<T> which can lead to memory leaks
3. Overusing RefCell<T> when simple borrowing rules would suffice
4. Not understanding the runtime cost of RefCell<T>'s borrowing checks
5. Forgetting to clone Rc<T> when creating new references (use Rc::clone(&rc) instead of rc.clone())

Advanced concepts:
- Deref trait: Allows smart pointers to be treated like references
- Drop trait: Customizes what happens when a smart pointer goes out of scope

Remember: Smart pointers in Rust provide additional functionality beyond what references provide,
often with some runtime cost. Use them judiciously and understand their trade-offs.
*/


// Box<T> example
// Box<T> is a smart pointer that provides heap allocation
#[allow(dead_code)]
enum List {
    Cons(i32, Box<List>),
    /*
     * The Cons variant represents a non-empty list
     * It contains an i32 value and a Box<List> for the rest of the list
     * the i32 value is the head of the list used as a pointer to the next element and the Box<List> is the tail of the list
     * 'cons' comes from 'construct' in Lisp, used to create a new list
     * Box<List> allows for a known size at compile time by storing the next List on the heap
     * This prevents the "recursive type has infinite size" error
     */
    Nil,
}

#[allow(dead_code)]
#[derive(Debug)]
/*
The #[...] syntax in Rust is used for attributes. Attributes are metadata
applied to modules, crates, items, or expressions. They can:
1. Conditionally compile code
2. Set crate name, version, and type (binary or library)
3. Disable lints (warnings)
4. Enable compiler features (experimental APIs)
5. Link to a foreign library
6. Mark functions as unit tests
7. Mark functions to be part of a benchmark

The #[derive(...)] attribute is used to automatically implement traits.
Here, #[derive(Debug)] automatically implements the Debug trait for the struct,
allowing it to be printed with {:?} in format strings or with dbg! macro.
This is particularly useful for quick debugging of custom types.
*/
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>, // Mutable vector of shared ownership Nodes
    /*
     * This nested structure serves multiple purposes:
     * 1. Vec<...>: Allows for multiple children, creating a tree-like structure.
     * 2. Rc<Node>: Enables shared ownership of child nodes. Multiple parents can point to the same child.
     * 3. RefCell<...>: Provides interior mutability, allowing the children vector to be modified even when the Node is immutable.
     *
     * Sample data schema:
     * Node {
     *     value: 1,
     *     children: RefCell(vec![
     *         Rc(Node {
     *             value: 2,
     *             children: RefCell(vec![])
     *         }),
     *         Rc(Node {
     *             value: 3,
     *             children: RefCell(vec![
     *                 Rc(Node {
     *                     value: 4,
     *                     children: RefCell(vec![])
     *                 })
     *             ])
     *         })
     *     ])
     * }
     *
     * This structure allows for complex, mutable tree structures with shared nodes,
     * useful in scenarios like DOM trees, file systems, or any hierarchical data
     * that requires flexibility in modification and shared references.
     */
}

fn main() {
    // Box<T> usage
    // Box allows for recursive data structures by putting the recursive part on the heap
    let _list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));

    // Rc<T> and RefCell<T> usage
    // Rc::new creates a new reference-counted value
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
        /*
         * The '!' in vec![] denotes a macro invocation. vec![] is a macro that creates a new Vec.
         * Macros in Rust are denoted by an exclamation mark (!) after their name.
         * vec![] is a convenient way to create a Vec with initial values.
         *
         * The '::' in RefCell::new is the path separator operator. It's used to access associated functions (similar to static methods in other languages) or nested items within a module or type.
         * Here, 'new' is an associated function of RefCell that creates a new RefCell instance.
         */
    });

    let branch = Rc::new(Node {
        value: 5,
        children: RefCell::new(vec![Rc::clone(&leaf)]), // Rc::clone increases the reference count
    });

    println!("leaf: {:?}", leaf);
    println!("branch: {:?}", branch);

    // Demonstrating interior mutability
    // We can modify the children of leaf even though leaf is immutable
    leaf.children.borrow_mut().push(Rc::new(Node {
        value: 4,
        children: RefCell::new(vec![]),
    }));

    println!("Modified leaf: {:?}", leaf);
}