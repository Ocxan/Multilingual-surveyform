from flask import Flask, request, session, redirect, url_for, render_template
from google.cloud import bigquery
from datetime import datetime
from google.api_core.exceptions import NotFound

app = Flask(__name__)
app.secret_key = 'your_secret_key'

project_id = 'smooth-topic-238416'
client = bigquery.Client(project=project_id)

dataset_id = 'FormResult'
table_id = 'Results'
table_ref = client.dataset(dataset_id).table(table_id)

schema = [
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("email", "STRING"),
    bigquery.SchemaField("language", "STRING"),
    bigquery.SchemaField("question_number", "INTEGER"),
    bigquery.SchemaField("progress", "FLOAT"),
    bigquery.SchemaField("axis", "STRING"),
    bigquery.SchemaField("answer", "INTEGER")
]

table_id_full = f"{project_id}.{dataset_id}.{table_id}"

table = bigquery.Table(table_id_full, schema=schema)

try:
    client.get_table(table_ref)
    print("Table exists")
except NotFound:
    table = client.create_table(table)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

questions = [
    {"en": "Am the life of the party.", "ru": "Я душа компании.", "es": "Soy el alma de la fiesta.", "axis": 1},
    {"en": "Feel little concern for others.", "ru": "Мало забочусь о других.", "es": "Siento poca preocupación por los demás.", "axis": -2},
    {"en": "Am always prepared.", "ru": "Всегда готов.", "es": "Siempre estoy preparado.", "axis": 3},
    {"en": "Get stressed out easily.", "ru": "Легко стрессую.", "es": "Me estreso fácilmente.", "axis": -4},
    {"en": "Have a rich vocabulary.", "ru": "У меня богатый словарный запас.", "es": "Tengo un vocabulario rico.", "axis": 5},
    {"en": "Don't talk a lot.", "ru": "Мало говорю.", "es": "No hablo mucho.", "axis": -1},
    {"en": "Am interested in people.", "ru": "Интересуюсь людьми.", "es": "Estoy interesado en la gente.", "axis": 2},
    {"en": "Leave my belongings around.", "ru": "Оставляю свои вещи повсюду.", "es": "Dejo mis pertenencias por ahí.", "axis": -3},
    {"en": "Am relaxed most of the time.", "ru": "Большую часть времени расслаблен.", "es": "Estoy relajado la mayor parte del tiempo.", "axis": 4},
    {"en": "Have difficulty understanding abstract ideas.", "ru": "Испытываю трудности с пониманием абстрактных идей.", "es": "Tengo dificultad para entender ideas abstractas.", "axis": -5},
    {"en": "Feel comfortable around people.", "ru": "Чувствую себя комфортно среди людей.", "es": "Me siento cómodo alrededor de la gente.", "axis": 1},
    {"en": "Insult people.", "ru": "Оскорбляю людей.", "es": "Insulto a la gente.", "axis": -2},
    {"en": "Pay attention to details.", "ru": "Обращаю внимание на детали.", "es": "Presto atención a los detalles.", "axis": 3},
    {"en": "Worry about things.", "ru": "Беспокоюсь о вещах.", "es": "Me preocupo por las cosas.", "axis": -4},
    {"en": "Have a vivid imagination.", "ru": "У меня богатое воображение.", "es": "Tengo una imaginación vívida.", "axis": 5},
    {"en": "Keep in the background.", "ru": "Держусь на заднем плане.", "es": "Me mantengo en segundo plano.", "axis": -1},
    {"en": "Sympathize with others' feelings.", "ru": "Сочувствую чувствам других.", "es": "Simpatizo con los sentimientos de los demás.", "axis": 2},
    {"en": "Make a mess of things.", "ru": "Создаю беспорядок.", "es": "Hago un lío de las cosas.", "axis": -3},
    {"en": "Seldom feel blue.", "ru": "Редко грущу.", "es": "Rara vez me siento triste.", "axis": 4},
    {"en": "Am not interested in abstract ideas.", "ru": "Не интересуюсь абстрактными идеями.", "es": "No estoy interesado en ideas abstractas.", "axis": -5},
    {"en": "Start conversations.", "ru": "Начинаю разговоры.", "es": "Inicio conversaciones.", "axis": 1},
    {"en": "Am not interested in other people's problems.", "ru": "Не интересуюсь проблемами других людей.", "es": "No estoy interesado en los problemas de los demás.", "axis": -2},
    {"en": "Get chores done right away.", "ru": "Сразу выполняю домашние дела.", "es": "Hago las tareas de inmediato.", "axis": 3},
    {"en": "Am easily disturbed.", "ru": "Легко возмущаюсь.", "es": "Me molesto fácilmente.", "axis": -4},
    {"en": "Have excellent ideas.", "ru": "У меня отличные идеи.", "es": "Tengo excelentes ideas.", "axis": 5},
    {"en": "Have little to say.", "ru": "Мне мало что сказать.", "es": "Tengo poco que decir.", "axis": -1},
    {"en": "Have a soft heart.", "ru": "У меня мягкое сердце.", "es": "Tengo un corazón blando.", "axis": 2},
    {"en": "Often forget to put things back in their proper place.", "ru": "Часто забываю класть вещи на место.", "es": "A menudo olvido poner las cosas en su lugar.", "axis": -3},
    {"en": "Get upset easily.", "ru": "Легко расстраиваюсь.", "es": "Me molesto fácilmente.", "axis": -4},
    {"en": "Do not have a good imagination.", "ru": "У меня нет хорошего воображения.", "es": "No tengo buena imaginación.", "axis": -5},
    {"en": "Talk to a lot of different people at parties.", "ru": "Разговариваю с множеством людей на вечеринках.", "es": "Hablo con mucha gente en las fiestas.", "axis": 1},
    {"en": "Am not really interested in others.", "ru": "Мне не особо интересны другие.", "es": "Realmente no estoy interesado en los demás.", "axis": -2},
    {"en": "Like order.", "ru": "Люблю порядок.", "es": "Me gusta el orden.", "axis": 3},
    {"en": "Change my mood a lot.", "ru": "Часто меняю настроение.", "es": "Cambio mucho de humor.", "axis": -4},
    {"en": "Am quick to understand things.", "ru": "Быстро понимаю вещи.", "es": "Soy rápido para entender las cosas.", "axis": 5},
    {"en": "Don't like to draw attention to myself.", "ru": "Не люблю привлекать к себе внимание.", "es": "No me gusta llamar la atención sobre mí mismo.", "axis": -1},
    {"en": "Take time out for others.", "ru": "Уделяю время другим.", "es": "Dedico tiempo a los demás.", "axis": 2},
    {"en": "Shirk my duties.", "ru": "Уклоняюсь от обязанностей.", "es": "Eludo mis deberes.", "axis": -3},
    {"en": "Have frequent mood swings.", "ru": "Часто меняю настроение.", "es": "Tengo cambios de humor frecuentes.", "axis": -4},
    {"en": "Use difficult words.", "ru": "Использую сложные слова.", "es": "Uso palabras difíciles.", "axis": 5},
    {"en": "Don't mind being the center of attention.", "ru": "Не против быть в центре внимания.", "es": "No me importa ser el centro de atención.", "axis": 1},
    {"en": "Feel others' emotions.", "ru": "Чувствую эмоции других.", "es": "Siento las emociones de los demás.", "axis": 2},
    {"en": "Follow a schedule.", "ru": "Следую расписанию.", "es": "Sigo un horario.", "axis": 3},
    {"en": "Get irritated easily.", "ru": "Легко раздражаюсь.", "es": "Me irrito fácilmente.", "axis": -4},
    {"en": "Spend time reflecting on things.", "ru": "Трачу время на размышления о вещах.", "es": "Dedico tiempo a reflexionar sobre las cosas.", "axis": 5},
    {"en": "Am quiet around strangers.", "ru": "Сдержан с незнакомцами.", "es": "Soy callado con los extraños.", "axis": -1},
    {"en": "Make people feel at ease.", "ru": "Заставляю людей чувствовать себя комфортно.", "es": "Hago que la gente se sienta a gusto.", "axis": 2},
    {"en": "Am exacting in my work.", "ru": "Скрупулезен в работе.", "es": "Soy exigente en mi trabajo.", "axis": 3},
    {"en": "Often feel blue.", "ru": "Часто грущу.", "es": "A menudo me siento triste.", "axis": -4},
    {"en": "Am full of ideas.", "ru": "Полон идей.", "es": "Estoy lleno de ideas.", "axis": 5}
]


