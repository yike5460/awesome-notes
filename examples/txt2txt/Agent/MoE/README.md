# Background
Sample application step by step combining the Mixture of Experts and LLM Agents

## Mixture of Experts (MoE) Explained
The Mixture of Experts (MoE) is a machine learning architecture designed to improve model efficiency and performance by dividing the workload among multiple specialized sub-models, known as experts. Each expert is responsible for a different subset of the input data, and a gating network determines which expert(s) to use for each input.

## Core Components of MoE
- Experts (Sparse MoE Layers): These are individual neural networks that specialize in different regions of the input space, Consist of multiple "experts" (e.g., 8), each being a neural network, typically FFNs.
- Gating Network: This network decides which expert(s) to activate for a given input. It compose of learned parameters and is pretrained with the rest of the network and assigns weights to each expert based on the input, 
- Conditional Computation: Only a subset of experts is activated for each input, making the computation more efficient.
- Expert Processing: The selected experts process the input data.
- Aggregation: The outputs from the selected experts are aggregated to form the final output.

## Overall Architecture & Workflow

Workflow diagram of the MoE architecture:

mermaid
```
flowchart TD
    A[Input Data] -->|Feeds into| B[Gating Network]
    B -->|Assigns weights| C{Expert Selection}
    C -->|Selects| D1[Expert 1]
    C -->|Selects| D2[Expert 2]
    C -->|Selects| D3[Expert 3]
    
    subgraph MoE_Layers[MoE Layers]
        direction TB
        D1 -->|Processes input| P1[Expert 1 Processing]
        D2 -->|Processes input| P2[Expert 2 Processing]
        D3 -->|Processes input| P3[Expert 3 Processing]
    end
    
    P1 -->|Outputs| E[Aggregation]
    P2 -->|Outputs| E[Aggregation]
    P3 -->|Outputs| E[Aggregation]
    E -->|Outputs| F[Final Output]

    classDef expert fill:#f9f,stroke:#333,stroke-width:2px;
    classDef moeLayers fill:lightgreen,stroke:#000,stroke-width:2px;
    class D1,D2,D3 expert;
    class MoE_Layers moeLayers;
```