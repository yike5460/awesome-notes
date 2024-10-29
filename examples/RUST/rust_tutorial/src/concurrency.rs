/* Typical usage of concurrency in Rust:

 - Creating threads for parallel execution of code
 - Using channels for safe communication between threads
 - Using mutexes and atomic types for shared state (not shown in this example)

Error-prone mistakes for new learners:
1. Forgetting to join spawned threads, leading to premature program termination
2. Creating data races by sharing mutable data between threads without proper synchronization
3. Deadlocks from improper use of mutexes (not shown in this example)
4. Forgetting that the main thread can finish before spawned threads
5. Not handling potential errors in thread communication (e.g., send/recv on channels)

Advanced concepts:
- Arc<T> for sharing ownership across multiple threads
- Mutex<T> for mutual exclusion in shared mutable state
- Atomic types for lock-free concurrent operations

Remember: Rust's ownership system and type checking help prevent many common concurrency errors at compile time,
but it's still important to design your concurrent programs carefully to avoid logical errors and deadlocks.
*/

use std::thread;
use std::sync::mpsc;
use std::time::Duration;

fn main() {
    // Creating threads
    // thread::spawn creates a new thread and returns a JoinHandle
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    // Main thread execution
    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }

    // Wait for the spawned thread to finish
    handle.join().unwrap();

    // Using channels for message passing
    // mpsc stands for multiple producer, single consumer
    let (tx, rx) = mpsc::channel();

    // Spawn a new thread that will send messages
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    // Receive messages in the main thread
    for received in rx {
        println!("Got: {}", received);
    }
}