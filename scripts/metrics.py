"""Evaluation metrics with explicit formulae (used by notebooks 03-06).

Classification (RQ1, supplementary):
    Accuracy  = (TP + TN) / (TP + TN + FP + FN)
    Precision = TP / (TP + FP)
    Recall    = TP / (TP + FN)
    F1        = 2 * Precision * Recall / (Precision + Recall)
    AUC       = area under the ROC curve

Forecasting (RQ4) - applied identically to every model (Hyndman & Athanasopoulos, 2021):
    MAE  = mean(|e_t|)
    RMSE = sqrt(mean(e_t ** 2))
    MASE = mean(|e_t|) / mean(|y_t - y_{t-m}|)  over the training period (m = 12)
"""
import numpy as np
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score)


def classification_report_dict(y_true, y_prob, threshold=0.5):
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "auc": roc_auc_score(y_true, y_prob),
    }


def confusion_counts(y_true, y_prob, threshold=0.5):
    """Counts behind accuracy / precision / recall (TP, FP, FN, TN) for a worked example in the report."""
    y_true = np.asarray(y_true).astype(int)
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    return {"tp": int(((y_pred == 1) & (y_true == 1)).sum()), "fp": int(((y_pred == 1) & (y_true == 0)).sum()),
            "fn": int(((y_pred == 0) & (y_true == 1)).sum()), "tn": int(((y_pred == 0) & (y_true == 0)).sum())}


def mae(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(np.mean(np.abs(y - yhat)))


def rmse(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def mase(y, yhat, y_train, m=12):
    """Mean absolute scaled error; scale = in-sample seasonal-naive MAE."""
    y_train = np.asarray(y_train, float)
    scale = np.mean(np.abs(y_train[m:] - y_train[:-m]))
    return float(mae(y, yhat) / scale) if scale > 0 else np.nan
