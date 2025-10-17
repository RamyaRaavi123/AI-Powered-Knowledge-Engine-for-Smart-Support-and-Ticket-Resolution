import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from utils.contentRecognizer import categorizationBuilder


def validate_model():
    df = pd.read_csv("./docs/ticket_validation_dataset.csv")

    categories = [
    "Getting Started",
    "Troubleshooting",
    "Connectivity",
    "Power Management",
    "Hardware",
    "Support",
    "Software",
    "Security"
    ]
    predictions = []
    for _, row in df.iterrows():
        predicted = categorizationBuilder(row["ticket_content"], categories)
        predictions.append(predicted)

    df["predicted_category"] = predictions
    df.to_csv("./docs/ticket_validation_results.csv", index=False)

    y_true = df["true_category"]
    y_pred = df["predicted_category"]

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    print("📊 Evaluation Metrics")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")
    print("\nDetailed Report:")
    print()

    return df,acc,prec,rec,f1,classification_report(y_true, y_pred, zero_division=0)


# if __name__ == "__main__":
#     validate_model()
