import unittest
from unittest.mock import MagicMock, patch
import hashlib
from datetime import datetime
import trivia_game_music  # Assuming the main game code is in a file named "game.py"


class TestTriviaGame(unittest.TestCase):

    @patch('game.psycopg2.connect')  # Mock the database connection
    def setUp(self, mock_connect):
        # Mock the database connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

    @patch('builtins.input', return_value='testuser')
    def test_create_user(self, mock_input):
        # Test user registration process
        mock_input.side_effect = ['testuser', 'testemail@example.com', 'password123', 'password123']
        trivia_game_music.create_user();

        # Check if the database queries were executed correctly
        self.mock_cursor.execute.assert_called_with("SELECT * FROM players WHERE username = %s OR email = %s;",
                                                    ('testuser', 'testemail@example.com'))
        self.mock_cursor.execute.assert_called_with(
            "INSERT INTO players (username, password, email) VALUES (%s, %s, %s);",
            ('testuser', hashlib.sha256('password123'.encode()).hexdigest(), 'testemail@example.com')
        );

    @patch('builtins.input', return_value='testuser')
    @patch('game.datetime')
    def test_create_new_game(self, mock_datetime, mock_input):
        # Simulate a new game creation
        mock_input.side_effect = ['testuser']
        mock_datetime.now.return_value = datetime(2024, 11, 24);

        # Assume the player exists and there are questions available
        self.mock_cursor.fetchone.return_value = [1]  # Simulate a player ID

        # Simulate fetching 20 questions
        self.mock_cursor.fetchall.return_value = [
            (1, 'Question 1', 'Answer 1', 'Answer 2', 'Answer 3', 'Answer 4', 'a', 'Answer 1'),
            (2, 'Question 2', 'Answer 1', 'Answer 2', 'Answer 3', 'Answer 4', 'b', 'Answer 2')
        ]

        # Simulate answering the first question correctly
        mock_input.side_effect = ['a', 'b']  # First answer correct, second wrong
        trivia_game_music.create_new_game();

        # Check if game queries (questions, answers) are executed
        self.mock_cursor.execute.assert_any_call("SELECT * FROM questions ORDER BY RANDOM() LIMIT 20;");

        # Check if the player's answers were recorded correctly
        self.mock_cursor.execute.assert_any_call(
            "INSERT INTO player_answers (player_id, question_id, selected_answer_id, is_correct) VALUES (%s, %s, %s, %s);",
            (1, 1, 1, True)
        );
        self.mock_cursor.execute.assert_any_call(
            "INSERT INTO player_answers (player_id, question_id, selected_answer_id, is_correct) VALUES (%s, %s, %s, %s);",
            (1, 2, 2, False)
        );

    @patch('builtins.input', return_value='testuser')
    def test_show_total_players(self, mock_input):
        # Test showing the total number of players
        self.mock_cursor.fetchone.return_value = [5]  # Simulate 5 players
        trivia_game_music.show_total_players();

        # Check if the correct database query was executed
        self.mock_cursor.execute.assert_called_with("SELECT COUNT(*) FROM players;");
        self.mock_cursor.fetchone.assert_called_once();

    @patch('builtins.input', return_value='testuser')
    def test_show_most_answered_question(self, mock_input):
        # Test displaying the most answered question
        self.mock_cursor.fetchone.return_value = [1, 10]  # Question ID 1, answered 10 times
        self.mock_cursor.fetchone.return_value = ['What is 2+2?']  # Question text

        trivia_game_music.show_most_answered_question();

        # Check if the correct database query was executed
        self.mock_cursor.execute.assert_called_with(
            "SELECT question_id, COUNT(*) AS total_answers FROM player_answers GROUP BY question_id ORDER BY total_answers DESC LIMIT 1;"
        );
        self.mock_cursor.execute.assert_called_with(
            "SELECT question_text FROM questions WHERE id = %s;", (1,)
        );

    @patch('builtins.input', return_value='testuser')
    def test_show_players_by_correct_answers(self, mock_input):
        # Test displaying players by correct answers
        self.mock_cursor.fetchall.return_value = [
            ('testuser', 15),
            ('anotheruser', 10)
        ]

        trivia_game_music.show_players_by_correct_answers();

        # Check if the correct database query was executed
        self.mock_cursor.execute.assert_called_with(
            "SELECT players.username, COUNT(player_answers.is_correct) AS correct_answers "
            "FROM player_answers JOIN players ON player_answers.player_id = players.id "
            "WHERE player_answers.is_correct = TRUE GROUP BY players.username ORDER BY correct_answers DESC;"
        );
        self.mock_cursor.fetchall.assert_called_once();

    @patch('builtins.input', return_value='testuser');
    def test_show_question_statistics(self, mock_input):
        # Test displaying question statistics
        self.mock_cursor.fetchall.return_value = [
            ('What is 2+2?', 20, 18, 2),  # Question with 20 answers, 18 correct, 2 incorrect
        ]

        trivia_game_music.show_question_statistics();

        # Check if the correct database query was executed
        self.mock_cursor.execute.assert_called_with(
            "SELECT questions.question_text, COUNT(player_answers.id) AS total_answers, "
            "SUM(CASE WHEN player_answers.is_correct THEN 1 ELSE 0 END) AS correct_answers, "
            "SUM(CASE WHEN NOT player_answers.is_correct THEN 1 ELSE 0 END) AS incorrect_answers "
            "FROM player_answers JOIN questions ON player_answers.question_id = questions.id "
            "GROUP BY questions.id ORDER BY total_answers DESC;"
        );
        self.mock_cursor.fetchall.assert_called_once();


if __name__ == '__main__':
    unittest.main();
