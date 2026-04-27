"""
Python pipeline: принимает JSON с признаками, возвращает предсказание в JSON.

Входные данные (sys.argv[1]) — JSON строка вида:
  {"features": [5.1, 3.5, 1.4, 0.2]}

Выход (stdout) — JSON вида:
  {"prediction": 0, "class": "setosa", "probabilities": {"setosa": 1.0, ...}}

Запуск вручную:
  py -3.12 predict.py "{\"features\": [5.1, 3.5, 1.4, 0.2]}"
"""
import sys
import json
import pathlib
import pickle
import numpy as np


def load_model():
    model_path = pathlib.Path(__file__).parent / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}\n"
            "Запусти сначала: py -3.12 train_model.py"
        )
    with open(model_path, "rb") as f:
        return pickle.load(f)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Нет входных данных. Передай JSON как argv[1]"}))
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Неверный JSON: {e}"}))
        sys.exit(1)

    if "features" not in data:
        print(json.dumps({"error": "Ключ 'features' отсутствует"}))
        sys.exit(1)

    try:
        features = np.array(data["features"], dtype=np.float64).reshape(1, -1)
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": f"Неверные признаки: {e}"}))
        sys.exit(1)

    if features.shape[1] != 4:
        print(json.dumps({"error": f"Нужно 4 признака, получено {features.shape[1]}"}))
        sys.exit(1)

    bundle  = load_model()
    model   = bundle["model"]
    classes = bundle["classes"]

    prediction = int(model.predict(features)[0])
    proba      = model.predict_proba(features)[0].tolist()

    result = {
        "prediction":    prediction,
        "class":         classes[prediction],
        "probabilities": {c: round(p, 4) for c, p in zip(classes, proba)},
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
