from datetime import timedelta

import pandas as pd
from CogEditor.models import AgreedStatus, Application, Schedule
from django.db.models import DurationField, ExpressionWrapper, F


# 3. Теперь можем обрабатывать временные признаки
def process_time_features(df):
    # Сначала создаем список реально существующих столбцов
    existing_cols = df.columns.tolist()

    # Определяем, какие столбцы мы действительно можем удалить
    cols_to_drop = [
        "processing_time",
        "event_duration",
        "subm_date",
        "event_schedule__start",
        "event_schedule__end",
        "installation_deinstallation__start",
        "installation_deinstallation__end",
    ]

    # Оставляем только те столбцы, которые есть в DataFrame
    actual_cols_to_drop = [col for col in cols_to_drop if col in existing_cols]

    # Преобразуем timedelta в часы (если столбцы существуют)
    if "processing_time" in existing_cols:
        df["processing_time_hours"] = (
            df["processing_time"].dt.total_seconds() / 3600
        )
    if "event_duration" in existing_cols:
        df["event_duration_hours"] = (
            df["event_duration"].dt.total_seconds() / 3600
        )

    # Извлекаем признаки из дат (если столбцы существуют)
    if "subm_date" in existing_cols:
        df["subm_day_of_week"] = df["subm_date"].dt.dayofweek
        df["subm_hour"] = df["subm_date"].dt.hour
    if "event_schedule__start" in existing_cols:
        df["event_start_hour"] = df["event_schedule__start"].dt.hour
        df["event_day_of_week"] = df["event_schedule__start"].dt.dayofweek

    # Время между подачей заявки и мероприятием (если оба столбца существуют)
    if (
        "event_schedule__start" in existing_cols
        and "subm_date" in existing_cols
    ):
        df["days_until_event"] = (
            df["event_schedule__start"] - df["subm_date"]
        ).dt.days

    # Удаляем только существующие столбцы
    if actual_cols_to_drop:
        df = df.drop(columns=actual_cols_to_drop)

    return df


def main():
    # 1. Собираем данные и сразу преобразуем в DataFrame
    applications = Application.objects.annotate(
        processing_time=ExpressionWrapper(
            F("event_schedule__start") - F("subm_date"),
            output_field=DurationField(),
        ),
        event_duration=ExpressionWrapper(
            F("event_schedule__end") - F("event_schedule__start"),
            output_field=DurationField(),
        ),
    ).values(
        "id",
        "subm_date",
        "status_id",
        "number_of_participants",
        "requires_technical_support",
        "processing_time",
        "event_duration",
        "event_schedule__start",
        "event_schedule__end",
        "installation_deinstallation__start",
        "installation_deinstallation__end",
    )

    df = pd.DataFrame.from_records(applications)

    # 2. Преобразуем строки в datetime
    datetime_cols = [
        "subm_date",
        "event_schedule__start",
        "event_schedule__end",
        "installation_deinstallation__start",
        "installation_deinstallation__end",
    ]

    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col])

    # Применяем функцию только после преобразования типов
    df = process_time_features(df)

    # Дальнейшая обработка и моделирование...
    print(df.head())

    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    # Ваши данные (предположим, что df уже загружен)
    print("Первые 5 строк данных:")
    print(df.head())
    print("\nИнформация о данных:")
    print(df.info())

    # 1. Подготовка данных
    # Преобразуем булевы значения в числовые
    df["requires_technical_support"] = df["requires_technical_support"].astype(
        int
    )

    # 2. Разделение на признаки и целевую переменную
    x = df.drop(columns=["id", "status_id"])
    y = df["status_id"]

    # 3. Разделение на обучающую и тестовую выборки
    x_train, X_test, y_train, y_test = train_test_split(
        x, y, test_size=0.3, random_state=42
    )

    # 4. Масштабирование числовых признаков
    scaler = StandardScaler()
    num_cols = [
        "number_of_participants",
        "processing_time_hours",
        "event_duration_hours",
        "days_until_event",
    ]

    x_train[num_cols] = scaler.fit_transform(x_train[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])

    # 5. Обучение модели
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight="balanced",  # Учитываем дисбаланс классов
    )
    model.fit(x_train, y_train)

    # 6. Оценка модели
    y_pred = model.predict(X_test)

    print("\nОтчет о классификации:")
    print(classification_report(y_test, y_pred))

    # Матрица ошибок
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Матрица ошибок")
    plt.xlabel("Предсказанные")
    plt.ylabel("Фактические")
    plt.show()

    # 7. Анализ важности признаков
    importance = pd.DataFrame(
        {"Признак": x.columns, "Коэффициент": model.coef_[0]}
    ).sort_values("Коэффициент", key=abs, ascending=False)

    print("\nВажность признаков:")
    print(importance)

    # 8. Визуализация важности признаков
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Коэффициент", y="Признак", data=importance)
    plt.title("Важность признаков в логистической регрессии")
    plt.show()
