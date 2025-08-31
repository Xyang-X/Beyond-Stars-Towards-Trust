import torch
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
from tqdm import tqdm
import os


MODEL_NAME = "roberta-base"
MAX_LEN = 128
BATCH_SIZE = 32
EPOCHS = 3
LR = 2e-5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_DPATH = "./roberta_bot_classifier_weighted"
INPUT_PATH = "bot_comments_dataset.csv"

df = pd.read_csv(INPUT_PATH)


df['time'] = pd.to_datetime(df['time'])

# 按时间排序
df = df.sort_values(by='time').reset_index(drop=True)

# 设置训练集比例，比如 80% 训练
train_size = 0.8
train_index = int(len(df) * train_size)

train_df = df.iloc[:train_index].reset_index(drop=True)
val_df = df.iloc[train_index:].reset_index(drop=True)

tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)

class CommentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }

train_dataset = CommentDataset(train_df["text"].tolist(), train_df["label"].tolist(), tokenizer, MAX_LEN)
val_dataset = CommentDataset(val_df["text"].tolist(), val_df["label"].tolist(), tokenizer, MAX_LEN)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
model.to(DEVICE)

num_0 = df['label'].value_counts()[0]
num_1 = df['label'].value_counts()[1]
weight_0 = 1.0
weight_1 = num_0 / num_1 
class_weights = torch.tensor([weight_0, weight_1], dtype=torch.float).to(DEVICE)

optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(0.1*total_steps), num_training_steps=total_steps)


import torch.nn as nn

def train_epoch(model, data_loader, optimizer, scheduler):
    model.train()
    total_loss = 0
    loss_fn = nn.CrossEntropyLoss(weight=class_weights)
    for batch in tqdm(data_loader, desc="Training"):
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels = batch["labels"].to(DEVICE)

        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits

        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
    return total_loss / len(data_loader)

def eval_model(model, data_loader):
    model.eval()
    preds, true_labels = [], []
    with torch.no_grad():
        for batch in tqdm(data_loader, desc="Validation"):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1)

            preds.extend(pred.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    return classification_report(true_labels, preds, digits=4)


for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS}")
    train_loss = train_epoch(model, train_loader, optimizer, scheduler)
    print(f"Train Loss: {train_loss:.4f}")
    report = eval_model(model, val_loader)
    print(report)


if not os.path.exists(OUTPUT_DPATH):
    os.makedirs(OUTPUT_DPATH)
model.save_pretrained(OUTPUT_DPATH)
tokenizer.save_pretrained(OUTPUT_DPATH)

