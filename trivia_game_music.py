import time
import psycopg2
import psycopg2.extras

import matplotlib.pyplot as plt
import numpy as np

# Database connection settings:
host = 'localhost'
database = 'trivia'
user = 'postgres'
password = 'postgres'
port = "5433"

# Connect to database:
try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    );
    print("Successfully connected to database!");

    #  cursor:
    cursor = conn.cursor();

    # Execute a query
    cursor.execute("SELECT * FROM categories;");

    # Data recovery:
    rows = cursor.fetchall();
    for row in rows:
        print(row);

except Exception as e:
    print(f"An error occurred: {e}");
finally:
    if conn:
        cursor.close();
        conn.close();
        print("The database connection was closed.");

##---------------------------------------------------------

# Data for the histogram
questions = np.arange(1, 31)  # Questions from 1 to 10
answered = [9, 8, 10, 9, 7, 8, 10, 9, 8, 7]  # Number of people who answered each question
correct = [7, 6, 8, 6, 5, 6, 8, 7, 6, 5]  # Number of correct answers
wrong = [answered[i] - correct[i] for i in range(len(answered))]  # Number of wrong answers

# Create the histogram
bar_width = 0.2
r1 = np.arange(len(questions));
r2 = [x + bar_width for x in r1];
r3 = [x + bar_width for x in r2];

plt.bar(r1, answered, color='blue', width=bar_width, edgecolor='grey', label='Answered');
plt.bar(r2, correct, color='green', width=bar_width, edgecolor='grey', label='Correct');
plt.bar(r3, wrong, color='red', width=bar_width, edgecolor='grey', label='Wrong');

# Add labels and title
plt.xlabel('Questions', fontweight='bold');
plt.ylabel('Number of Responses', fontweight='bold');
plt.title('Responses to Questions 1-10: Answered, Correct, and Wrong');
plt.xticks([r + bar_width for r in range(len(questions))], questions);


# Show the legend
plt.legend();

# Display the graph
plt.tight_layout();
plt.show();

## ----------------------------------

def start_game():
    choice = input("Do you want to start a new game (1) or continue a previous game (2)? ");
    if choice == '1':
        create_new_game();
    elif choice == '2':
        continue_game();
    else:
        print("Invalid choice.");

##---------------------------------------------

####  1. Start a new game or continue a previous game:

def create_new_game():
    username = input("Enter your username: ");
    cursor.execute("SELECT id FROM players WHERE username = %s;", (username,));
    user = cursor.fetchone();

    if not user:
        print("User not found. Please create an account first.");
        return

    player_id = user[0];
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10;");
    questions = cursor.fetchall();

    score = 0
    for question in questions:
        print(question[2])  # question_text
        print(f"a) {question[3]}  b) {question[4]}  c) {question[5]}  d) {question[6]}");
        answer = input("Your answer (a/b/c/d): ");

        if answer.lower() == question[7]:  # correct_answer
            print("Correct!");
            score += 1
            is_correct = True
        else:
            print("Wrong!");
            is_correct = False

        # Save the answer to the database
        cursor.execute("INSERT INTO player_answers (player_id, question_id, selected_answer_id, is_correct) VALUES (%s, %s, %s, %s);",
                       (player_id, question[0], answer, is_correct));
        conn.commit();

    print(f"Your score: {score}/{len(questions)}");


def continue_game():
    # Logic to load a saved game
    print("Continuing previous game...");
    # Add your code here to load the game state.

def start_game():
    choice = input("Do you want to create a new account (1) or log in (2)? ");
    if choice == '1':
        create_user();
    elif choice == '2':
        login_user();
    else:
        print("Invalid choice.");

###------------------------------------------------------------------

#### 2. Create a new user:

def create_user():
    username = input("Enter username: ");
    email = input("Enter email: ")
    password = input("Enter password: ");
    confirm_password = input("Re-enter password: ");

    if password != confirm_password:
        print("Passwords do not match.");
        return

    # Check if username and email are unique
    cursor.execute("SELECT * FROM players WHERE username = %s OR email = %s;", (username, email));
    if cursor.fetchone():
        print("Username or email already exists.");
    else:
        cursor.execute("INSERT INTO players (username, password, email) VALUES (%s, %s, %s);",
                       (username, password, email));
        conn.commit();
        print("Account created successfully.");

##--------------------------------------------------------------

#### 3. Login for an existing user

def login_user():
    username = input("Enter username: ");
    password = input("Enter password: ");

    cursor.execute("SELECT * FROM players WHERE username = %s AND password = %s;", (username, password));
    user = cursor.fetchone();

    if user:
        print("Logged in successfully.");
        continue_game(user[0]); # Continue from where you left off
    else:
        print("Username or password is incorrect.");
##---------------------------------------------------------------------------

#### 4. Game and player statistics:

def show_statistics(player_id):
    cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s AND is_correct = TRUE;", (player_id,));
    correct_answers = cursor.fetchone()[0];

    cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s;", (player_id,));
    total_answers = cursor.fetchone()[0];

    print(f"Number of correct answers: {correct_answers}");
    print(f"Total number of questions answered: {total_answers}");
##-----------------------------------------------------------------------

#### 5. High score leaderboard:

def show_high_scores():
    cursor.execute(
        "SELECT players.username, high_scores.score FROM high_scores JOIN players ON players.id = high_scores.player_id ORDER BY high_scores.score DESC LIMIT 10;")
    high_scores = cursor.fetchall();

    print("Top 10 Scores:");
    for score in high_scores:
        print(f"{score[0]}: {score[1]}");
##--------------------------------------------------------------