translations = {
    "en": {
        "title": "How Accurately Can You Describe Yourself?",
        "instructions": "Describe yourself as you generally are now, not as you wish to be in the future. Describe yourself as you honestly see yourself, in relation to other people you know of the same sex as you are, and roughly your same age. So that you can describe yourself in an honest manner, your responses will be kept in absolute confidence. Indicate for each statement whether it is:",
        "options": ["Very Inaccurate", "Moderately Inaccurate", "Neither Accurate Nor Inaccurate", "Moderately Accurate", "Very Accurate"]
    },
    "ru": {
        "title": "Насколько точно вы можете описать себя?",
        "instructions": "Описывайте себя так, как вы есть сейчас, а не так, каким вы хотите быть в будущем. Описывайте себя так, как вы честно видите себя в отношении других людей того же пола, что и вы, и примерно того же возраста. Чтобы вы могли честно описать себя, ваши ответы будут храниться в строгой конфиденциальности. Укажите для каждого утверждения, насколько оно соответствует вашему описанию:",
        "options": ["Совершенно неверно", "Умеренно неверно", "Ни верно, ни неверно", "Умеренно верно", "Совершенно верно"]
    },
    "es": {
        "title": "¿Qué tan exactamente puedes describirte a ti mismo?",
        "instructions": "Descríbete tal como eres ahora, no como desearías ser en el futuro. Descríbete tal como te ves honestamente, en relación con otras personas que conoces del mismo sexo que tú y aproximadamente de tu misma edad. Para que puedas describirte de manera honesta, tus respuestas se mantendrán en absoluta confidencialidad. Indica para cada declaración si es:",
        "options": ["Muy inexacto", "Moderadamente inexacto", "Ni exacto ni inexacto", "Moderadamente exacto", "Muy exacto"]
    }
}

