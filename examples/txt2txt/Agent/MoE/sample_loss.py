import torch
import torch.nn.functional as F

class MoELayer(torch.nn.Module):
    def __init__(self, num_experts, input_dim, output_dim):
        super(MoELayer, self).__init__()
        self.num_experts = num_experts
        self.experts = torch.nn.ModuleList([torch.nn.Linear(input_dim, output_dim) for _ in range(num_experts)])
        self.gate = torch.nn.Linear(input_dim, num_experts)
    
    def forward(self, x):
        gate_outputs = self.gate(x)
        gate_probs = F.softmax(gate_outputs, dim=-1)
        
        expert_outputs = torch.stack([expert(x) for expert in self.experts], dim=1)
        output = torch.einsum('bne,bn->be', expert_outputs, gate_probs)
        
        return output, gate_probs

def auxiliary_loss(gate_probs):
    # Importance Loss
    importance_loss = torch.var(torch.sum(gate_probs, dim=0))
    
    # Load Loss
    load_loss = torch.var(torch.sum(gate_probs, dim=1))
    
    return importance_loss + load_loss

# Example usage
input_dim = 10
output_dim = 5
num_experts = 4
batch_size = 8

moe_layer = MoELayer(num_experts, input_dim, output_dim)
inputs = torch.randn(batch_size, input_dim)
outputs, gate_probs = moe_layer(inputs)

# Compute auxiliary loss
aux_loss = auxiliary_loss(gate_probs)
print("Auxiliary Loss:", aux_loss.item())
