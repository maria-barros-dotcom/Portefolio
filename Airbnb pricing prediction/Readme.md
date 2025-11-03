# Airbnb Pricing Prediction Project

## 🏠 Project Overview
Predicting optimal Airbnb listing prices using machine learning to help hosts competitively price their properties. Achieved **65.7% variance explained (R²)** using gradient boosting on log-transformed prices.

## 📊 Key Results
| Model          | MAE (log) | RMSE (log) | R² (log) | Training Time |
|----------------|-----------|------------|----------|---------------|
| XGBoost        | 0.289     | 0.148      | 0.657    | 2m 14s        |
| LightGBM       | 0.289     | 0.149      | 0.654    | 1m 02s        |
| Random Forest  | 0.295     | 0.155      | 0.641    | 4m 37s        |

**Best Model**: XGBoost with log transformation (MAE ±29% of actual price)

**🛠️ Tools**: Python, Pandas, XGBoost, LightGBM, Scikit-learn, Jupyter

#### Data used: 
https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data?resource=download