axes = {
    1: "Extraversion",
    2: "Agreeableness",
    3: "Conscientiousness",
    4: "Emotional Stability",
    5: "Intellect/Imagination"
}

@app.context_processor
def utility_processor():
    def get_translations():
        return translations
    return dict(get_translations=get_translations)

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('start'))

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        email = request.form['email']
        language = request.form['language']
        session['email'] = email
        session['language'] = language
        session['progress'] = 0
        session['question_number'] = 1
        session['scores'] = {axis: 0 for axis in axes.values()}  # Initialize scores for each axis

        return redirect(url_for('survey'))

    return render_template('index.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if 'question_number' not in session:
        return redirect(url_for('start'))

    question_number = session['question_number']

    if request.method == 'POST':
        if 'response' in request.form:
            answer = int(request.form['response'])
            question = questions[question_number - 1]
            question_text = question[session['language']]
            axis_key = question['axis']

            axis = axes[abs(axis_key)]
            answer_value = answer if axis_key > 0 else 6 - answer

            # Update the progress and score
            session['progress'] = question_number / len(questions)
            session['scores'][axis] += answer_value  # Update the score for the specific axis

            # Prepare row data
            row = {
                "timestamp": datetime.utcnow().isoformat(),
                "email": session['email'],
                "language": session['language'],
                "question_number": question_number,
                "progress": session['progress'],
                "axis": axis,
                "answer": answer_value
            }

            # Update the row in BigQuery
            errors = client.insert_rows_json(table_id_full, [row])
            if errors:
                print(f"Encountered errors while inserting rows: {errors}")

            # Move to the next question
            session['question_number'] += 1
            if session['question_number'] > len(questions):
                return redirect(url_for('thank_you'))
        else:
            return redirect(url_for('survey'))

    if 'language' not in session or session['language'] not in translations:
        session['language'] = 'en'  # Default language

    question_number = session['question_number']
    question = questions[question_number - 1]
    question_text = question[session['language']]
    language = session['language']
    translation = translations[language]

    return render_template('survey.html', 
                            question_number=question_number, 
                            question_text=question_text, 
                            translation=translation,
                            total_questions=len(questions))

@app.route('/thank_you', methods=['GET'])
def thank_you():
    return render_template('thank_you.html')

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    email = session.get('email')
    language = session.get('language')
    question_number = session.get('question_number', 1)
    answer = request.form.get('answer')
    progress = request.form.get('progress')
    
    # Получаем текущий вопрос и его параметры
    question_text, axis_info = questions[question_number - 1]
    axis = abs(axis_info)
    key_type = "+" if axis_info > 0 else "-"
    
    # Рассчитываем балл
    score = calculate_score(answer, key_type)
    
    # Сохраняем результаты в BigQuery
    rows_to_insert = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "email": email,
            "language": language,
            "question_number": question_number,
            "progress": float(progress),
            "axis": axis,
            "answer": score
        }
    ]
    
    errors = client.insert_rows_json(table_id_full, rows_to_insert)
    if errors == []:
        print(f"New rows have been added for question {question_number}")
    else:
        print(f"Encountered errors: {errors}")
    
    # Обновляем номер вопроса в сессии
    session['question_number'] = question_number + 1
    
    # Перенаправляем на следующий вопрос или на страницу завершения
    if question_number < len(questions):
        return redirect(url_for('survey_question'))
    else:
        return redirect(url_for('survey_complete'))

@app.route('/survey_question')
def survey_question():
    question_number = session.get('question_number', 1)
    question_text, axis_info = questions[question_number - 1]
    return render_template('survey_question.html', question_text=question_text, question_number=question_number)

@app.route('/survey_complete')
def survey_complete():
    return render_template('survey_complete.html')

def calculate_score(answer, key_type):
    score_mapping = {
        "Very Inaccurate": 1,
        "Moderately Inaccurate": 2,
        "Neither Accurate Nor Inaccurate": 3,
        "Moderately Accurate": 4,
        "Very Accurate": 5
    }
    score = score_mapping[answer]
    if key_type == "-":
        score = 6 - score  # Инвертируем значение для -keyed items
    return score

if __name__ == '__main__':
    app.run(debug=True)
