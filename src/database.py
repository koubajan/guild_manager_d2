import mysql.connector
import json
import os


class Database:
    _instance = None

    @staticmethod
    def get_connection():
        if Database._instance is None:
            # Finds path to root folder (one level up from src)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'config.json')

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Missing 'config.json' in root: {base_dir}")

            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                Database._instance = mysql.connector.connect(**config)
            except Exception as e:
                raise ConnectionError(f"Connection error: {e}")

        # Reconnect if connection was lost
        if not Database._instance.is_connected():
            Database._instance.reconnect(attempts=3, delay=0)

        return Database._instance

    @staticmethod
    def execute_query(query, params=None):
        conn = Database.get_connection()
        # Returns data as dictionary
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid  # Returns ID of the new row
        except Exception as e:
            conn.rollback()  # Revert changes on error
            raise e
        finally:
            cursor.close()