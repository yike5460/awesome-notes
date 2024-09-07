fn main() {
    // Closure example
    let add_one = |x| x + 1;
    println!("Add one to 5: {}", add_one(5));

    // Closure that captures its environment
    let x = 4;
    let equal_to_x = |z| z == x;
    let y = 4;
    println!("Is y equal to x? {}", equal_to_x(y));

    // Iterator example
    let v1 = vec![1, 2, 3];
    let v1_iter = v1.iter();

    for val in v1_iter {
        println!("Got: {}", val);
    }

    // Using iterator adaptors
    let v2: Vec<i32> = v1.iter().map(|x| x + 1).collect();
    println!("v2: {:?}", v2);

    // Using filter
    let v3: Vec<i32> = v1.into_iter().filter(|x| x % 2 == 0).collect();
    println!("v3: {:?}", v3);
}