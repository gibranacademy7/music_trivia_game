"""
סטטיסטיקות:
הצג תפריט שממנו אפשר לבחור את הסטטיסטיקה הרצויה:
• כמה שחקנים שחקו עד כה
• מהי השאלה שענו עליה נכון הכי הרבה שחקנים )אם יש יותר מאחת אז הצג את כולם(
• מהי השאלה שענו עליה נכון הכי פחות שחקנים )אם יש יותר מאחת אז הצג את כולם(
• הצג את השחקנים בסדר יורד לפי מס' השאלות הנכונות שענו. הראשון ברשימה יהיה זה שענה
על הכי הרבה שאלות נכונות, אח"כ שני וכו'
• הצג את השחקנים בסדר יורד לפי מס' השאלות שענו. הראשון ברשימה יהיה זה שענה על הכי
הרבה שאלות, אח"כ שני וכו'
• קלוט מספר שחקן והדפס את כל השאלות שאותו השחקן ענה עליהם. הדפס את טקסט השאלה.
ואם ענה נכון או לא
• *אתגר: הצג עבור כל שאלה: טקסט השאלה, כמה ענו, כמה ענו נכון, כמה טעו
"""

import time
import psycopg2
import psycopg2.extras
from datetime import datetime
import hashlib  # For password hashing
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
        password=password,
        port=port
    )
    print("Successfully connected to the database!")
    cursor = conn.cursor()
except Exception as e:
    print(f"An error occurred: {e}")
    exit()


# Game Functions
def start_game():
    choice = input("Do you want to start a new game (1) or continue a previous game (2)? ")
    if choice == '1':
        create_new_game()
    elif choice == '2':
        continue_game()
    else:
        print("Invalid choice.")
        start_game()


def create_new_game():
    username = input("Enter your username: ")
    cursor.execute("SELECT id FROM players WHERE username = %s;", (username,))
    user = cursor.fetchone()

    if not user:
        print("User not found. Please create an account first.")
        return

    player_id = user[0]
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 20;")  # Limit to 20 questions
    questions = cursor.fetchall()

    score = 0
    for question in questions:
        print(question[2])  # question_text
        print(f"a) {question[3]}  b) {question[4]}  c) {question[5]}  d) {question[6]}")
        answer = input("Your answer (a/b/c/d): ").lower()

        # Find the selected answer ID based on the chosen answer:
        cursor.execute("""
            SELECT id FROM answers 
            WHERE question_id = %s AND answer_text = %s;
        """, (question[0], answer))
        selected_answer_id = cursor.fetchone()

        if selected_answer_id:
            selected_answer_id = selected_answer_id[0]
        else:
            print("Invalid answer selected.")
            continue

        # Check if the answer is correct:
        is_correct = answer == question[7]
        if is_correct:
            print("Correct!")
            score += 1
        else:
            print("Wrong!")

        # Save the player's answer to the database:
        cursor.execute("""
            INSERT INTO player_answers (player_id, question_id, selected_answer_id, is_correct) 
            VALUES (%s, %s, %s, %s);
        """, (player_id, question[0], selected_answer_id, is_correct))
        conn.commit()

    print(f"Game Over! Your score: {score}/20")
    display_high_scores()

    # Optionally update high scores if score > previous high
    now = datetime.now()
    cursor.execute("""
        INSERT INTO high_scores (player_id, score, at_achieved) 
        VALUES (%s, %s, %s);
    """, (player_id, score, now))
    conn.commit()


def continue_game():
    print("Continuing previous game... (Not yet implemented)")


# User registration and login
def create_user():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    confirm_password = input("Re-enter password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    cursor.execute("SELECT * FROM players WHERE username = %s OR email = %s;", (username, email))
    if cursor.fetchone():
        print("Username or email already exists.")
    else:
        # Hash the password before saving it
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO players (username, password, email) VALUES (%s, %s, %s);",
                       (username, hashed_password, email))
        conn.commit()
        print("Account created successfully.")


def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Hash the entered password for comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("SELECT * FROM players WHERE username = %s AND password = %s;", (username, hashed_password))
    user = cursor.fetchone()

    if user:
        print("Logged in successfully.")
        start_game()  # Directly start the game after successful login
    else:
        print("Username or password is incorrect.")


