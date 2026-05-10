from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
import PyPDF2

app = Flask(__name__)

app.secret_key = "ai_project"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- USER TABLE ---------------- #

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))


# ---------------- SKILLS ---------------- #

skills_list = [

    "python",
    "html",
    "css",
    "javascript",
    "flask",
    "java",
    "machine learning",
    "ai",
    "react",
    "node",
    "django"
]

# ---------------- QUESTIONS ---------------- #

questions_data = {

    "python": [
        "What is Python?",
        "Difference between list and tuple?",
        "Explain decorators."
    ],

    "html": [
        "What is semantic HTML?",
        "Difference between div and span?"
    ],

    "css": [
        "What is Flexbox?",
        "What is CSS Grid?"
    ],

    "javascript": [
        "What is DOM?",
        "Difference between let var and const?"
    ],

    "flask": [
        "What is Flask?",
        "Explain routing in Flask."
    ],

    "machine learning": [
        "What is supervised learning?",
        "What is overfitting?"
    ]
}

# ---------------- HOME ---------------- #

@app.route('/')
def home():

    return render_template('index.html')


# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session['user'] = user.name

            return redirect('/dashboard')

    return render_template('login.html')


# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():

    if 'user' in session:

        return render_template(
            'dashboard.html',
            user=session['user'],
            skills=session.get('skills', []),
            score=session.get('score', 0),
            feedback=session.get('feedback', [])
        )

    return redirect('/login')


# ---------------- UPLOAD RESUME ---------------- #

@app.route('/upload_resume', methods=['POST'])
def upload_resume():

    if 'user' not in session:
        return redirect('/login')

    file = request.files['resume']

    # ONLY PDF
    if not file.filename.endswith('.pdf'):
        return "Please upload PDF file only"

    # UPLOAD FOLDER
    upload_folder = os.path.join(
        app.root_path,
        'static',
        'uploads'
    )

    # CREATE FOLDER
    os.makedirs(upload_folder, exist_ok=True)

    # SAVE FILE
    filepath = os.path.join(
        upload_folder,
        file.filename
    )

    file.save(filepath)

    # READ PDF
    text = ""

    with open(filepath, 'rb') as pdf_file:

        reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

    text = text.lower()

    # SKILL EXTRACTION
    extracted_skills = []

    for skill in skills_list:

        if skill in text:

            extracted_skills.append(skill)

    # STORE SKILLS
    session['skills'] = extracted_skills

    # ---------------- ATS SCORE ---------------- #

    score = 0

    feedback = []

    # Skill Count
    score += len(extracted_skills) * 10

    # AI Skills
    if "machine learning" in extracted_skills:

        score += 15

        feedback.append(
            "Good Machine Learning knowledge"
        )

    if "ai" in extracted_skills:

        score += 15

        feedback.append(
            "AI skills detected"
        )

    # Frontend
    if "html" in extracted_skills and "css" in extracted_skills:

        score += 10

        feedback.append(
            "Strong frontend foundation"
        )

    # Python
    if "python" in extracted_skills:

        score += 10

        feedback.append(
            "Python skill detected"
        )

    # LIMIT
    if score > 100:
        score = 100

    # Suggestions
    if score < 50:

        feedback.append(
            "Add more technical skills"
        )

    if "flask" not in extracted_skills:

        feedback.append(
            "Try adding Flask projects"
        )

    # STORE
    session['score'] = score
    session['feedback'] = feedback

    return render_template(
        'dashboard.html',
        user=session['user'],
        skills=extracted_skills,
        score=score,
        feedback=feedback
    )


# ---------------- GENERATE QUESTIONS ---------------- #

@app.route('/generate_questions')
def generate_questions():

    if 'user' not in session:
        return redirect('/login')

    skills = session.get('skills', [])

    questions = []

    for skill in skills:

        if skill in questions_data:

            questions.extend(
                questions_data[skill]
            )

    # HR QUESTIONS
    hr_questions = [

        "Tell me about yourself",

        "Why should we hire you?",

        "What are your strengths?",

        "Describe a project you worked on"
    ]

    questions.extend(hr_questions)

    return render_template(
        'interview.html',
        questions=questions
    )


# ---------------- VOICE INTERVIEW ---------------- #

@app.route('/voice_interview')
def voice_interview():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'voice_interview.html'
    )
# ---------------- AI ANSWER EVALUATION ---------------- #

@app.route('/evaluate_answer', methods=['GET', 'POST'])
def evaluate_answer():

    if 'user' not in session:
        return redirect('/login')

    result = None

    if request.method == 'POST':

        answer = request.form['answer']

        communication = 5
        technical = 5
        confidence = 5

        feedback = []

        answer_lower = answer.lower()

        # LENGTH CHECK
        if len(answer.split()) > 20:

            communication += 2

            feedback.append(
                "Good detailed explanation"
            )

        else:

            feedback.append(
                "Try giving longer answers"
            )

        # TECHNICAL WORDS
        technical_words = [
            "python",
            "flask",
            "database",
            "algorithm",
            "api",
            "machine learning"
        ]

        for word in technical_words:

            if word in answer_lower:

                technical += 1

        # CONFIDENCE WORDS
        confidence_words = [
            "confident",
            "implemented",
            "developed",
            "created",
            "designed"
        ]

        for word in confidence_words:

            if word in answer_lower:

                confidence += 1

        # LIMIT SCORES
        communication = min(10, communication)
        technical = min(10, technical)
        confidence = min(10, confidence)

        result = {
            "communication": communication,
            "technical": technical,
            "confidence": confidence,
            "feedback": feedback
        }

    return render_template(
        'evaluate.html',
        result=result
    )

# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# ---------------- CREATE DATABASE ---------------- #

with app.app_context():
    db.create_all()


# ---------------- RUN ---------------- #

if __name__ == '__main__':

    app.run(debug=True)