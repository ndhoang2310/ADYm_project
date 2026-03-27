import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import joblib
import os
import warnings

warnings.filterwarnings("ignore")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "final_ml_dataset.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "trained_model.joblib")


def load_and_prepare_data(path):
    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)
    df = pd.read_csv(path)
    print(f"  Dataset shape: {df.shape}")
    print(f"  Target column: salary_avg")
    print(f"  Target stats:")
    print(f"    Mean:   {df['salary_avg'].mean():.2f}")
    print(f"    Median: {df['salary_avg'].median():.2f}")
    print(f"    Min:    {df['salary_avg'].min():.2f}")
    print(f"    Max:    {df['salary_avg'].max():.2f}")

    bool_cols = df.select_dtypes(include=["bool"]).columns
    df[bool_cols] = df[bool_cols].astype(int)

    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        if col != "salary_avg":
            df[col] = df[col].map({"True": 1, "False": 0, True: 1, False: 0})
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    y = df["salary_avg"]
    X = df.drop(columns=["salary_avg"])

    print(f"  Features count: {X.shape[1]}")
    print()
    return X, y


def train_and_evaluate(X_train, X_test, y_train, y_test):
    models = {
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
        ),
    }

    results = {}

    print("=" * 60)
    print("TRAINING MODELS")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n  Training {name}...")
        model.fit(X_train, y_train)

        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        train_acc10 = np.mean(np.abs(y_pred_train - y_train) / np.clip(np.abs(y_train), 1e-8, None) <= 0.10) * 100
        test_acc10 = np.mean(np.abs(y_pred_test - y_test) / np.clip(np.abs(y_test), 1e-8, None) <= 0.10) * 100

        train_metrics = {
            "MAE": mean_absolute_error(y_train, y_pred_train),
            "RMSE": np.sqrt(mean_squared_error(y_train, y_pred_train)),
            "R2": r2_score(y_train, y_pred_train),
            "MAPE": mean_absolute_percentage_error(y_train, y_pred_train) * 100,
            "Acc±10%": train_acc10,
        }
        test_metrics = {
            "MAE": mean_absolute_error(y_test, y_pred_test),
            "RMSE": np.sqrt(mean_squared_error(y_test, y_pred_test)),
            "R2": r2_score(y_test, y_pred_test),
            "MAPE": mean_absolute_percentage_error(y_test, y_pred_test) * 100,
            "Acc±10%": test_acc10,
        }

        results[name] = {
            "model": model,
            "train": train_metrics,
            "test": test_metrics,
        }
        print(f"  {name} - Done!")

    return results


def print_results(results):
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)

    header = f"{'Model':<22} {'Split':<8} {'MAE':>10} {'RMSE':>10} {'R²':>10} {'MAPE%':>10} {'Acc±10%':>10}"
    print(header)
    print("-" * len(header))

    for name, res in results.items():
        for split in ["train", "test"]:
            m = res[split]
            tag = "Train" if split == "train" else "Test"
            print(
                f"{name:<22} {tag:<8} {m['MAE']:>10.2f} {m['RMSE']:>10.2f} {m['R2']:>10.4f} {m['MAPE']:>9.2f}% {m['Acc±10%']:>9.2f}%"
            )
        print()


def print_feature_importance(model, feature_names, top_n=20):
    print("=" * 60)
    print(f"TOP {top_n} FEATURE IMPORTANCES (Best Model)")
    print("=" * 60)

    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]

    for rank, idx in enumerate(indices, 1):
        print(f"  {rank:>3}. {feature_names[idx]:<35} {importances[idx]:.4f}")
    print()


def select_best_model(results):
    best_name = max(results, key=lambda k: results[k]["test"]["R2"])
    print(f"Best model: {best_name} (Test R² = {results[best_name]['test']['R2']:.4f})")
    return best_name, results[best_name]["model"]


def main():
    print()
    print("*" * 60)
    print("   SALARY PREDICTION - MODEL TRAINING")
    print("*" * 60)
    print()

    X, y = load_and_prepare_data(DATA_PATH)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"  Train set: {X_train.shape[0]} samples")
    print(f"  Test set:  {X_test.shape[0]} samples")

    results = train_and_evaluate(X_train, X_test, y_train, y_test)

    print_results(results)

    best_name, best_model = select_best_model(results)
    print()

    print_feature_importance(best_model, X.columns.tolist())

    joblib.dump(best_model, MODEL_SAVE_PATH)
    print(f"Model saved to: {MODEL_SAVE_PATH}")
    print()
    print("*" * 60)
    print("   TRAINING COMPLETE")
    print("*" * 60)


if __name__ == "__main__":
    main()
