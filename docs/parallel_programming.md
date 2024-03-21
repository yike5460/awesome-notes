
## Basics of Parallel Programming
parallel programming is a type of programming where multiple tasks are executed simultaneously. This can be achieved using multiple threads, processes, or a combination of both. The main advantage of parallel programming is that it can significantly reduce the time required to execute a program by taking advantage of the multiple cores available in modern CPUs.

### Threads (Python)
threading.Condition works as a synchronization primitive that allows threads to wait for a condition to be met. It is used to notify other threads that a condition has been met. It is similar to a semaphore but with some additional features. The overall workflow is as follows:
1. a condition instance is linked to a lock, which is used to synchronize access to the shared resource
2. threads can wait for a condition to be met using the wait() method, when a thread calls wait() it releases the lock and suspends its execution until it is woken up by another thread call to notify() or notify_all()
3. thread possess the means to notify the condition using the notify() method, which wakes up one of the waiting threads, or notify_all() which wakes up all the waiting threads, once awakened the waiting threads will reacquire the lock and continue their execution

sample code:

```python
import threading

# Create a shared resource (e.g., a buffer)
shared_buffer = []

# Create a condition
condition = threading.Condition()

def producer():
    with condition:
        # Produce an item
        shared_buffer.append("New item")
        print("Produced an item")
        # Notify waiting consumers
        condition.notify()

def consumer():
    with condition:
        # Wait until an item is available
        while not shared_buffer:
            condition.wait()
        # Consume the item
        item = shared_buffer.pop()
        print(f"Consumed: {item}")

# Create producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

# Start the threads
producer_thread.start()
consumer_thread.start()

# Wait for both threads to finish
producer_thread.join()
consumer_thread.join()
```

## Lock (Python)


## Async/Await (TypeScript)
Async/Await is a feature in TypeScript that allows you to write asynchronous code that looks synchronous. It is built on top of promises and generators, or syntactic sugar for promise, and it provides a more readable and maintainable way to write asynchronous code. The async keyword is used to define an asynchronous function, and the await keyword is used to wait for a promise to be resolved. The overall workflow is as follows:
1. an async function is defined using the async keyword
2. inside the async function, the await keyword is used to wait for a promise to be resolved, you can only await inside an async function
3. the async function returns a promise that will be resolved with the value returned by the async function, or rejected with an error thrown by the async function

sample code:

```typescript
function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log("Start");
    await delay(1000);
    console.log("Middle");
    await delay(1000);
    console.log("End");
}

main();
```

