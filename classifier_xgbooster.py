import pandas as pd
import numpy as np
from transformers import RobertaTokenizer, RobertaModel
import torch
import xgboost as xgb
from sklearn.metrics import classification_report
from tqdm import tqdm


INPUT_PATH = "bot_comments_dataset.csv"
OUTPUT_PATH = "xgb_RoBERTa.model"

df = pd.read_csv(INPUT_PATH)
df = df.dropna(subset=["text", "label", "time"])
df["text"] = df["text"].astype(str)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)

train_size = 0.8
train_len = int(len(df) * train_size)
train_df = df.iloc[:train_len]
val_df   = df.iloc[train_len:]



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
roberta_model = RobertaModel.from_pretrained("roberta-base").to(device)
roberta_model.eval()

def encode_texts(texts, batch_size=32):
    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Encoding texts"):
        batch = texts[i:i+batch_size]
        batch = ["" if x is None or str(x) == "nan" else str(x) for x in batch]

        enc = tokenizer(batch, padding=True, truncation=True, max_length=128, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = roberta_model(**enc)
            embeddings = outputs.last_hidden_state[:,0,:].cpu().numpy()
            all_embeddings.append(embeddings)
    return np.vstack(all_embeddings)

X_train = encode_texts(train_df["text"].tolist())
y_train = train_df["label"].values

X_val   = encode_texts(val_df["text"].tolist())
y_val   = val_df["label"].values

n_pos = (y_train == 1).sum()
n_neg = (y_train == 0).sum()
scale_pos_weight = n_neg / n_pos

dtrain = xgb.DMatrix(X_train, label=y_train)
dval   = xgb.DMatrix(X_val, label=y_val)

params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "scale_pos_weight": scale_pos_weight,
    "max_depth": 6,
    "eta": 0.1,
    "verbosity": 1
}


num_boost_round = 100
evals = [(dtrain, "train"), (dval, "val")]

for i in tqdm(range(1, num_boost_round+1), desc="XGBoost training rounds"):
    bst = xgb.train(
        params,
        dtrain,
        num_boost_round=i,
        evals=evals,
        verbose_eval=False  
    )


y_pred_prob = bst.predict(dval)
y_pred = (y_pred_prob >= 0.5).astype(int)

print(classification_report(y_val, y_pred))

bst.save_model(OUTPUT_PATH)

