from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from functools import wraps
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

USERS_FILE = 'users.json'
QUESTIONS_FILE = 'questions.json'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

HISTORY_FILE = 'user_history.json'
LEADERBOARD_FILE = 'leaderboard.json'

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4', 'webm', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_questions():
    with open(QUESTIONS_FILE, 'r') as f:
        return json.load(f)

def save_questions(questions):
    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(questions, f, indent=2)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump({}, f)
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump([], f)
    with open(LEADERBOARD_FILE, 'r') as f:
        return json.load(f)

def save_leaderboard(lb):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(lb, f, indent=2)

QUESTIONS = load_questions()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to add questions.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin login required.')
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.')
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out.')
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    users = load_users()
    # Load questions and leaderboard
    questions = load_questions()
    total_questions = len(questions)
    leaderboard = load_leaderboard()
    # Find the highest score(s)
    high_score_achievers = []
    if leaderboard:
        max_score = max(entry['score'] for entry in leaderboard)
        high_score_achievers = [entry for entry in leaderboard if entry['score'] == max_score]
    return render_template('admin_dashboard.html', users=users, total_questions=total_questions, high_score_achievers=high_score_achievers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Please fill in all fields.')
            return render_template('register.html')
        users = load_users()
        if username in users:
            flash('Username already exists.')
            return render_template('register.html')
        users[username] = password
        save_users(users)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    history = load_history().get(username, [])
    best = max([h['score'] for h in history], default=0)
    return render_template('dashboard.html', username=username, best=best)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        users = load_users()
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('home'))

@app.route('/')
def home():
    global QUESTIONS
    QUESTIONS = load_questions()
    session.pop('logged_in', None)  # Optional: log out on home
    session.clear()
    return render_template('quiz.html', question=QUESTIONS[0], qnum=1, total=len(QUESTIONS), score=0, time_per_q=10)

@app.route('/start', methods=['GET', 'POST'])
def start_quiz():
    QUESTIONS = load_questions()
    # Get unique categories and difficulties
    categories = sorted(set(q.get('category', 'General') for q in QUESTIONS))
    difficulties = sorted(set(q.get('difficulty', 'Easy') for q in QUESTIONS))
    if request.method == 'POST':
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')
        timer = int(request.form.get('timer', 10))
        # Filter questions
        quiz_questions = [q for q in QUESTIONS if q.get('category', 'General') == category and q.get('difficulty', 'Easy') == difficulty]
        if not quiz_questions:
            flash('No questions found for that category/difficulty.')
            return render_template('start.html', categories=categories, difficulties=difficulties)
        session['quiz_questions'] = quiz_questions
        session['quiz_timer'] = timer
        session['user_answers'] = []
        return redirect(url_for('quiz', qnum=1, score=0))
    return render_template('start.html', categories=categories, difficulties=difficulties)

@app.route('/quiz/<int:qnum>/<int:score>', methods=['GET'])
def quiz(qnum, score):
    quiz_questions = session.get('quiz_questions')
    timer = session.get('quiz_timer', 10)
    if not quiz_questions or qnum > len(quiz_questions):
        return redirect(url_for('result'))
    question = quiz_questions[qnum-1]
    total = len(quiz_questions)
    return render_template('quiz.html', question=question, qnum=qnum, total=total, score=score, time_per_q=timer)

@app.route('/answer', methods=['POST'])
def answer():
    quiz_questions = session.get('quiz_questions')
    if not quiz_questions:
        quiz_questions = load_questions()
    qnum = int(request.form['qnum'])
    selected = request.form.get('option')
    score = int(request.form['score'])
    user_answers = session.get('user_answers', [])
    # Always append the answer
    if not selected:
        user_answers.append('Skipped')
    else:
        user_answers.append(selected)
        if selected == quiz_questions[qnum-1]['answer']:
            score += 1
    session['user_answers'] = user_answers
    # Now check if quiz is finished
    if qnum >= len(quiz_questions):
        return redirect(url_for('result'))
    # Show feedback page before next question
    return render_template('feedback.html',
        question=quiz_questions[qnum-1],
        selected=selected,
        correct=quiz_questions[qnum-1]['answer'],
        feedback=('skipped' if not selected else ('correct' if selected == quiz_questions[qnum-1]['answer'] else 'wrong')),
        next_qnum=qnum+1,
        score=score,
        total=len(quiz_questions)
    )

@app.route('/next/<int:qnum>/<int:score>', methods=['POST'])
def next_question(qnum, score):
    global QUESTIONS
    QUESTIONS = load_questions()
    return render_template('quiz.html', question=QUESTIONS[qnum-1], qnum=qnum, total=len(QUESTIONS), score=score, time_per_q=10)

@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    history = load_history().get(username, [])
    if not history:
        stats = None
    else:
        scores = [h['score'] for h in history]
        best = max(scores)
        avg = round(sum(scores)/len(scores), 2)
        # Most missed questions
        missed = {}
        for h in history:
            for i, ans in enumerate(h['user_answers']):
                if ans != h['questions'][i]['answer']:
                    qtext = h['questions'][i]['question']
                    missed[qtext] = missed.get(qtext, 0) + 1
        most_missed = sorted(missed.items(), key=lambda x: -x[1])[:3]
        stats = {
            'best': best,
            'avg': avg,
            'most_missed': most_missed
        }
    return render_template('profile.html', history=history, stats=stats)

