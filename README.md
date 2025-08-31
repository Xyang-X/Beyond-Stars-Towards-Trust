# Beyond Stars, Towards Trust

This project demonstrates a pipeline for detecting bot-generated comments using **RoBERTa embeddings** and **XGBoost** for classification. The workflow involves data preprocessing, feature extraction with a pretrained language model, training a gradient boosting classifier, and evaluating its performance.

---

## 📦 Requirements

- Python 3.8+
- `pandas`
- `numpy`
- `torch`
- `transformers`
- `xgboost`
- `scikit-learn`
- `tqdm`

Install dependencies via pip:

```bash
pip install pandas numpy torch transformers xgboost scikit-learn tqdm
```
## Data Preprocessing

Before we start to analyze the data, a series of preprocessing procedures were applied to filter out noise and target the pseudolabels. It includes:
- `remove_duplicates.py`: Removing the duplicate reviews(the same reviews from the same user at the same time)
- `redact_pii.py`: Replace the email addresses, phone numbers and websites in the reviews by placeholder, like `<email>`.
- 

## Training

We trained two different models, **XGBoost** and **RoBERTa**, to determine whether a review can be considered trustworthy. Each model is suited for different application scenarios:

- **XGBoost**: suitable for fast baseline modeling, smaller datasets, or scenarios where interpretability and efficiency are important.  
- **RoBERTa**: suitable for high-accuracy classification on large-scale text data, where capturing deeper semantic meaning is required.  

Choose the different scripte within `classifier_roBERTa.py` and `classifier_xgbooster.py` to decide which model to be used. To run the training on a specific dataset, simply modify the `INPUT_PATH` variable to point to your desired input file.

