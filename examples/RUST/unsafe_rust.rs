use std::slice;

fn main() {
    // Example 1: Dereferencing a raw pointer
    let mut num = 5;

    let r1 = &num as *const i32;
    let r2 = &mut num as *mut i32;

    unsafe {
        println!("r1 is: {}", *r1);
        println!("r2 is: {}", *r2);
    }

    // Example 2: Calling an unsafe function
    unsafe {
        dangerous();
    }

    // Example 3: Creating a safe abstraction over unsafe code
    let mut v = vec![1, 2, 3, 4, 5, 6];
    let r = &mut v[..];
    let (a, b) = split_at_mut(r, 3);
    println!("a: {:?}, b: {:?}", a, b);

    // Example 4: Using extern functions to call external code
    unsafe {
        println!("Absolute value of -3 according to C: {}", abs(-3));
    }
}

// Unsafe function
unsafe fn dangerous() {
    println!("This function is unsafe and requires careful use");
}

// Safe abstraction over unsafe code
fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();

    assert!(mid <= len);

    unsafe {
        (
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(ptr.add(mid), len - mid),
        )
    }
}

// Calling a C function
extern "C" {
    fn abs(input: i32) -> i32;
}