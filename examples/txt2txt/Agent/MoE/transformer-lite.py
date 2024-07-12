import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class DecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, dropout=dropout)
        self.cross_attn = nn.MultiheadAttention(d_model, num_heads, dropout=dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, encoder_output, src_mask, tgt_mask):
        """
        self_attn & cross_attn
        Inputs:
        query, key, value: These are the inputs to the attention mechanism. In the case of self_attn, all three are the same (x). For cross_attn, the query is the output from the self-attention layer, and key and value are the encoder output. The dimensions of these tensors are (L, N, E) where L is the sequence length, N is the batch size, and E is the embedding dimension.

        attn_mask: This is an optional parameter that specifies which positions should be ignored when calculating the attention weights. The dimensions of this tensor are (L, L) where L is the sequence length.

        Output:
        The output of self_attn and cross_attn is a tuple where the first element is the output tensor of shape (L, N, E) and the second element is the attention weights of shape (N, L, S) where S is the source sequence length.
        """
        # Self-attention
        attn_output = self.self_attn(x, x, x, attn_mask=tgt_mask)[0]
        x = self.norm1(x + self.dropout(attn_output))
        
        # Cross-attention
        attn_output = self.cross_attn(x, encoder_output, encoder_output, attn_mask=src_mask)[0]
        x = self.norm2(x + self.dropout(attn_output))
        
        # Feed-forward network
        ffn_output = self.ffn(x)
        x = self.norm3(x + self.dropout(ffn_output))
        
        return x

class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff, max_len=5000, dropout=0.1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_len)
        self.layers = nn.ModuleList([DecoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)])
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, tgt, encoder_output, src_mask, tgt_mask):
        x = self.embedding(tgt)
        x = self.pos_encoder(x)
        x = self.dropout(x)

        for layer in self.layers:
            x = layer(x, encoder_output, src_mask, tgt_mask)

        output = self.fc_out(x)
        return output

# Example usage
vocab_size = 10000
d_model = 512
num_heads = 8
num_layers = 6
d_ff = 2048
max_len = 100

decoder = TransformerDecoder(vocab_size, d_model, num_heads, num_layers, d_ff, max_len)

# Dummy inputs
tgt = torch.randint(0, vocab_size, (32, 20))  # Batch size 32, sequence length 20
encoder_output = torch.randn(32, 25, d_model)  # Encoder output with 25 time steps
src_mask = torch.ones(32, 25)  # Assuming no padding in source
tgt_mask = torch.tril(torch.ones(20, 20)).expand(32, 1, 20, 20)

output = decoder(tgt, encoder_output, src_mask, tgt_mask)
print(output.shape)  # Should be [32, 20, vocab_size]
