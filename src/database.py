import mysql.connector
import json
import os


class Database:
    _instance = None

    @staticmethod
    def get_connection():
        if Database._instance is None:
            # Najde cestu k root slozce (o uroven vys nez tento skript)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'config.json')

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Chybi 'config.json' v root slozce: {base_dir}")

            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                Database._instance = mysql.connector.connect(**config)
            except Exception as e:
                raise ConnectionError(f"Chyba pripojeni: {e}")

        # Reconnect, pokud spojeni spadlo
        if not Database._instance.is_connected():
            Database._instance.reconnect(attempts=3, delay=0)

        return Database._instance

    @staticmethod
    def execute_query(query, params=None):
        conn = Database.get_connection()
        # Vrati data jako slovnik
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid  # Vrati ID noveho radku
        except Exception as e:
            conn.rollback()  # Vrati zmeny zpet pri chybe
            raise e
        finally:
            cursor.close()