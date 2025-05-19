import base64
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from CogEditor.models import Application
from CogNeural.LogisticRegression import process_time_features
from django.db.models import DurationField, ExpressionWrapper, F, IntegerField
from django.db.models.functions import Length
from django.shortcuts import render
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def index(request):
    # Ваш код для получения и обработки данных
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
        description_len=ExpressionWrapper(
            Length(F("e_description")),
            output_field=IntegerField(),
        ),
    ).values(
        "id",
        "subm_date",
        "status_id",
        "description_len",
        "number_of_participants",
        "requires_technical_support",
        "processing_time",
        "event_duration",
        "event_schedule__start",
        "event_schedule__end",
        # Убрали installation_deinstallation, так как их нет в данных
    )

    df = pd.DataFrame.from_records(applications)

    # 2. Преобразуем строки в datetime
    datetime_cols = [
        "subm_date",
        "event_schedule__start",
        "event_schedule__end",
    ]

    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    # 3. Обрабатываем временные признаки
    df = process_time_features(df)

    df["requires_technical_support"] = df["requires_technical_support"].astype(
        int
    )

    # Подготовка данных для модели
    X = df.drop(columns=["id", "status_id"])
    y = df["status_id"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Масштабирование и обучение модели
    scaler = StandardScaler()
    num_cols = [
        "number_of_participants",
        "processing_time_hours",
        "event_duration_hours",
        "days_until_event",
    ]
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])

    model = LogisticRegression(
        max_iter=1000, random_state=42, class_weight="balanced"
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Генерация графиков
    plt.switch_backend("Agg")  # Важно для работы в Django

    # График 1: Матрица ошибок
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Матрица ошибок")
    plt.xlabel("Предсказанные")
    plt.ylabel("Фактические")

    img1 = BytesIO()
    plt.savefig(img1, format="png")
    plt.close()
    img1.seek(0)
    plot1_url = base64.b64encode(img1.getvalue()).decode("utf8")

    # График 2: Важность признаков
    importance = pd.DataFrame(
        {"Признак": X.columns, "Коэффициент": model.coef_[0]}
    ).sort_values("Коэффициент", key=abs, ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x="Коэффициент", y="Признак", data=importance)
    plt.title("Важность признаков в логистической регрессии")

    img2 = BytesIO()
    plt.savefig(img2, format="png")
    plt.close()
    img2.seek(0)
    plot2_url = base64.b64encode(img2.getvalue()).decode("utf8")

    # Подготовка данных для таблицы
    report = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_html = report_df.to_html(classes="table table-striped")

    importance_html = importance.to_html(classes="table table-striped")

    # Отправка данных в шаблон
    context = {
        "plot1": plot1_url,
        "plot2": plot2_url,
        "classification_report": report_html,
        "feature_importance": importance_html,
        "data_head": df.to_html(classes="table table-striped"),
    }

    return render(request, "CogNeural/index.html", context)