# Save history after quiz completion (result or stop)
@app.route('/result')
def result():
    quiz_questions = session.get('quiz_questions')
    if not quiz_questions:
        quiz_questions = load_questions()
    user_answers = session.get('user_answers', [])
    # Fill unanswered questions with 'Not attempted' if any
    while len(user_answers) < len(quiz_questions):
        user_answers.append('Not attempted')
    score = sum(1 for i, q in enumerate(quiz_questions) if i < len(user_answers) and user_answers[i] == q['answer'])
    # Save to history if logged in
    if session.get('logged_in') and session.get('username'):
        history = load_history()
        user_hist = history.get(session['username'], [])
        user_hist.append({
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': score,
            'user_answers': user_answers,
            'questions': quiz_questions
        })
        history[session['username']] = user_hist
        save_history(history)
        # Save to leaderboard
        lb = load_leaderboard()
        lb.append({
            'username': session['username'],
            'score': score,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_leaderboard(lb)
    return render_template('result.html', questions=quiz_questions, user_answers=user_answers, score=score)

@app.route('/stop', methods=['POST'])
def stop():
    global QUESTIONS
    QUESTIONS = load_questions()
    user_answers = session.get('user_answers', [])
    # Fill unanswered questions with 'Not attempted'
    while len(user_answers) < len(QUESTIONS):
        user_answers.append('Not attempted')
    score = sum(1 for i, q in enumerate(QUESTIONS) if i < len(user_answers) and user_answers[i] == q['answer'])
    # Save to history if logged in
    if session.get('logged_in') and session.get('username'):
        history = load_history()
        user_hist = history.get(session['username'], [])
        user_hist.append({
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': score,
            'user_answers': user_answers,
            'questions': QUESTIONS
        })
        history[session['username']] = user_hist
        save_history(history)
        # Save to leaderboard
        lb = load_leaderboard()
        lb.append({
            'username': session['username'],
            'score': score,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_leaderboard(lb)
    return render_template('result.html', questions=QUESTIONS, user_answers=user_answers, score=score)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        optionA = request.form.get('optionA', '').strip()
        optionB = request.form.get('optionB', '').strip()
        optionC = request.form.get('optionC', '').strip()
        optionD = request.form.get('optionD', '').strip()
        answer = request.form.get('answer', '').strip().upper()
        # Handle file uploads
        q_image = request.files.get('q_image')
        q_audio = request.files.get('q_audio')
        q_video = request.files.get('q_video')
        optA_img = request.files.get('optA_img')
        optB_img = request.files.get('optB_img')
        optC_img = request.files.get('optC_img')
        optD_img = request.files.get('optD_img')
        q_image_url = q_audio_url = q_video_url = None
        optA_img_url = optB_img_url = optC_img_url = optD_img_url = None
        def save_file(file):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                return '/' + path.replace('\\', '/')
            return None
        q_image_url = save_file(q_image)
        q_audio_url = save_file(q_audio)
        q_video_url = save_file(q_video)
        optA_img_url = save_file(optA_img)
        optB_img_url = save_file(optB_img)
        optC_img_url = save_file(optC_img)
        optD_img_url = save_file(optD_img)
        if not (question and optionA and optionB and optionC and optionD and answer in ['A','B','C','D']):
            flash('Please fill all fields and select a valid answer (A/B/C/D).')
            return render_template('add_question.html')
        options = []
        for idx, opt, img_url in zip(['A','B','C','D'], [optionA, optionB, optionC, optionD], [optA_img_url, optB_img_url, optC_img_url, optD_img_url]):
            opt_dict = {'text': f"{idx}. {opt}"}
            if img_url:
                opt_dict['image'] = img_url
            options.append(opt_dict)
        new_q = {
            'question': question,
            'options': options,
            'answer': answer
        }
        if q_image_url:
            new_q['image'] = q_image_url
        if q_audio_url:
            new_q['audio'] = q_audio_url
        if q_video_url:
            new_q['video'] = q_video_url
        questions = load_questions()
        questions.append(new_q)
        save_questions(questions)
        flash('Question added successfully!')
        return redirect(url_for('add_question'))
    return render_template('add_question.html')

@app.route('/admin_edit_user/<username>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(username):
    users = load_users()
    if username not in users:
        flash('User not found.')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        if not new_password:
            flash('Password cannot be empty.')
            return redirect(url_for('admin_edit_user', username=username))
        users[username] = new_password
        save_users(users)
        flash(f'Password for {username} updated.')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_user.html', username=username)

@app.route('/admin_delete_user/<username>', methods=['POST'])
@admin_required
def admin_delete_user(username):
    users = load_users()
    if username not in users:
        flash('User not found.')
    else:
        users.pop(username)
        save_users(users)
        flash(f'User {username} deleted.')
    return redirect(url_for('admin_dashboard'))

@app.route('/leaderboard')
def leaderboard():
    lb = load_leaderboard()
    # Sort by score descending, then date descending
    lb_sorted = sorted(lb, key=lambda x: (-x['score'], x['date']), reverse=False)[:20]
    return render_template('leaderboard.html', leaderboard=lb_sorted)

@app.route('/delete_leaderboard/<int:idx>', methods=['POST'])
@login_required
def delete_leaderboard(idx):
    lb = load_leaderboard()
    username = session.get('username')
    # Only allow deletion if the entry belongs to the current user
    if 0 <= idx < len(lb) and lb[idx]['username'] == username:
        lb.pop(idx)
        save_leaderboard(lb)
        flash('Leaderboard record deleted.')
    else:
        flash('You can only delete your own records.')
    return redirect(url_for('leaderboard'))

@app.route('/delete_history/<int:index>', methods=['POST'])
@login_required
def delete_history(index):
    username = session.get('username')
    history = load_history()
    user_hist = history.get(username, [])
    # The index from the form is in reverse order (latest first)
    if 0 <= index < len(user_hist):
        user_hist.pop(index)
        history[username] = user_hist
        save_history(history)
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True) 