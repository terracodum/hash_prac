"""
Обучает простую модель (KNN) на датасете Iris и сохраняет в model.pkl.
Запуск: py -3.12 train_model.py
"""
import pathlib
import pickle
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import numpy as np

iris = load_iris()
X, y = iris.data, iris.target

pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("knn",    KNeighborsClassifier(n_neighbors=5)),
])

scores = cross_val_score(pipe, X, y, cv=5)
pipe.fit(X, y)

model_path = pathlib.Path(__file__).parent / "model.pkl"
with open(model_path, "wb") as f:
    pickle.dump({"model": pipe, "classes": iris.target_names.tolist()}, f)

print(f"Модель обучена, CV accuracy: {np.mean(scores):.3f} ± {np.std(scores):.3f}")
print(f"Сохранено в {model_path}")
print(f"Признаки: sepal_length, sepal_width, petal_length, petal_width")
print(f"Классы:   {iris.target_names.tolist()}")
