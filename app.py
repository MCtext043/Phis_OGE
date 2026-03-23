from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from flask import Flask, render_template, request


app = Flask(__name__)

# ----------------------------
# Data: справочник по ОГЭ
# ----------------------------


@dataclass(frozen=True)
class TopicItem:
    title: str
    body: str


@dataclass(frozen=True)
class Scientist:
    title: str
    field: str
    body: str


@dataclass(frozen=True)
class FormulaItem:
    formula: str
    note: str


@dataclass(frozen=True)
class Topic:
    title: str
    items: list[Any]


FORMULAS: list[Topic] = [
    Topic(
        title="Механика. Кинематика",
        items=[
            FormulaItem("v = s / t", "Скорость при равномерном движении."),
            FormulaItem("v = v0 + a·t", "Конечная скорость при равноускоренном движении."),
            FormulaItem("s = v0·t + a·t²/2", "Путь при равноускоренном движении."),
            FormulaItem("v² = v0² + 2a·s", "Связь скорости и перемещения (без времени)."),
        ],
    ),
    Topic(
        title="Механика. Динамика",
        items=[
            FormulaItem("F = m·a", "Второй закон Ньютона (равнодействующая)."),
            FormulaItem("P = m·g", "Вес тела (сила тяжести), P — сила тяжести."),
            FormulaItem("Fтр = μ·N", "Сила трения скольжения (модель)."),
            FormulaItem("ΣF = 0  =>  a = 0", "Условие равновесия поступательного движения."),
        ],
    ),
    Topic(
        title="Работа и энергия",
        items=[
            FormulaItem("A = F·s·cosα", "Работа силы при угле α между F и перемещением."),
            FormulaItem("Ek = m·v²/2", "Кинетическая энергия."),
            FormulaItem("Ep = m·g·h", "Потенциальная энергия вблизи поверхности Земли."),
            FormulaItem("η = Aполезн / Aзатрач", "КПД (если понадобится)."),
        ],
    ),
    Topic(
        title="Импульс и закон сохранения",
        items=[
            FormulaItem("p = m·v", "Импульс тела."),
            FormulaItem("J = F·Δt", "Импульс силы."),
            FormulaItem("p1 + p2 = p'1 + p'2", "Закон сохранения импульса (для замкнутой системы)."),
        ],
    ),
    Topic(
        title="Тепловые явления",
        items=[
            FormulaItem("Q = c·m·Δt", "Количество теплоты при нагревании/охлаждении."),
            FormulaItem("Q = λ·m", "Теплота фазового перехода (плавление/парообразование)."),
            FormulaItem("ΔU = Q − A", "Первый закон термодинамики (часто в задачах)."),
        ],
    ),
    Topic(
        title="Электрические явления",
        items=[
            FormulaItem("U = I·R", "Закон Ома."),
            FormulaItem("I = U / R", "Тот же закон, выраженный иначе."),
            FormulaItem("P = U·I", "Мощность электрического тока."),
            FormulaItem("Q = I²·R·t", "Закон Джоуля–Ленца (тепловое действие тока)."),
        ],
    ),
    Topic(
        title="Электрические цепи",
        items=[
            FormulaItem("Rпосл = R1 + R2 + ...", "Суммарное сопротивление при последовательном соединении."),
            FormulaItem("1/Rп = 1/R1 + 1/R2 + ...", "Обратная величина сопротивления при параллельном соединении."),
            FormulaItem("Uобщ = U1 + U2 + ...", "Падение напряжений при последовательном соединении."),
            FormulaItem("Iобщ = I1 + I2 + ...", "Токи ветвей при параллельном соединении."),
        ],
    ),
    Topic(
        title="Световые явления (оптика)",
        items=[
            FormulaItem("αпад = αотр", "Закон отражения света."),
            FormulaItem("1/F = 1/d + 1/d'", "Формула тонкой линзы (обобщённо)."),
            FormulaItem("k = h'/h = d'/d", "Увеличение линзы (со знаком в продвинутых задачах)."),
        ],
    ),
]


