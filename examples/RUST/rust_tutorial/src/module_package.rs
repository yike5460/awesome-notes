// File: src/module_package.rs

// Define a module named 'shapes'
mod shapes {
    // Public struct
    pub struct Rectangle {
        width: f64,
        height: f64,
    }

    impl Rectangle {
        // Public associated function (constructor)
        pub fn new(width: f64, height: f64) -> Rectangle {
            Rectangle { width, height }
        }

        // Public method
        pub fn area(&self) -> f64 {
            self.width * self.height
        }
    }

    // Private function
    fn helper_function() {
        println!("This is a private helper function");
    }

    // Public module within shapes
    pub mod utils {
        pub fn print_dimensions(width: f64, height: f64) {
            println!("Width: {}, Height: {}", width, height);
        }
    }
}

// Main function to demonstrate usage
fn main() {
    // Using the Rectangle struct from the shapes module
    let rect = shapes::Rectangle::new(5.0, 10.0);
    println!("Area of rectangle: {}", rect.area());

    // Using the utils submodule
    shapes::utils::print_dimensions(5.0, 10.0);

    // This would cause a compilation error because helper_function is private
    // shapes::helper_function();
}
