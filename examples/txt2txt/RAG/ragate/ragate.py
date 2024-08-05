import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Load the KETOD dataset
train_data = pd.read_csv("ketod_train.csv")
test_data = pd.read_csv("ketod_test.csv")

# Define the RAGate-Prompt model
class RAGatePrompt(torch.nn.Module):
    def __init__(self):
        super(RAGatePrompt, self).__init__()
        self.model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        return logits

# Initialize the RAGate-Prompt model
model = RAGatePrompt()

# Define the training loop
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)

for epoch in range(5):
    model.train()
    total_loss = 0
    for batch in train_data:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()

        outputs = model(input_ids, attention_mask)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}, Loss: {total_loss / len(train_data)}")

model.eval()
