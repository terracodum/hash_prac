"""
Python pipeline: принимает признаки, возвращает предсказание в JSON.

Три режима ввода:
  1. JSON-строка:  predict.py '{"features": [5.1, 3.5, 1.4, 0.2]}'
  2. Файл:         predict.py --file input.json
  3. Числа argv:   predict.py 5.1 3.5 1.4 0.2

Выход (stdout):
  {"prediction": 0, "class": "setosa", "probabilities": {"setosa": 1.0, ...}}
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
            "Запусти сначала: train_model.py"
        )
    with open(model_path, "rb") as f:
        return pickle.load(f)


def parse_args(argv: list) -> list:
    if not argv:
        raise ValueError("Нет входных данных")

    if argv[0] == "--file":
        if len(argv) < 2:
            raise ValueError("--file требует путь к файлу")
        text = pathlib.Path(argv[1]).read_text(encoding="utf-8")
        return json.loads(text)["features"]

    if argv[0].startswith("{"):
        return json.loads(argv[0])["features"]

    return [float(v) for v in argv]


def main():
    try:
        raw = parse_args(sys.argv[1:])
        features = np.array(raw, dtype=np.float64).reshape(1, -1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
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
