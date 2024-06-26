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