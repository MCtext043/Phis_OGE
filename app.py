from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

from flask import Flask, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = "physics-oge-secret-key"


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
    items: list[FormulaItem]


@dataclass(frozen=True)
class Question:
    text: str
    options: list[str]
    correct_index: int
    explanation: str


FORMULAS: list[Topic] = [
    Topic(
        title="Механика: движение и кинематика",
        items=[
            FormulaItem("v = s / t", "Средняя скорость при равномерном движении."),
            FormulaItem("x = x0 + vx·t", "Координата при равномерном прямолинейном движении."),
            FormulaItem("vx = v0x + ax·t", "Проекция скорости при равноускоренном движении."),
            FormulaItem("sx = v0x·t + ax·t²/2", "Проекция перемещения."),
            FormulaItem("x = x0 + v0x·t + ax·t²/2", "Координата при равноускоренном движении."),
            FormulaItem("vx² = v0x² + 2ax·sx", "Связь скорости и перемещения без времени."),
            FormulaItem("g = 9.8 м/с² (приближённо 10)", "Ускорение свободного падения."),
            FormulaItem("v = 2πR / T", "Скорость при движении по окружности."),
            FormulaItem("aц = v² / R", "Центростремительное ускорение."),
            FormulaItem("ν = 1 / T", "Частота через период."),
        ],
    ),
    Topic(
        title="Механика: силы, статика, гидростатика",
        items=[
            FormulaItem("ρ = m / V", "Плотность вещества."),
            FormulaItem("F = m·a", "Второй закон Ньютона."),
            FormulaItem("Fтяж = m·g", "Сила тяжести."),
            FormulaItem("Fтр = μ·N", "Сила трения скольжения."),
            FormulaItem("Fупр = k·Δl", "Закон Гука."),
            FormulaItem("F = G·m1·m2 / R²", "Закон всемирного тяготения."),
            FormulaItem("p = F / S", "Давление твёрдого тела."),
            FormulaItem("p = patm + ρgh", "Давление внутри жидкости."),
            FormulaItem("FАрх = ρж·g·Vпогр", "Выталкивающая сила Архимеда."),
            FormulaItem("M = F·l", "Момент силы."),
            FormulaItem("M1 + M2 + ... = 0", "Условие равновесия рычага."),
        ],
    ),
    Topic(
        title="Механика: импульс, работа, энергия, колебания",
        items=[
            FormulaItem("p = m·v", "Импульс тела."),
            FormulaItem("F·Δt = Δp", "Импульс силы."),
            FormulaItem("pсист = const", "Закон сохранения импульса в замкнутой системе."),
            FormulaItem("A = F·s·cosα", "Механическая работа."),
            FormulaItem("N = A / t", "Мощность."),
            FormulaItem("Ek = m·v² / 2", "Кинетическая энергия."),
            FormulaItem("Ep = m·g·h", "Потенциальная энергия в поле тяжести."),
            FormulaItem("Eмех = Ek + Ep", "Полная механическая энергия."),
            FormulaItem("Eмех = const", "Закон сохранения механической энергии (без потерь)."),
            FormulaItem("η = Aпол / Aзатр", "КПД."),
            FormulaItem("ν = 1 / T", "Связь частоты и периода колебаний."),
            FormulaItem("vволны = λ·ν = λ / T", "Скорость волны."),
        ],
    ),
    Topic(
        title="Тепловые явления и термодинамика",
        items=[
            FormulaItem("Q = c·m·(t2 − t1)", "Количество теплоты при нагревании/охлаждении."),
            FormulaItem("Q1 + Q2 + ... = 0", "Уравнение теплового баланса."),
            FormulaItem("Q = L·m", "Теплота парообразования/конденсации."),
            FormulaItem("Q = λ·m", "Теплота плавления/кристаллизации."),
            FormulaItem("Q = q·m", "Теплота сгорания топлива."),
            FormulaItem("η = Aпол / Qзатрач", "КПД теплового двигателя (упрощённо)."),
        ],
    ),
    Topic(
        title="Электродинамика и магнитные явления",
        items=[
            FormulaItem("I = q / t", "Сила тока."),
            FormulaItem("U = A / q", "Напряжение."),
            FormulaItem("R = ρ·l / S", "Сопротивление проводника."),
            FormulaItem("I = U / R", "Закон Ома для участка цепи."),
            FormulaItem("Rпосл = R1 + R2 + ...", "Последовательное соединение сопротивлений."),
            FormulaItem("1/Rпар = 1/R1 + 1/R2 + ...", "Параллельное соединение сопротивлений."),
            FormulaItem("A = U·I·t", "Работа электрического тока."),
            FormulaItem("P = U·I", "Мощность тока."),
            FormulaItem("Q = I²·R·t", "Закон Джоуля-Ленца."),
        ],
    ),
    Topic(
        title="Оптика и квантовые явления",
        items=[
            FormulaItem("αпад = αотр", "Закон отражения света."),
            FormulaItem("D = 1 / F", "Оптическая сила линзы."),
            FormulaItem("1/F = 1/d + 1/f", "Формула тонкой линзы (школьная запись)."),
            FormulaItem("Γ = h'/h = f/d", "Линейное увеличение."),
            FormulaItem("N(t) = N0·2^(-t/T1/2)", "Закон радиоактивного распада (качественно/для задач)."),
        ],
    ),
]