THEORY: list[Topic] = [
    Topic(
        title="Механика. Кинематика",
        items=[
            TopicItem(
                "Как читать условия",
                "Укажи, что дано: путь `s`, время `t`, скорость `v`, ускорение `a`, начальная скорость `v0`. Старайся выбрать формулы, в которых есть ровно эти величины.",
            ),
            TopicItem(
                "Типичные ловушки",
                "1) Перепутали `v` и `v0`. 2) Подставили ускорение с неправильным знаком. 3) Не разделили «равномерно» и «равноускоренно».",
            ),
        ],
    ),
    Topic(
        title="Механика. Динамика",
        items=[
            TopicItem(
                "Равнодействующая сил",
                "Записывай сумму сил вдоль нужного направления. Если тело движется равномерно, то ΣF = 0 (при отсутствии других оговорок).",
            ),
            TopicItem(
                "Трение",
                "Для задач ОГЭ трение часто берут как `Fтр = μN`. Учти, что `N` — это сила реакции опоры (может зависеть от угла и т.д.).",
            ),
        ],
    ),
    Topic(
        title="Работа и энергия",
        items=[
            TopicItem(
                "Связь с перемещением",
                "Работа зависит от угла между направлением силы и перемещением: `A = F·s·cosα`. Если α = 90°, работа равна нулю.",
            ),
            TopicItem(
                "Когда применять закон сохранения энергии",
                "Если силы типа трения несущественны или не указаны как ключевые, удобно переходить к `Ek` и `Ep` и составлять баланс.",
            ),
        ],
    ),
    Topic(
        title="Тепловые явления",
        items=[
            TopicItem(
                "Нагрев без фазового перехода",
                "Используй `Q = c·m·Δt`: сначала найди Δt = t2 − t1, затем вычисляй количество теплоты.",
            ),
            TopicItem(
                "Фазовый переход",
                "При плавлении/кипении температура может быть постоянной, тогда применяется `Q = λ·m`.",
            ),
        ],
    ),
    Topic(
        title="Электричество",
        items=[
            TopicItem(
                "Единицы измерения",
                "Проверяй, что U в вольтах, I в амперах, R в омах, а ток — в ветвях/общий — в нужном виде.",
            ),
            TopicItem(
                "Цепи: последовательное и параллельное",
                "В последовательном больше подходит `Rпосл = R1 + R2 + ...`, а в параллельном — формула для `1/R`. Также меняется логика для токов и напряжений.",
            ),
        ],
    ),
    Topic(
        title="Оптика",
        items=[
            TopicItem(
                "Отражение",
                "Для зеркала важен закон: угол падения равен углу отражения.",
            ),
            TopicItem(
                "Линзы",
                "В задачах на изображения используется формула тонкой линзы и увеличение. Старайся явно выписать что является d (расстояние до предмета) и d' (до изображения).",
            ),
        ],
    ),
]


SCIENTISTS: list[Scientist] = [
    Scientist(
        title="Исаак Ньютон",
        field="Механика",
        body="Законы движения и закон всемирного тяготения; идея «равнодействующая сил → ускорение».",
    ),
    Scientist(
        title="Галилео Галилей",
        field="Кинематика",
        body="Изучение движения и эксперименты; представления о равномерном и равноускоренном движении.",
    ),
    Scientist(
        title="Архимед",
        field="Гидростатика",
        body="Закон Архимеда и выталкивающая сила — ключ к задачам про плавание тел.",
    ),
    Scientist(
        title="Блез Паскаль",
        field="Давление",
        body="Принцип передачи давления в жидкостях — помогает связывать силы и площади.",
    ),
    Scientist(
        title="Шарль-Огюстен де Кулон",
        field="Электростатика",
        body="Закон Кулона для взаимодействия зарядов — основа понимания электростатических сил.",
    ),
    Scientist(
        title="Георг Ом",
        field="Электрические цепи",
        body="Закон Ома и связь U, I и R; без него сложно решать задачи по цепям.",
    ),
    Scientist(
        title="Майкл Фарадей",
        field="Индукция",
        body="Электромагнитная индукция: появление ЭДС при изменении магнитного потока.",
    ),
    Scientist(
        title="Джеймс Клерк Максвелл",
        field="Электромагнетизм",
        body="Уравнения электромагнитного поля — целостная теория электричества и магнетизма.",
    ),
    Scientist(
        title="Генрих Герц",
        field="Электромагнитные волны",
        body="Экспериментальное подтверждение существования электромагнитных волн.",
    ),
]


# ----------------------------
# Quiz: тест на закрепление
# ----------------------------


@dataclass(frozen=True)
class Question:
    text: str
    options: list[str]
    correct_index: int
    explanation: str


