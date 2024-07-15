import asyncio
import time
import logging
from functools import wraps
from typing import List, Dict, Any
from transformers import DistilBertTokenizer, DistilBertForMaskedLM
import torch
import hashlib
from collections import OrderedDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForMaskedLM.from_pretrained('distilbert-base-uncased', output_hidden_states=True)

def timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

class KVCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def _hash_key(self, key):
        return hashlib.sha256(key.encode()).hexdigest()

    async def get(self, key):
        hashed_key = self._hash_key(key)
        if hashed_key not in self.cache:
            return None
        value = self.cache.pop(hashed_key)
        self.cache[hashed_key] = value
        return value

    async def put(self, key, value):
        hashed_key = self._hash_key(key)
        if hashed_key in self.cache:
            self.cache.pop(hashed_key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[hashed_key] = value

class Messenger:
    async def transfer_kv_cache(self, source, destination, kv_data):
        for key, value in kv_data.items():
            await destination.put(key, value)

    async def transfer_kv_cache_rdma(self, source, destination, kv_data):
        # Simulate RDMA transfer
        for key, value in kv_data.items():
            await destination.put(key, value)
            # In actual implementation, use RDMA APIs like `nvidia_p2p_get_pages` and `nvidia_p2p_put_pages`
            # Example:
            # nvidia_p2p_get_pages(...)
            # Perform RDMA transfer
            # nvidia_p2p_put_pages(...)
    # async def transfer_kv_cache_rdma(self, source, destination, kv_data):
    #     # Simulate RDMA transfer using asyncio streams
    #     reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    #     for key, value in kv_data.items():
    #         writer.write(f"{key}:{value}\n".encode())
    #         await writer.drain()
    #     writer.write_eof()
    #     await writer.wait_closed()            

class PrefillNode:
    def __init__(self, gpu_memory, cpu_memory, window_size=3):
        self.gpu_memory = gpu_memory
        self.cpu_memory = cpu_memory
        self.window_size = window_size

    @timing_decorator
    async def prefill(self, input_tokens, reusable_block_ids):
        new_kv_data = {}
        uncached_windows = []

        # Check for cached results using sliding window
        for i in range(len(input_tokens) - self.window_size + 1):
            window = tuple(input_tokens[i:i+self.window_size])
            window_hash = self.cpu_memory._hash_key(str(window))
            cached_result = await self.cpu_memory.get(window_hash)
            if cached_result is not None:
                new_kv_data[window_hash] = cached_result
            else:
                uncached_windows.append(window)

        # Process only uncached windows
        if uncached_windows:
            logger.info(f"Processing {len(uncached_windows)} uncached windows")
            """
            Sample uncached_windows:
            uncached_windows = [['apple', 'banana', 'cherry'], ['banana', 'cherry', 'date'], ['cherry', 'date', 'apple']]

            Sample uncached_tokens:
            uncached_tokens = ['apple', 'banana', 'cherry', 'date']

            Sample mapping:
            token_to_hidden_state =
            {
                'apple': [0.1, 0.2, 0.3, ..., 0.5],  # dimensional hidden state for 'apple'
                'banana': [0.6, 0.7, 0.8, ..., 0.9],  # dimensional hidden state for 'banana'
                'cherry': [0.1, 0.2, 0.3, ..., 0.4],  # dimensional hidden state for 'cherry'
                'date': [0.5, 0.6, 0.7, ..., 0.8]  # dimensional hidden state for 'date'
            }
            """
            uncached_tokens = list(set(token for window in uncached_windows for token in window))
            inputs = tokenizer(uncached_tokens, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)

            if outputs.hidden_states is None:
                logger.error("Model did not return hidden_states.")
                return None

            hidden_states = outputs.hidden_states[-1]
            num_tokens = hidden_states.size(1)
            # Store the hidden states for the entire window, not just individual tokens since number of auto-regressive hidden states that may not directly correspond to input tokens, which means the prefill might return fewer hidden states than the number of input   tokens due to padding, truncation, or other preprocessing steps.
            token_to_hidden_state = {token: hidden_states[0, i].tolist() for i, token in enumerate(uncached_tokens) if i < num_tokens}

            # Process and cache new results for each window
            for window in uncached_windows:
                window_hidden_states = [token_to_hidden_state.get(token, []) for token in window]
                window_hash = self.cpu_memory._hash_key(str(window))
                new_kv_data[window_hash] = window_hidden_states
                await self.cpu_memory.put(window_hash, window_hidden_states)

        logger.info(f"Processed {len(uncached_windows)} uncached windows")
        return new_kv_data

class DecodingNode:
    def __init__(self, cpu_memory):
        self.cpu_memory = cpu_memory
        self.current_load = 0

    async def receive_kv_cache(self, kv_data):
        for key, value in kv_data.items():
            await self.cpu_memory.put(key, value)

    @timing_decorator
    async def decode(self, tokens: List[str]) -> List[str]:
        decoded_tokens = []
        for token in tokens:
            token_hash = self.cpu_memory._hash_key(token)
            cached_vector = await self.cpu_memory.get(token_hash)
            if cached_vector is not None:
                logits = torch.tensor(cached_vector).unsqueeze(0)
            else:
                inputs = tokenizer(token, return_tensors="pt")
                with torch.no_grad():
                    outputs = model(**inputs)
                logits = outputs.logits

            logger.info(f"Decoding token: {token}")
            predicted_token_id = torch.argmax(logits[0, -1]).item()
            decoded_token = tokenizer.decode([predicted_token_id])
            decoded_tokens.append(decoded_token)
        return decoded_tokens

class Conductor:
    def __init__(self, prefill_nodes: List[PrefillNode], decoding_nodes: List[DecodingNode], messenger: Messenger):
        self.prefill_nodes = prefill_nodes
        self.decoding_nodes = decoding_nodes
        self.messenger = messenger

    async def handle_request(self, input_tokens: List[str], reusable_block_ids: List[int]) -> List[str]:
        try:
            selected_prefill_node = self.select_prefill_node()
            new_kv_data = await selected_prefill_node.prefill(input_tokens, reusable_block_ids)
            selected_decoding_node = self.select_decoding_node()
            await self.messenger.transfer_kv_cache(selected_prefill_node.cpu_memory, selected_decoding_node.cpu_memory, new_kv_data)
            # await self.messenger.transfer_kv_cache_rdma(selected_prefill_node.cpu_memory, selected_decoding_node.cpu_memory, new_kv_data)
            decoded_tokens = await selected_decoding_node.decode(input_tokens)
            logger.info(f"Decoded tokens: {decoded_tokens}")
            return decoded_tokens
        except Exception as e:
            logger.info(f"Error handling request: {str(e)}")
            raise

    def select_prefill_node(self) -> PrefillNode:
        return self.prefill_nodes[0]

    def select_decoding_node(self) -> DecodingNode:
        return min(self.decoding_nodes, key=lambda node: node.current_load)

async def main():
    cpu_memory = KVCache(capacity=1000)
    gpu_memory = KVCache(capacity=1000)
    messenger = Messenger()
    prefill_node = PrefillNode(gpu_memory, cpu_memory, window_size=3)
    decoding_node = DecodingNode(cpu_memory)
    conductor = Conductor([prefill_node], [decoding_node], messenger)

    input_tokens = ["Hello", "world", "how", "are", "you"]
    reusable_block_ids = [1, 2, 3]

    try:
        result = await conductor.handle_request(input_tokens, reusable_block_ids)
        logger.info(f"Generated Tokens: {result}")
    except Exception as e:
        logger.info(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())