SCIENTISTS: list[Scientist] = [
    Scientist("Исаак Ньютон", "Механика", "Законы движения и всемирного тяготения."),
    Scientist("Галилео Галилей", "Кинематика", "Исследование движения тел и свободного падения."),
    Scientist("Архимед", "Гидростатика", "Закон Архимеда и условия плавания тел."),
    Scientist("Блез Паскаль", "Давление", "Закон Паскаля и гидравлические устройства."),
    Scientist("Георг Ом", "Электричество", "Закон Ома для участка электрической цепи."),
    Scientist("Майкл Фарадей", "Индукция", "Электромагнитная индукция."),
    Scientist("Джеймс Максвелл", "Электромагнетизм", "Теория электромагнитного поля."),
]


QUESTIONS_BANK: list[Question] = [
    Question("Как записывается формула средней скорости?", ["v = s/t", "v = t/s", "v = s+t", "v = s·t"], 0, "Средняя скорость - это отношение пути ко времени."),
    Question("Формула второго закона Ньютона:", ["F = m·a", "F = m/a", "F = a/m", "F = m+ a"], 0, "Равнодействующая сила равна произведению массы на ускорение."),
    Question("Формула силы тяжести:", ["F = m·g", "F = m/g", "F = g/m", "F = m+g"], 0, "Сила тяжести равна m·g."),
    Question("Формула силы трения скольжения:", ["Fтр = μN", "Fтр = N/μ", "Fтр = μ/N", "Fтр = μm"], 0, "В школьных задачах используется Fтр = μN."),
    Question("Закон Гука:", ["Fупр = k·Δl", "Fупр = Δl/k", "Fупр = k+Δl", "Fупр = k/Δl"], 0, "Сила упругости пропорциональна удлинению."),
    Question("Формула плотности:", ["ρ = m/V", "ρ = V/m", "ρ = m·V", "ρ = m+V"], 0, "Плотность - масса единицы объёма."),
    Question("Формула давления твёрдого тела:", ["p = F/S", "p = S/F", "p = F·S", "p = F+S"], 0, "Давление равно силе, делённой на площадь."),
    Question("Гидростатическое давление в жидкости:", ["p = patm + ρgh", "p = ρg/h", "p = ρh/g", "p = ρ+g+h"], 0, "В жидкости на глубине добавляется ρgh."),
    Question("Сила Архимеда:", ["Fарх = ρжgV", "Fарх = ρж/V", "Fарх = ρж+g+V", "Fарх = ρжg/V"], 0, "Зависит от плотности жидкости и объёма погружённой части."),
    Question("Формула момента силы:", ["M = F·l", "M = F/l", "M = l/F", "M = F+l"], 0, "Момент силы - произведение силы на плечо."),
    Question("Формула работы силы:", ["A = F·s·cosα", "A = F/s", "A = s/F", "A = F+s"], 0, "Работа зависит от угла между силой и перемещением."),
    Question("Формула мощности:", ["N = A/t", "N = t/A", "N = A+t", "N = A·t"], 0, "Мощность - работа за единицу времени."),
    Question("Кинетическая энергия:", ["Ek = mv²/2", "Ek = m/v²", "Ek = mv/2", "Ek = mgh"], 0, "Кинетическая энергия зависит от квадрата скорости."),
    Question("Потенциальная энергия у поверхности Земли:", ["Ep = mgh", "Ep = mg/h", "Ep = m+g+h", "Ep = gh/m"], 0, "Для высоты h используем mgh."),
    Question("Импульс тела:", ["p = m·v", "p = m/v", "p = v/m", "p = m+v"], 0, "Импульс равен произведению массы на скорость."),
    Question("Закон сохранения импульса верен для...", ["замкнутой системы", "любой системы с трением", "только покоящихся тел", "только жидкостей"], 0, "Без внешних сил импульс системы сохраняется."),
    Question("Связь частоты и периода:", ["ν = 1/T", "ν = T", "ν = 1+T", "ν = T²"], 0, "Частота обратна периоду."),
    Question("Скорость волны:", ["v = λν", "v = λ/ν", "v = ν/λ", "v = λ+ν"], 0, "Скорость волны - длина волны на частоту."),
    Question("Закон Ома:", ["I = U/R", "I = UR", "I = R/U", "I = U+R"], 0, "Сила тока прямо пропорциональна напряжению."),
    Question("Формула сопротивления проводника:", ["R = ρl/S", "R = ρS/l", "R = l/ρS", "R = ρ+l+S"], 0, "Сопротивление пропорционально длине и обратно площади."),
    Question("Работа электрического тока:", ["A = UIt", "A = UI/t", "A = U+I+t", "A = U/I"], 0, "Работа тока равна произведению U, I и t."),
    Question("Мощность тока:", ["P = UI", "P = U/I", "P = I/U", "P = U+I"], 0, "Мощность в цепи постоянного тока: P = UI."),
    Question("Закон Джоуля-Ленца:", ["Q = I²Rt", "Q = IR/t", "Q = UIt", "Q = I+R+t"], 0, "Количество теплоты в проводнике: I^2Rt."),
    Question("Последовательное соединение сопротивлений:", ["R = R1 + R2 + ...", "1/R = 1/R1 + 1/R2", "R = R1R2", "R = R1/R2"], 0, "При последовательном соединении сопротивления складываются."),
    Question("Параллельное соединение сопротивлений:", ["1/R = 1/R1 + 1/R2 + ...", "R = R1 + R2", "R = R1 - R2", "R = R1R2"], 0, "Для параллели складываются обратные сопротивления."),
    Question("Закон отражения света:", ["угол падения равен углу отражения", "угол падения вдвое больше", "угол отражения всегда 90°", "углы не связаны"], 0, "Углы измеряются от нормали."),
    Question("Оптическая сила линзы:", ["D = 1/F", "D = F", "D = F²", "D = 1/F²"], 0, "Оптическая сила обратна фокусному расстоянию."),
    Question("Формула тонкой линзы:", ["1/F = 1/d + 1/f", "F = d+f", "1/F = d/f", "F = d/f"], 0, "Связывает фокусное расстояние и расстояния до предмета/изображения."),
    Question("Линейное увеличение линзы:", ["Γ = h'/h", "Γ = h+h'", "Γ = h/h'", "Γ = hh'"], 0, "Увеличение - отношение высот изображения и предмета."),
    Question("Количество теплоты при нагревании:", ["Q = cmΔt", "Q = c/mΔt", "Q = cm/Δt", "Q = c+m+Δt"], 0, "Нужно умножить теплоёмкость, массу и изменение температуры."),
    Question("Удельная теплота плавления:", ["Q = λm", "Q = m/λ", "Q = λ/m", "Q = λ+m"], 0, "Для плавления и кристаллизации: Q = λm."),
    Question("Удельная теплота парообразования:", ["Q = Lm", "Q = L/m", "Q = m/L", "Q = L+m"], 0, "Для испарения и конденсации: Q = Lm."),
    Question("Удельная теплота сгорания:", ["Q = qm", "Q = q/m", "Q = m/q", "Q = q+m"], 0, "Количество теплоты при сгорании топлива."),
    Question("Тепловой баланс для изолированной системы:", ["Q1 + Q2 + ... = 0", "Q1 = Q2 = 0", "Q = const", "Q1Q2 = 0"], 0, "Сумма полученных и отданных количеств теплоты равна нулю."),
    Question("Скорость при движении по окружности:", ["v = 2πR/T", "v = 2πT/R", "v = R/T²", "v = RT"], 0, "За период тело проходит длину окружности."),
    Question("Центростремительное ускорение:", ["aц = v²/R", "aц = R/v²", "aц = v/R²", "aц = vR"], 0, "Направлено к центру окружности."),
    Question("Координата при равномерном движении:", ["x = x0 + vt", "x = x0 - vt²", "x = vt", "x = x0/vt"], 0, "Линейная зависимость от времени."),
    Question("Проекция скорости при равноускоренном движении:", ["vx = v0x + axt", "vx = v0x/t", "vx = axt²", "vx = v0x - ax/t"], 0, "Скорость меняется линейно со временем."),
    Question("Проекция перемещения при равноускоренном движении:", ["sx = v0xt + axt²/2", "sx = v0x + axt", "sx = axt", "sx = v0x/t"], 0, "Стандартная формула кинематики."),
    Question("Связь скоростей и перемещения:", ["vx² = v0x² + 2axsx", "vx = v0x + 2axsx", "vx² = v0x + 2axsx", "vx² = v0x² + axsx"], 0, "Формула без времени."),
    Question("Сила тока - это...", ["q/t", "qt", "q+t", "t/q"], 0, "Определение силы тока: заряд за единицу времени."),
    Question("Напряжение - это...", ["A/q", "Aq", "q/A", "A+q"], 0, "Работа поля по переносу единичного заряда."),
    Question("КПД механизма:", ["η = Aпол/Aзатр", "η = Aзатр/Aпол", "η = Aпол + Aзатр", "η = Aпол - Aзатр"], 0, "КПД всегда меньше 1 (или 100%)."),
    Question("Механическая энергия включает...", ["кинетическую и потенциальную", "только кинетическую", "только потенциальную", "только внутреннюю"], 0, "Eмех = Ek + Ep."),
    Question("При отсутствии потерь механическая энергия...", ["сохраняется", "исчезает", "всегда растёт", "всегда уменьшается"], 0, "Закон сохранения механической энергии."),
    Question("Радиоактивность - это...", ["самопроизвольное превращение ядер", "распад молекул воды", "испарение вещества", "намагничивание"], 0, "Явление связано с превращениями атомных ядер."),
    Question("Период полураспада - это время, за которое...", ["распадается половина исходных ядер", "распадаются все ядра", "масса удваивается", "энергия падает в 4 раза"], 0, "Определение периода полураспада."),
    Question("В опыте Резерфорда было показано...", ["существование компактного ядра", "что атом неделим", "что ядро отрицательно", "отсутствие электронов"], 0, "Большая часть массы и положительного заряда сосредоточена в ядре."),
    Question("Изотопы - это атомы с одинаковым...", ["зарядом ядра, но разным числом нейтронов", "числом нейтронов и разным зарядом", "числом электронов и протонов", "массовым числом и зарядом"], 0, "Изотопы одного элемента имеют одинаковое Z."),
    Question("Какая величина измеряется в омах?", ["сопротивление", "сила тока", "напряжение", "мощность"], 0, "Ом - единица сопротивления."),
]