# Display high scores
def display_high_scores():
    cursor.execute("""
        SELECT players.username, high_scores.score, high_scores.at_achieved 
        FROM high_scores 
        JOIN players ON players.id = high_scores.player_id 
        ORDER BY high_scores.score DESC 
        LIMIT 10;
    """)
    high_scores = cursor.fetchall()

    print("Top 10 Scores:")
    for score in high_scores:
        print(f"{score[0]}: {score[1]} - {score[2]}")  # Show username, score, and the date it was achieved

    main_menu()


# Main menu
def main_menu():
    print("\nMain Menu:")
    print("1. Start a new game")
    print("2. Continue previous game")
    print("3. View statistics")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        start_game()
    elif choice == '2':
        continue_game()
    elif choice == '3':
        show_statistics_menu()
    elif choice == '4':
        print("Goodbye!")
        exit()
    else:
        print("Invalid choice. Please try again.")
        main_menu()


# Statistics Menu
def show_statistics_menu():
    print("\nStatistics Menu:")
    print("1. Total number of players who played so far")
    print("2. Question answered correctly by the most players")
    print("3. Question answered correctly by the least players")
    print("4. Players sorted by the number of correct answers")
    print("5. Players sorted by the total number of answers")
    print("6. Display questions answered by a specific player")
    print("7. Statistics for each question")
    print("8. Back to Main Menu")

    choice = input("Enter your choice: ")

    if choice == "1":
        show_total_players()
    elif choice == "2":
        show_most_answered_question()
    elif choice == "3":
        show_least_answered_question()
    elif choice == "4":
        show_players_by_correct_answers()
    elif choice == "5":
        show_players_by_total_answers()
    elif choice == "6":
        show_player_answers()
    elif choice == "7":
        show_question_statistics()
    elif choice == "8":
        main_menu()
    else:
        print("Invalid choice. Please try again.")
        show_statistics_menu()


def show_total_players():
    cursor.execute("SELECT COUNT(*) FROM players;")
    total_players = cursor.fetchone()[0]
    print(f"Total number of players: {total_players}")
    show_statistics_menu()


def show_most_answered_question():
    cursor.execute("""
        SELECT question_id, COUNT(*) AS total_answers
        FROM player_answers
        GROUP BY question_id
        ORDER BY total_answers DESC
        LIMIT 1;
    """)
    question = cursor.fetchone()
    cursor.execute("""
        SELECT question_text FROM questions WHERE id = %s;
    """, (question[0],))
    question_text = cursor.fetchone()[0]
    print(f"The question with the most answers: {question_text}")
    show_statistics_menu()


def show_least_answered_question():
    cursor.execute("""
        SELECT question_id, COUNT(*) AS total_answers
        FROM player_answers
        GROUP BY question_id
        ORDER BY total_answers ASC
        LIMIT 1;
    """)
    question = cursor.fetchone()
    cursor.execute("""
        SELECT question_text FROM questions WHERE id = %s;
    """, (question[0],))
    question_text = cursor.fetchone()[0]
    print(f"The question with the least answers: {question_text}")
    show_statistics_menu()


def show_players_by_correct_answers():
    cursor.execute("""
        SELECT players.username, COUNT(player_answers.is_correct) AS correct_answers
        FROM player_answers
        JOIN players ON player_answers.player_id = players.id
        WHERE player_answers.is_correct = TRUE
        GROUP BY players.username
        ORDER BY correct_answers DESC;
    """)
    players = cursor.fetchall()
    print("Players sorted by correct answers:")
    for player in players:
        print(f"{player[0]}: {player[1]} correct answers")
    show_statistics_menu()


def show_players_by_total_answers():
    cursor.execute("""
        SELECT players.username, COUNT(player_answers.id) AS total_answers
        FROM player_answers
        JOIN players ON player_answers.player_id = players.id
        GROUP BY players.username
        ORDER BY total_answers DESC;
    """)
    players = cursor.fetchall()
    print("Players sorted by total answers:")
    for player in players:
        print(f"{player[0]}: {player[1]} total answers")
    show_statistics_menu()