QUESTIONS: list[Question] = [
    Question(
        text="Тело движется равномерно. Как связаны путь s, скорость v и время t?",
        options=["s = v·t", "v = s + t", "t = v·s", "v = s/t²"],
        correct_index=0,
        explanation="При равномерном движении скорость постоянна, поэтому s = v·t.",
    ),
    Question(
        text="При равноускоренном движении чему равно ускорение a, если известно v0, v и t?",
        options=["a = (v − v0)/t", "a = v·t", "a = (v0 − v)·t", "a = t/(v − v0)"],
        correct_index=0,
        explanation="Из v = v0 + a·t следует a = (v − v0)/t.",
    ),
    Question(
        text="Сила трения скольжения можно оценить по формуле:",
        options=["Fтр = μ·N", "Fтр = μ/N", "Fтр = m·g/μ", "Fтр = μ·m"],
        correct_index=0,
        explanation="В школьной модели: Fтр = μ·N, где N — сила реакции опоры.",
    ),
    Question(
        text="Работа силы A при угле α между направлением силы и перемещением равна:",
        options=["A = F·s·cosα", "A = F/s·cosα", "A = F·cosα", "A = s·sinα"],
        correct_index=0,
        explanation="Проекция силы на направление перемещения даёт косинус: A = F·s·cosα.",
    ),
    Question(
        text="Кинетическая энергия тела выражается формулой:",
        options=["Ek = m·v²/2", "Ek = m·v/2", "Ek = m·v²", "Ek = m·g·h"],
        correct_index=0,
        explanation="Ek зависит от квадрата скорости: Ek = m·v²/2.",
    ),
    Question(
        text="Количество теплоты при нагревании без фазового перехода:",
        options=["Q = c·m·Δt", "Q = λ·m", "Q = I²·R·t", "Q = F·s"],
        correct_index=0,
        explanation="При изменении температуры без смены агрегатного состояния используется Q = c·m·Δt.",
    ),
    Question(
        text="Закон Ома записывается как:",
        options=["U = I·R", "R = U/I²", "I = R·U", "U = I + R"],
        correct_index=0,
        explanation="Классическая форма: U = I·R.",
    ),
    Question(
        text="Мощность электрического тока равна:",
        options=["P = U·I", "P = U/I", "P = I/R", "P = U·R"],
        correct_index=0,
        explanation="Мощность: P = U·I (и эквивалентно P = I²R = U²/R).",
    ),
    Question(
        text="Тепловое действие тока (закон Джоуля–Ленца):",
        options=["Q = I²·R·t", "Q = I·R/t", "Q = U·t/R", "Q = I·t"],
        correct_index=0,
        explanation="В школьной записи: Q = I²·R·t.",
    ),
    Question(
        text="Закон отражения света на плоском зеркале:",
        options=["αпад = αотр", "αпад + αотр = 90°", "αпад = 0", "αотр = 2αпад"],
        correct_index=0,
        explanation="Угол падения равен углу отражения относительно нормали.",
    ),
]

# Иконки Bootstrap Icons по смысловым разделам.
TOPIC_ICONS: dict[str, str] = {
    "Механика. Кинематика": "bi-speedometer2",
    "Механика. Динамика": "bi-arrows-move",
    "Работа и энергия": "bi-lightning-charge",
    "Импульс и закон сохранения": "bi-arrow-left-right",
    "Тепловые явления": "bi-thermometer-sun",
    "Электрические явления": "bi-lightning",
    "Электрические цепи": "bi-diagram-3",
    "Световые явления (оптика)": "bi-sun",
    "Электричество": "bi-lightning",
    "Оптика": "bi-eye",
}

FIELD_ICONS: dict[str, str] = {
    "Механика": "bi-gear",
    "Кинематика": "bi-speedometer2",
    "Гидростатика": "bi-droplet",
    "Давление": "bi-arrows-collapse",
    "Электростатика": "bi-lightning-charge",
    "Электрические цепи": "bi-diagram-3",
    "Индукция": "bi-magnet",
    "Электромагнетизм": "bi-broadcast",
    "Электромагнитные волны": "bi-wifi",
}


# ----------------------------
# Routes
# ----------------------------


@app.route("/")
def index() -> str:
    return render_template(
        "index.html",
        formulas_count=sum(len(t.items) for t in FORMULAS),
        theory_topics=len(THEORY),
        scientists_count=len(SCIENTISTS),
    )


@app.route("/formulas")
def formulas() -> str:
    return render_template("formulas.html", topics=FORMULAS, topic_icons=TOPIC_ICONS)


@app.route("/theory")
def theory() -> str:
    return render_template("theory.html", topics=THEORY, topic_icons=TOPIC_ICONS)


@app.route("/scientists")
def scientists() -> str:
    return render_template(
        "scientists.html",
        scientists=SCIENTISTS,
        field_icons=FIELD_ICONS,
    )


def _evaluate_quiz(form: Any) -> tuple[int, list[tuple[Question, int, int]]]:
    """
    Возвращает:
    - score (кол-во верных),
    - details: [(question, selected_index, correct_index), ...]
    """
    details: list[tuple[Question, int, int]] = []
    score = 0

    for i, q in enumerate(QUESTIONS):
        raw = form.get(f"q{i}")
        try:
            selected = int(raw) if raw is not None else -1
        except (TypeError, ValueError):
            selected = -1

        if selected == q.correct_index:
            score += 1
        details.append((q, selected, q.correct_index))

    return score, details


@app.route("/quiz", methods=["GET", "POST"])
def quiz() -> str:
    if request.method == "POST":
        score, details = _evaluate_quiz(request.form)
        total = len(QUESTIONS)
        percent = 0
        if total:
            percent = int(math.floor(100 * score / total))

        return render_template(
            "quiz.html",
            questions=QUESTIONS,
            submitted=True,
            score=score,
            total=total,
            percent=percent,
            details=details,
        )

    return render_template(
        "quiz.html",
        questions=QUESTIONS,
        submitted=False,
    )


if __name__ == "__main__":
    # Для локальной разработки.
    app.run(host="127.0.0.1", port=5000, debug=True)

