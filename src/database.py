import mysql.connector
import json
import os


class Database:
    _instance = None

    @staticmethod
    def get_connection():
        if Database._instance is None:
            # 1. Find config file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'config.json')

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Missing 'config.json' in: {base_dir}")

            # 2. Load and VALIDATE config
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)

                # Check for required keys
                required_keys = ["host", "user", "password", "database"]
                for key in required_keys:
                    if key not in config:
                        raise ValueError(f"Config is missing required key: '{key}'")

                Database._instance = mysql.connector.connect(**config)

            except json.JSONDecodeError:
                raise ValueError("Config file is not valid JSON! Check for missing commas or quotes.")
            except mysql.connector.Error as err:
                # Handle specific DB errors
                if err.errno == 2003:
                    raise ConnectionError("Cannot connect to MySQL Server. Is it running?")
                elif err.errno == 1045:
                    raise ConnectionError("Wrong username or password.")
                elif err.errno == 1049:
                    raise ConnectionError(f"Database '{config.get('database')}' does not exist.")
                else:
                    raise ConnectionError(f"Database Error: {err}")
            except Exception as e:
                raise e

        # 3. Reconnect if connection dropped
        try:
            if not Database._instance.is_connected():
                Database._instance.reconnect(attempts=3, delay=0)
        except Exception:
            # If reconnect fails, clear instance so we try fresh next time
            Database._instance = None
            raise ConnectionError("Lost connection to database and cannot reconnect.")

        return Database._instance

    @staticmethod
    def execute_query(query, params=None):
        try:
            conn = Database.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
        except Exception as e:
            # If query fails, try to rollback just in case
            try:
                if Database._instance:
                    Database._instance.rollback()
            except:
                pass
            raise e