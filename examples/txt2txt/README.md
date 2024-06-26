- Using [awscurl](https://github.com/okigan/awscurl) to make a request to the LMI [Large Model Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html) API
- Exploration TGI, TensorRTLLM and VLLM
- Metrics alike logprob
- Dense/Parse/Multi-vector embeddings
- Ray on EKS

## Q & A

Q: In the context of tokenizer phase, does the input_id is fixed in sequence or mapped according specific corpus rules, or they are just random at the initial phase and depend on specific model implementation
A: Input IDs for tokens in language models are not random, but are assigned in a specific way according to the model's vocabulary and tokenization process. Here are the key points about how input IDs are typically determined:
- Vocabulary creation: During model training, a vocabulary of tokens is created from the training corpus. This vocabulary contains the most common words, subwords, or characters depending on the tokenization method used.
- Assigning IDs: Each unique token in the vocabulary is assigned a unique numerical identifier called a token ID. This mapping of tokens to IDs is fixed once the vocabulary is created.
- Consistency: The mapping between tokens and their IDs remains consistent for a given model/tokenizer. This means the same token will always map to the same ID.
- Corpus-specific: The exact mapping of tokens to IDs can vary between different models and corpora. A token might have different IDs in different models trained on different datasets.
- Special tokens: Most vocabularies include special tokens like [PAD], [UNK], [CLS], [SEP] etc., which are typically assigned specific IDs (often low-numbered IDs).
- Tokenization process: When encoding text, the tokenizer breaks down the input into tokens and looks up the corresponding ID for each token in its vocabulary.
- Out-of-vocabulary handling: Tokens not in the vocabulary are typically mapped to a special [UNK] (unknown) token ID or broken down into smaller subwords/characters that are in the vocabulary.
- Model-specific: The exact tokenization method and vocabulary can vary between different model architectures (e.g., BERT vs. GPT), but the principle of consistent token-to-ID mapping remains.
In summary, input IDs are not random, but are determined by a fixed mapping based on the model's specific vocabulary, which is created during the initial training process. This mapping remains consistent for that particular model/tokenizer implementation.

Q: Does the larger the dimension of vector is, the performant the embedding model is?
A: The dimensionality of embedding vectors does not have a simple linear relationship with model performance. While increasing the dimension of embedding vectors can potentially improve model performance, it's not always true that larger dimensions lead to better performance. Here are some key points to consider:
- Representational capacity: Higher-dimensional embeddings can capture more information and nuances about words or tokens, potentially leading to better performance in certain tasks.
- Overfitting risk: Very high-dimensional embeddings may lead to overfitting, especially if the training data is limited. This can result in poor generalization to unseen data.
- Computational cost: Larger embedding dimensions increase the computational resources required for training and inference, which may not always be justified by the performance gains.
- Task dependency: The optimal embedding dimension can vary depending on the specific task and the complexity of the language or domain being modeled.
- Diminishing returns: There's often a point of diminishing returns, where increasing the embedding dimension beyond a certain point yields minimal or no improvement in performance.
- Model architecture: The overall architecture of the model, not just the embedding dimension, plays a crucial role in determining performance.
In practice, the choice of embedding dimension is often determined empirically through experimentation, considering factors such as model performance, computational resources, and the specific requirements of the task at hand. It's common to see embedding dimensions ranging from a few hundred to several thousand in modern language models, but the optimal size can vary widely depending on the application.

Q: Self-attention implementation in transformer architecture 
A: Detailed step by step with formulae:
**Self-Attention Mechanism**

Self-attention, also known as scaled dot-product attention, is a mechanism that allows a model to weigh the importance of different words in a sentence when processing a specific word. It helps the model understand the context by focusing on relevant words.

**How Self-Attention Works**

1. **Input Representation:**
   - Each word in the input sequence is represented as a vector. For simplicity, let's consider a sentence with three words: "I love movies."

2. **Query, Key, and Value Vectors:**
   - For each word, we create three vectors: Query (Q), Key (K), and Value (V). These vectors are obtained by multiplying the input embeddings with learned weight matrices $$W_Q$$, $$W_K$$, and $$W_V$$.

   $$
   Q = XW_Q, \quad K = XW_K, \quad V = XW_V
   $$

3. **Compatibility Scores:**
   - The compatibility score between the query vector of a word and the key vectors of all words is calculated using the dot product. This score indicates how much focus the model should place on other words when processing the current word.

   $$
   \text{score}(Q_i, K_j) = Q_i \cdot K_j
   $$

4. **Scaled Dot-Product:**
   - To prevent the dot product from growing too large, we scale it by the square root of the dimension of the key vectors ($$d_k$$).

   $$
   \text{scaled\_score}(Q_i, K_j) = \frac{Q_i \cdot K_j}{\sqrt{d_k}}
   $$

5. **Softmax Function:**
   - The scaled scores are passed through a softmax function to obtain the attention weights. These weights determine the importance of each word in the context of the current word.

   $$
   \text{attention\_weights}(Q_i, K) = \text{softmax}\left(\frac{Q_i \cdot K}{\sqrt{d_k}}\right)
   $$

6. **Weighted Sum:**
   - The final output for each word is obtained by taking the weighted sum of the value vectors, using the attention weights.

   $$
   \text{output}_i = \sum_j \text{attention\_weights}(Q_i, K_j) \cdot V_j
   $$

Q: What does multiheaded attention used for in transformer architecture compare to existing self-attention mechanism?
A: Multi-headed attention is a key component of the Transformer architecture that extends the basic self-attention mechanism to capture different aspects of the input sequence simultaneously. Here are some key benefits of multi-headed attention compared to single-headed self-attention:
Diverse Focus: Each attention head can focus on different parts of the sentence, capturing various relationships and dependencies. For example, one head might focus on short-term dependencies while another focuses on long-term dependencies.
Enhanced Representation: By combining the outputs of multiple heads, the model can create a more comprehensive representation of the input sequence.
Improved Performance: Multi-head attention allows the model to learn more complex patterns and relationships, leading to better performance on tasks like translation, summarization, and question answering.
Detailed step by step with formulae:
1. **Multiple Attention Heads:**
   - Instead of having a single set of Q, K, and V vectors, multi-head attention uses multiple sets (heads). Each head operates independently and focuses on different parts of the sentence.

   $$
   \text{head}_i = \text{Attention}(QW_Q^i, KW_K^i, VW_V^i)
   $$

2. **Parallel Processing:**
   - Each attention head processes the input sequence separately, allowing the model to capture various aspects of the sentence simultaneously.

3. **Concatenation and Linear Transformation:**
   - The outputs from all attention heads are concatenated and then linearly transformed to produce the final output.

   $$
   \text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \text{head}_2, \ldots, \text{head}_h)W_O
   $$