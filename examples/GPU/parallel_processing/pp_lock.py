import threading

# A shared variable
counter = 0

# A lock object to manage access to the shared variable
lock = threading.Lock()

# The target function for each thread
def increment_counter():
    global counter
    for _ in range(1000):
        # Acquire the lock before accessing the shared resource
        lock.acquire()
        try:
            # Critical section of code
            # Print current thread name and the current value of the counter
            print(f"{threading.current_thread().name}: {counter}")
            counter += 1
        finally:
            # Always release the lock, even if an error occurred in the critical section
            lock.release()

# Create threads
threads = [threading.Thread(target=increment_counter) for _ in range(10)]

# Start threads
for thread in threads:
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print(f"Final counter value: {counter}")
