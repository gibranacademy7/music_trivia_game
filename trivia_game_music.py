import time
import psycopg2
import psycopg2.extras
import matplotlib.pyplot as plt
import numpy as np

# Database connection settings:
host = 'localhost'
database = 'trivia'
user = 'postgres'
password = 'admin'
port = "5432"

# Connect to database:
try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    print("Successfully connected to database!");
    cursor = conn.cursor();
except Exception as e:
    print(f"An error occurred: {e}");
else:
    # Execute a query to retrieve categories:
    cursor.execute("SELECT * FROM categories;");
    rows = cursor.fetchall();
    for row in rows:
        print(row);

#---------------------------------------------------------
# Retrieve answer data for the chart:
cursor.execute("""
    SELECT q.question_id, 
           COUNT(pa.selected_answer_id) AS answered,
           SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS correct
    FROM questions q
    LEFT JOIN player_answers pa ON q.question_id = pa.question_id
    LEFT JOIN answers a ON pa.selected_answer_id = a.id
    GROUP BY q.question_id
    ORDER BY q.question_id;
""");
data = cursor.fetchall();

# Prepare data for the chart:
questions = [row[0] for row in data]  # IDs of questions
answered = [row[1] for row in data]   # Number of answers
correct = [row[2] for row in data]    # Number of correct answers
wrong = [answered[i] - correct[i] for i in range(len(answered))]  # Number of wrong answers

# Create bar chart:
bar_width = 0.2
r1 = np.arange(len(questions));
r2 = [x + bar_width for x in r1];
r3 = [x + bar_width for x in r2];

fig, ax = plt.subplots(figsize=(10, 6)); # Set figure size

# Bars for Answered, Correct, Wrong
bars_answered = ax.bar(r1, answered, color='dodgerblue', width=bar_width, edgecolor='grey', label='Answered');
bars_correct = ax.bar(r2, correct, color='forestgreen', width=bar_width, edgecolor='grey', label='Correct');
bars_wrong = ax.bar(r3, wrong, color='firebrick', width=bar_width, edgecolor='grey', label='Wrong');

# Add data labels on top of each bar
def add_labels(bars):
    for bar in bars:
        yval = bar.get_height();
        ax.text(bar.get_x() + bar.get_width()/2, yval + 1, round(yval, 1), ha='center', va='bottom', fontsize=10);

add_labels(bars_answered);
add_labels(bars_correct);
add_labels(bars_wrong);

# Set labels and title
ax.set_xlabel('Questions', fontweight='bold', fontsize=12);
ax.set_ylabel('Number of Responses', fontweight='bold', fontsize=12);
ax.set_title('Responses to Questions: Answered, Correct, and Wrong', fontsize=14);
ax.set_xticks([r + bar_width for r in range(len(questions))]);
ax.set_xticklabels(questions, rotation=45, ha='right', fontsize=10);

# Customize the grid and add legend
ax.grid(True, axis='y', linestyle='--', alpha=0.7);
ax.legend();

# Show the plot
plt.tight_layout();  # Adjust the plot to make it fit neatly
plt.show();

#---------------------------------------------------------
# Game Functions

def start_game():
    choice = input("Do you want to start a new game (1) or continue a previous game (2)? ");
    if choice == '1':
        create_new_game();
    elif choice == '2':
        continue_game();
    else:
        print("Invalid choice.");

def create_new_game():
    username = input("Enter your username: ");
    cursor.execute("SELECT id FROM players WHERE username = %s;", (username,));
    user = cursor.fetchone();

    if not user:
        print("User not found. Please create an account first.");
        return

    player_id = user[0]
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10;");
    questions = cursor.fetchall();

    score = 0
    for question in questions:
        print(question[2])  # question_text
        print(f"a) {question[3]}  b) {question[4]}  c) {question[5]}  d) {question[6]}");
        answer = input("Your answer (a/b/c/d): ");

        # Find the selected answer ID based on the chosen answer:
        cursor.execute("""
            SELECT id FROM answers 
            WHERE question_id = %s AND answer_text = %s;
        """, (question[0], answer.lower()));
        selected_answer_id = cursor.fetchone();

        if selected_answer_id:
            selected_answer_id = selected_answer_id[0]
        else:
            print("Invalid answer selected.");
            continue

        # Check if the answer is correct:
        is_correct = answer.lower() == question[7]
        if is_correct:
            print("Correct!");
            score += 1
        else:
            print("Wrong!");

        # Save the player's answer to the database:
        cursor.execute("""
            INSERT INTO player_answers (player_id, question_id, selected_answer_id, is_correct) 
            VALUES (%s, %s, %s, %s);
        """, (player_id, question[0], selected_answer_id, is_correct));
        conn.commit();

    print(f"Your score: {score}/{len(questions)}");

def continue_game():
    print("Continuing previous game...");
    # Logic to load a saved game (to be implemented)

# User registration and login

def create_user():
    username = input("Enter username: ");
    email = input("Enter email: ");
    password = input("Enter password: ");
    confirm_password = input("Re-enter password: ");

    if password != confirm_password:
        print("Passwords do not match.");
        return

    cursor.execute("SELECT * FROM players WHERE username = %s OR email = %s;", (username, email));
    if cursor.fetchone():
        print("Username or email already exists.");
    else:
        cursor.execute("INSERT INTO players (username, password, email) VALUES (%s, %s, %s);",
                       (username, password, email));
        conn.commit();
        print("Account created successfully.");

def login_user():
    username = input("Enter username: ");
    password = input("Enter password: ");

    cursor.execute("SELECT * FROM players WHERE username = %s AND password = %s;", (username, password));
    user = cursor.fetchone();

    if user:
        print("Logged in successfully.");
        continue_game();# Continue the game if the user is logged in
    else:
        print("Username or password is incorrect.");

# Statistics and high scores

def show_statistics(player_id):
    cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s AND is_correct = TRUE;", (player_id,));
    correct_answers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s;", (player_id,));
    total_answers = cursor.fetchone()[0]

    print(f"Number of correct answers: {correct_answers}");
    print(f"Total number of questions answered: {total_answers}");

def show_high_scores():
    cursor.execute("""
        SELECT players.username, high_scores.score 
        FROM high_scores 
        JOIN players ON players.id = high_scores.player_id 
        ORDER BY high_scores.score DESC 
        LIMIT 10;
    """);
    high_scores = cursor.fetchall();

    print("Top 10 Scores:");
    for score in high_scores:
        print(f"{score[0]}: {score[1]}");