TOPIC_ICONS: dict[str, str] = {
    "Механика: движение и кинематика": "bi-speedometer2",
    "Механика: силы, статика, гидростатика": "bi-gear",
    "Механика: импульс, работа, энергия, колебания": "bi-lightning-charge",
    "Тепловые явления и термодинамика": "bi-thermometer-sun",
    "Электродинамика и магнитные явления": "bi-lightning",
    "Оптика и квантовые явления": "bi-eye",
}


FIELD_ICONS: dict[str, str] = {
    "Механика": "bi-gear",
    "Кинематика": "bi-speedometer2",
    "Гидростатика": "bi-droplet",
    "Давление": "bi-arrows-collapse",
    "Электричество": "bi-lightning-charge",
    "Индукция": "bi-magnet",
    "Электромагнетизм": "bi-broadcast",
}


def _build_quiz_set() -> list[dict[str, Any]]:
    selected = random.sample(QUESTIONS_BANK, k=5)
    payload: list[dict[str, Any]] = []
    for q in selected:
        options = q.options[:]
        correct_text = q.options[q.correct_index]
        random.shuffle(options)
        payload.append(
            {
                "text": q.text,
                "options": options,
                "correct_index": options.index(correct_text),
                "explanation": q.explanation,
            }
        )
    return payload


