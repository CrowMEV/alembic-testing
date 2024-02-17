# Alembic Testing

Примеры как можно тестировать alembic


## Настройка проекта

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -r requirements.txt
poetry install
```

### Установка pre-commit hooks

Установка хуков

```bash
pre-commit install
```

Для того чтобы прогнать `pre-commit` до выполнения коммита

```bash
pre-commit run --all-files
```

### Запуск тестов

```bash
poetry run pytest
```

полезные флаги для запуска pytest

```
--tb=[auto/long/short/line/native/no]: Управляет стилем трассировки.
-v / --verbose: Отображает все имена тестов, пройденных или не пройденных.
-l / --showlocals: Отображает локальные переменные рядом с трассировкой стека.
-lf / --last-failed: Запускает только тесты, которые завершились неудачей.
-x / --exitfirst: Останавливает тестовую сессию при первом сбое.
--pdb: Запускает интерактивный сеанс отладки в точке сбоя.
```
