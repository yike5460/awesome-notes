use std::rc::Rc;
use std::cell::RefCell;

// Smart Pointers in Rust

// Box<T> example
// Box<T> is a smart pointer that provides heap allocation
#[allow(dead_code)]
enum List {
    Cons(i32, Box<List>), // Recursive data structure using Box
    Nil,
}

// Rc<T> and RefCell<T> example
// Rc<T> provides shared ownership of a value
// RefCell<T> provides interior mutability
#[allow(dead_code)]
#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>, // Mutable vector of shared ownership Nodes
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

// Typical usage of smart pointers:
// - Box<T>: When you have a type whose size can't be known at compile time and you want to use it in a context that requires an exact size
// - Rc<T>: When you need multiple ownership of data
// - RefCell<T>: When you need mutable access to data that's behind a shared reference

// Error-prone mistakes for new learners:
// 1. Forgetting that Box<T> is for single ownership scenarios
// 2. Creating reference cycles with Rc<T> which can lead to memory leaks
// 3. Overusing RefCell<T> when simple borrowing rules would suffice
// 4. Not understanding the runtime cost of RefCell<T>'s borrowing checks
// 5. Forgetting to clone Rc<T> when creating new references (use Rc::clone(&rc) instead of rc.clone())

// Advanced concepts:
// - Deref trait: Allows smart pointers to be treated like references
// - Drop trait: Customizes what happens when a smart pointer goes out of scope

// Remember: Smart pointers in Rust provide additional functionality beyond what references provide,
// often with some runtime cost. Use them judiciously and understand their trade-offs.