def _evaluate_quiz(form: Any, questions: list[dict[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
    details: list[dict[str, Any]] = []
    score = 0

    for i, q in enumerate(questions):
        raw = form.get(f"q{i}")
        try:
            selected = int(raw) if raw is not None else -1
        except (TypeError, ValueError):
            selected = -1

        correct = q["correct_index"]
        if selected == correct:
            score += 1

        details.append(
            {
                "question": q["text"],
                "options": q["options"],
                "selected": selected,
                "correct": correct,
                "explanation": q["explanation"],
            }
        )

    return score, details


@app.route("/")
def index() -> str:
    return render_template(
        "index.html",
        formulas_count=sum(len(t.items) for t in FORMULAS),
        scientists_count=len(SCIENTISTS),
    )


@app.route("/formulas")
def formulas() -> str:
    return render_template("formulas.html", topics=FORMULAS, topic_icons=TOPIC_ICONS)


@app.route("/scientists")
def scientists() -> str:
    return render_template("scientists.html", scientists=SCIENTISTS, field_icons=FIELD_ICONS)


@app.route("/quiz", methods=["GET", "POST"])
def quiz() -> str:
    if request.method == "GET":
        questions = _build_quiz_set()
        session["quiz_questions"] = questions
        return render_template("quiz.html", questions=questions, submitted=False)

    questions = session.get("quiz_questions")
    if not questions:
        return redirect(url_for("quiz"))

    score, details = _evaluate_quiz(request.form, questions)
    total = len(questions)
    percent = int(math.floor(100 * score / total)) if total else 0
    return render_template(
        "quiz.html",
        questions=questions,
        submitted=True,
        score=score,
        total=total,
        percent=percent,
        details=details,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

