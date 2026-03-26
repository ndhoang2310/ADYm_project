# Salary Prediction - Model Training

## Dataset Overview

| Property | Value |
|---|---|
| Samples | 2,400 |
| Features | ~370+ |
| Target | `salary_avg` (continuous) |
| Task | **Regression** |

**Feature groups:**
- **Numeric** (5): `language_req`, `is_manager`, `exp_years`, `job_level`, `is_shift_work`
- **Tech skills** (~340): One-hot encoded (e.g., `tech_Python`, `tech_React`, `tech_AWS`)
- **Location** (~30): One-hot encoded Vietnamese provinces/cities
- **Job category** (~18): One-hot encoded job roles
- **Other**: `work_method`, `contract_type`, `education_level` (one-hot)

---

## Model Selection

### Primary: Random Forest Regressor

**Why Random Forest?**

1. **High-dimensional sparse data** — The dataset has 370+ features, most of which are binary (one-hot encoded). Random Forest handles this naturally without requiring dimensionality reduction or feature scaling.

2. **No preprocessing needed** — Tree-based models don't require normalization or standardization, which simplifies the pipeline for a dataset with mixed numeric and binary features.

3. **Feature importance** — Random Forest provides built-in feature importance scores, which is valuable for understanding which skills, locations, and job levels drive salary predictions.

4. **Robustness** — Ensembling many decision trees reduces overfitting compared to a single tree, and handles noise in salary data well.

5. **Good baseline** — For tabular/structured data with many categorical features, tree-based ensembles consistently outperform linear models and neural networks.

### Comparison: Gradient Boosting Regressor

Gradient Boosting is included as a comparison because:
- It often achieves **higher accuracy** than Random Forest by learning from errors sequentially
- It can capture more complex feature interactions
- The script automatically selects the model with the best test R² score

### Why not other models?

| Model | Reason not chosen |
|---|---|
| Linear Regression | Poor with 370+ sparse binary features, assumes linear relationships |
| SVR | Too slow for 370+ features × 2400 samples, requires feature scaling |
| Neural Network | Overkill for 2400 samples, requires careful tuning, no interpretability |
| KNN | Suffers from curse of dimensionality with 370+ features |
| XGBoost/LightGBM | Great but adds external dependencies; sklearn's GradientBoosting is sufficient here |

---

## Hyperparameter Configuration

### Random Forest

```python
RandomForestRegressor(
    n_estimators=200,      # 200 trees for stable predictions
    max_depth=15,          # Limit depth to prevent overfitting
    min_samples_split=5,   # Require 5+ samples to split a node
    min_samples_leaf=2,    # Each leaf must have 2+ samples
    random_state=42,       # Reproducibility
    n_jobs=-1,             # Use all CPU cores for speed
)
```

| Parameter | Value | Rationale |
|---|---|---|
| `n_estimators` | 200 | Enough trees for convergence without excessive training time |
| `max_depth` | 15 | Limits tree complexity; with 370+ features, deep trees overfit easily |
| `min_samples_split` | 5 | Prevents splits on very small groups |
| `min_samples_leaf` | 2 | Ensures predictions are based on at least 2 data points |

### Gradient Boosting

```python
GradientBoostingRegressor(
    n_estimators=200,      # 200 boosting stages
    max_depth=5,           # Shallow trees (standard for boosting)
    learning_rate=0.1,     # Moderate shrinkage
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
)
```

| Parameter | Value | Rationale |
|---|---|---|
| `n_estimators` | 200 | Balanced accuracy vs. training time |
| `max_depth` | 5 | Boosting works best with shallow weak learners |
| `learning_rate` | 0.1 | Standard value; lower = more robust but slower |

---

## Train/Test Split

```
Split ratio: 80% train / 20% test
Random state: 42 (reproducible)
```

80/20 is standard for datasets of this size (~2400 samples), providing ~1920 training and ~480 test samples.

---

## Evaluation Metrics

| Metric | Description |
|---|---|
| **MAE** | Average absolute error in salary prediction (in the same unit as salary) |
| **RMSE** | Penalizes large errors more heavily than MAE |
| **R² Score** | Proportion of variance explained (1.0 = perfect, 0.0 = baseline) |

---

## Usage

```bash
python modeling/train_model.py
```

**Output:**
- Prints dataset statistics
- Trains both models
- Displays comparison table with train/test metrics
- Shows top 20 most important features
- Saves best model to `modeling/trained_model.joblib`

## Saved Model

The best model (highest test R²) is saved via `joblib` to `modeling/trained_model.joblib`. Load it with:

```python
import joblib
model = joblib.load("modeling/trained_model.joblib")
predictions = model.predict(X_new)
```
