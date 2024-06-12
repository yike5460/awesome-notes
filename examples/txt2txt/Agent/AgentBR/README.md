# Web Search Agent with RALM
## Introduction

## Agent

## Hybrid retrieval
Hybrid retrieval combining dense, sparse and internet retrieval methods in RALM architecture:

Quota from the [paper](https://arxiv.org/pdf/2404.19543)
```
To tackle the issue of inaccurate Internet retrieval
results, Lazaridou et al. (2022) proposed using
the TF-IDF algorithm to score the retrieval results.
They used each question q verbatim as a query
and issued a call to Google Search via the Google
Search API. For each question, they retrieved the
top 20 URLs and parsed their HTML content to
extract clean text, generating a set of documents
D for each question q. To prevent irrelevant information from hindering the resolution of a user’s
query, Hu et al. (2023) designed a gating circuit.
This circuit utilised a dual-encoder dot product to
calculate similarity and a gating circuit based on
term weights. Additionally, Boytsov et al. (2016)
presented an approach that replaced term-based
retrieval with k-Nearest Neighbors(kNN) search
while combining a translation model and BM25
to improve retrieval performance. This approach
enabled the model to take into account the semantic
relationships between terms and traditional statistical weighting schemes, resulting in a more efficient
retrieval system.
```