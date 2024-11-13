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


import psycopg2
from datetime import datetime

# Database connection settings:
host = 'localhost'
database = 'trivia'
user = 'postgres'
password = 'admin'
port = "5432"

# Connect to database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        print("Successfully connected to the database!")
        return conn
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Show main statistics menu
def show_statistics_menu(conn):
    while True:
        print("\nStatistics Menu:")
        print("1. Number of players who have played so far")
        print("2. Question answered correctly by the most players")
        print("3. Question answered correctly by the fewest players")
        print("4. Players sorted by most correct answers")
        print("5. Players sorted by most total answers")
        print("6. View answers of a specific player")
        print("7. Show statistics per question (answered, correct, wrong)")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            display_player_count(conn)
        elif choice == '2':
            display_most_answered_question(conn)
        elif choice == '3':
            display_least_answered_question(conn)
        elif choice == '4':
            display_players_sorted_by_correct_answers(conn)
        elif choice == '5':
            display_players_sorted_by_answers(conn)
        elif choice == '6':
            player_id = input("Enter player ID: ")
            display_player_answers(conn, player_id)
        elif choice == '7':
            display_question_statistics(conn)
        elif choice == '8':
            print("Exiting statistics menu.")
            break
        else:
            print("Invalid choice. Please try again.")

# 1. Display number of players who have played so far
def display_player_count(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_answers;")
    count = cursor.fetchone()[0]
    print(f"Number of players who have played: {count}")

# 2. Display question answered correctly by the most players
def display_most_answered_question(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.question_text, COUNT(pa.player_id) AS correct_answers
        FROM player_answers pa
        JOIN questions q ON pa.question_id = q.question_id
        WHERE pa.is_correct = TRUE
        GROUP BY q.question_text
        ORDER BY correct_answers DESC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    print(f"The question answered correctly by the most players: {result[0]} (answered correctly by {result[1]} players)")

# 3. Display question answered correctly by the fewest players
def display_least_answered_question(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.question_text, COUNT(pa.player_id) AS correct_answers
        FROM player_answers pa
        JOIN questions q ON pa.question_id = q.question_id
        WHERE pa.is_correct = TRUE
        GROUP BY q.question_text
        ORDER BY correct_answers ASC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    print(f"The question answered correctly by the fewest players: {result[0]} (answered correctly by {result[1]} players)")

# 4. Display players sorted by most correct answers
def display_players_sorted_by_correct_answers(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.username, COUNT(pa.id) AS correct_answers
        FROM player_answers pa
        JOIN players p ON pa.player_id = p.id
        WHERE pa.is_correct = TRUE
        GROUP BY p.username
        ORDER BY correct_answers DESC;
    """)
    players = cursor.fetchall()
    print("\nPlayers sorted by most correct answers:")
    for player in players:
        print(f"{player[0]}: {player[1]} correct answers")

# 5. Display players sorted by most total answers
def display_players_sorted_by_answers(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.username, COUNT(pa.id) AS total_answers
        FROM player_answers pa
        JOIN players p ON pa.player_id = p.id
        GROUP BY p.username
        ORDER BY total_answers DESC;
    """)
    players = cursor.fetchall()
    print("\nPlayers sorted by most total answers:")
    for player in players:
        print(f"{player[0]}: {player[1]} total answers")

# 6. Display answers of a specific player
def display_player_answers(conn, player_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.question_text, pa.is_correct
        FROM player_answers pa
        JOIN questions q ON pa.question_id = q.question_id
        WHERE pa.player_id = %s;
    """, (player_id,))
    answers = cursor.fetchall()
    print(f"\nAnswers for player {player_id}:")
    for answer in answers:
        result = "Correct" if answer[1] else "Wrong"
        print(f"Question: {answer[0]} - Answer: {result}")

# 7. Show statistics per question (answered, correct, wrong)
def display_question_statistics(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.question_text, 
               COUNT(pa.player_id) AS total_answers, 
               COUNT(CASE WHEN pa.is_correct THEN 1 END) AS correct_answers,
               COUNT(CASE WHEN NOT pa.is_correct THEN 1 END) AS wrong_answers
        FROM player_answers pa
        JOIN questions q ON pa.question_id = q.question_id
        GROUP BY q.question_text;
    """)
    stats = cursor.fetchall()
    print("\nStatistics per question:")
    for stat in stats:
        print(f"Question: {stat[0]} - Total Answers: {stat[1]} - Correct: {stat[2]} - Wrong: {stat[3]}")

if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        show_statistics_menu(conn)
        conn.close()
