# Timed Quiz Web Application

A modern, feature-rich Flask web application for timed quizzes with user management, admin dashboard, media support, and leaderboard.

---

## Features

### Branding
- All pages include a footer with the author's name (Prabesh Subedi) for consistent branding.

### User Features
- **User Registration & Login**: Secure registration and login system.
- **Profile Page**: View quiz history, best/average scores, and most missed questions.
- **Quiz Functionality**:
  - Select question categories and difficulty.
  - Timer per question with analog clock UI.
  - Media support: image, audio, and video for questions/options.
  - Feedback after each answer (correct/wrong, correct answer shown).
  - "Stop" button to end quiz early and see results.
  - No "skipped" bug for last question; all answers recorded.
- **Leaderboard**: View top scores, delete own records.
- **Delete Quiz Attempts**: Remove own quiz attempts from profile.
- **Responsive UI**: Modern design with glassmorphism, overlays, and context-aware navigation.

### Admin Features
- **Admin Login & Dashboard**: Secure admin access.
- **User Management**: View, edit, and delete users.
- **Quiz Management**: View total questions, high score achievers.
- **Recent Activity**: See 5 most recent quiz attempts (user, score, date).
- **User Search**: Search/filter users by username and view details.
- **Admin-only Sidebar**: Contextual sidebar for admin actions.

### Data Management
- All data (users, questions, leaderboard, history) is stored in JSON files and updated automatically.

---

## Project Structure

```
TIMED_QUIZ/
│
├── app.py                # Main Flask application
├── questions.json        # Quiz questions data
├── users.json            # User data
├── leaderboard.json      # Leaderboard data
├── user_history.json     # User quiz history
├── templates/            # HTML templates (Jinja2)
│   └── ...
├── static/               # Static files (CSS, JS, media)
├── env/                  # (Optional) Python virtual environment
└── .gitignore            # Git ignore rules
```

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd TIMED_QUIZ
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask werkzeug
   ```
   (Add any other dependencies you use)

4. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000/`

---

## Usage
- Register as a new user or log in as admin.
- Start a quiz, select category/difficulty, and answer questions.
- View your profile, quiz history, and leaderboard.
- Admins can manage users, view recent activity, and search users from the dashboard.

---

## Notes
- All data is stored in JSON files in the project root. Do not delete these files unless you want to reset data.
- For media uploads, ensure the `static/` directory is writable.
- To add or edit questions, use the web UI (admin access required).

---

## License
MIT License (or specify your license here) 