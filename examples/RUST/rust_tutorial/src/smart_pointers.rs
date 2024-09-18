use std::rc::Rc;
use std::cell::RefCell;

// Box<T> example
#[allow(dead_code)]
enum List {
    Cons(i32, Box<List>),
    Nil,
}

// Rc<T> and RefCell<T> example
#[allow(dead_code)]
#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
}

fn main() {
    // Change this line
    let _list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));

    // Rc<T> and RefCell<T> usage
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
    });

    let branch = Rc::new(Node {
        value: 5,
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    println!("leaf: {:?}", leaf);
    println!("branch: {:?}", branch);
}