"""
*בונוס/רשות גרפים
• קלוט מספר שחקן והצג פאי עוגה המראה על כמה שאלות )מתוך 20(: לא ענה בכלל? כמה ענה
נכון? וכמה ענה לא נכון?

"""


import psycopg2
import matplotlib.pyplot as plt
import numpy as np

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

# Function to display the pie chart for a given player
def display_player_pie_chart(conn, player_id):
    cursor = conn.cursor()

    # Query to get the total number of questions (assuming 20 questions)
    total_questions = 20

    # Query to get the number of answered, correct, and wrong answers for the player
    cursor.execute("""
        SELECT
            COUNT(*) FILTER (WHERE pa.is_correct = TRUE) AS correct,
            COUNT(*) FILTER (WHERE pa.is_correct = FALSE) AS wrong,
            COUNT(*) FILTER (WHERE pa.selected_answer_id IS NULL) AS not_answered
        FROM player_answers pa
        WHERE pa.player_id = %s;
    """, (player_id,))

    result = cursor.fetchone()
    correct_answers = result[0]
    wrong_answers = result[1]
    not_answered = total_questions - (correct_answers + wrong_answers)  # remaining unanswered

    # Data for the pie chart
    labels = ['Correct', 'Wrong', 'Not Answered']
    sizes = [correct_answers, wrong_answers, not_answered]
    colors = ['yellowgreen', 'red', 'gold']
    explode = (0.1, 0, 0)  # explode the "Correct" slice slightly

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)

    # Equal aspect ratio ensures that the pie chart is drawn as a circle.
    ax.axis('equal')

    # Add a headline
    ax.set_title(f"Player {player_id} - Answer Distribution")

    # Show the plot
    plt.show()

# Function to prompt user for player ID and display the pie chart
def prompt_player_and_show_pie_chart(conn):
    player_id = input("Enter player ID to view answer distribution pie chart: ")
    try:
        player_id = int(player_id)
        display_player_pie_chart(conn, player_id)
    except ValueError:
        print("Invalid player ID. Please enter a numeric value.")

# Main function to run the program
if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        prompt_player_and_show_pie_chart(conn)
        conn.close()