def show_player_answers():
    # Ask for the player ID or username
    username = input("Enter the username of the player: ")

    # Fetch the player ID from the database
    cursor.execute("SELECT id FROM players WHERE username = %s;", (username,))
    player = cursor.fetchone()

    if player:
        player_id = player[0]

        # Fetch all questions and the player's responses
        cursor.execute("""
            SELECT questions.question_text, 
                   player_answers.is_correct,
                   answers.answer_text
            FROM player_answers
            JOIN questions ON player_answers.question_id = questions.id
            JOIN answers ON player_answers.selected_answer_id = answers.id
            WHERE player_answers.player_id = %s;
        """, (player_id,))

        answers = cursor.fetchall()

        if answers:
            print(f"\nAnswers for {username}:")
            for answer in answers:
                correct_str = "Correct" if answer[1] else "Incorrect"
                print(f"Question: {answer[0]}")
                print(f"Answer: {answer[2]} - {correct_str}")
        else:
            print(f"{username} has not answered any questions yet.")

    else:
        print(f"No player found with the username '{username}'.")

    show_statistics_menu()  # Return to statistics menu


# Start the program by showing the main menu
main_menu()


def show_total_players():
    cursor.execute("SELECT COUNT(*) FROM players;")
    total_players = cursor.fetchone()[0]
    print(f"Total number of players: {total_players}")
    show_statistics_menu()


def show_most_answered_question():
    cursor.execute("""
        SELECT question_id, COUNT(*) AS total_answers
        FROM player_answers
        GROUP BY question_id
        ORDER BY total_answers DESC
        LIMIT 1;
    """)
    question = cursor.fetchone()
    cursor.execute("""
        SELECT question_text FROM questions WHERE id = %s;
    """, (question[0],))
    question_text = cursor.fetchone()[0]
    print(f"The question with the most answers: {question_text}")
    show_statistics_menu()


def show_least_answered_question():
    cursor.execute("""
        SELECT question_id, COUNT(*) AS total_answers
        FROM player_answers
        GROUP BY question_id
        ORDER BY total_answers ASC
        LIMIT 1;
    """)
    question = cursor.fetchone()
    cursor.execute("""
        SELECT question_text FROM questions WHERE id = %s;
    """, (question[0],))
    question_text = cursor.fetchone()[0]
    print(f"The question with the least answers: {question_text}")
    show_statistics_menu()


def show_players_by_correct_answers():
    cursor.execute("""
        SELECT players.username, COUNT(player_answers.is_correct) AS correct_answers
        FROM player_answers
        JOIN players ON player_answers.player_id = players.id
        WHERE player_answers.is_correct = TRUE
        GROUP BY players.username
        ORDER BY correct_answers DESC;
    """)
    players = cursor.fetchall()
    print("Players sorted by correct answers:")
    for player in players:
        print(f"{player[0]}: {player[1]} correct answers")
    show_statistics_menu()


def show_players_by_total_answers():
    cursor.execute("""
        SELECT players.username, COUNT(player_answers.id) AS total_answers
        FROM player_answers
        JOIN players ON player_answers.player_id = players.id
        GROUP BY players.username
        ORDER BY total_answers DESC;
    """)
    players = cursor.fetchall()
    print("Players sorted by total answers:")
    for player in players:
        print(f"{player[0]}: {player[1]} total answers")
    show_statistics_menu()


def show_question_statistics():
    cursor.execute("""
        SELECT questions.question_text, 
               COUNT(player_answers.id) AS total_answers,
               SUM(CASE WHEN player_answers.is_correct THEN 1 ELSE 0 END) AS correct_answers,
               SUM(CASE WHEN NOT player_answers.is_correct THEN 1 ELSE 0 END) AS incorrect_answers
        FROM player_answers
        JOIN questions ON player_answers.question_id = questions.id
        GROUP BY questions.id
        ORDER BY total_answers DESC;
    """)
    stats = cursor.fetchall()

    for stat in stats:
        print(f"Question: {stat[0]}")
        print(f"Total answers: {stat[1]}, Correct answers: {stat[2]}, Incorrect answers: {stat[3]}")

    show_statistics_menu()


# Start the program by showing the main menu
main_menu()



