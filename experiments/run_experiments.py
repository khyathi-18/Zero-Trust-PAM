# experiments/run_experiments.py
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import matplotlib.pyplot as plt
import joblib

# --- CONFIG ---
DATA_PATH = "../datasets/data.csv"   # put your dataset here
RESULTS_DIR = "../results"
ASSETS_DIR = "../paper_assets"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# --- LOAD DATA ---
# Expected: a CSV with features and a column "label" where 1=anomaly, 0=normal
df = pd.read_csv(DATA_PATH)
y_true = df['label'].values
X = df.drop(columns=['label']).values

# --- MODEL 1: Isolation Forest (unsupervised) ---
if_model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
if_model.fit(X)
# IsolationForest returns -1 for outliers, 1 for inliers
if_preds = if_model.predict(X)
# convert to 1=anomaly, 0=normal
y_if = np.where(if_preds == -1, 1, 0)

# --- MODEL 2: Simple Autoencoder (reconstruction error) using PyTorch ---
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

class AE(nn.Module):
    def __init__(self, n_features, hid=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(n_features, hid),
            nn.ReLU(),
            nn.Linear(hid, hid//2)
        )
        self.decoder = nn.Sequential(
            nn.Linear(hid//2, hid),
            nn.ReLU(),
            nn.Linear(hid, n_features)
        )
    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

# prepare tensor data (use only normal samples for training ideally)
X_np = X.astype(np.float32)
# if you have label column, train on y==0 only
try:
    X_train = X_np[y_true == 0]
except:
    X_train = X_np

train_loader = DataLoader(TensorDataset(torch.from_numpy(X_train)), batch_size=64, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AE(n_features=X.shape[1]).to(device)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

# train for a small number of epochs
for epoch in range(20):
    model.train()
    total_loss = 0
    for batch in train_loader:
        xb = batch[0].to(device)
        out = model(xb)
        loss = loss_fn(out, xb)
        opt.zero_grad(); loss.backward(); opt.step()
        total_loss += loss.item()
    # print(epoch, total_loss / len(train_loader))

# compute reconstruction error on full dataset
model.eval()
with torch.no_grad():
    X_t = torch.from_numpy(X_np).to(device)
    rec = model(X_t).cpu().numpy()
recon_err = np.mean((rec - X_np)**2, axis=1)
# choose threshold (e.g., 95th percentile on training normal data)
th = np.percentile(recon_err[y_true == 0], 95) if np.any(y_true==0) else np.percentile(recon_err, 95)
y_ae = (recon_err > th).astype(int)

# --- METRICS ---
def compute_metrics(y_true, y_pred):
    pr = precision_score(y_true, y_pred, zero_division=0)
    rc = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_true, y_pred)
    except:
        auc = np.nan
    return pr, rc, f1, auc

pr_if, rc_if, f1_if, auc_if = compute_metrics(y_true, y_if)
pr_ae, rc_ae, f1_ae, auc_ae = compute_metrics(y_true, y_ae)

results = pd.DataFrame([
    ["IsolationForest", pr_if, rc_if, f1_if, auc_if],
    ["Autoencoder", pr_ae, rc_ae, f1_ae, auc_ae]
], columns=["Method","Precision","Recall","F1","AUC"])

results.to_csv(os.path.join(RESULTS_DIR, "metrics.csv"), index=False)
print("Saved metrics to", os.path.join(RESULTS_DIR, "metrics.csv"))

# --- SAVE BAR CHART (F1 comparison) ---
plt.figure()
plt.bar(results['Method'], results['F1'])
plt.title("F1 Score Comparison")
plt.ylabel("F1 score")
plt.savefig(os.path.join(ASSETS_DIR, "model_comparison_bar.png"), bbox_inches='tight')
print("Saved bar chart to", os.path.join(ASSETS_DIR, "model_comparison_bar.png"))

# optionally save models
joblib.dump(if_model, os.path.join(RESULTS_DIR, "isolation_forest.joblib"))
torch.save(model.state_dict(), os.path.join(RESULTS_DIR, "autoencoder.pth"))

