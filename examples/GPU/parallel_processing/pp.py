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