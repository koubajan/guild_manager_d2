from orm import ActiveRecord
from database import Database


class Hero(ActiveRecord):
    table = "heroes"


class Item(ActiveRecord):
    table = "items"


class GuildManager:
    @staticmethod
    def create_hero_with_starter_pack(name, class_id, level, gold):
        conn = Database.get_connection()

        try:
            conn.rollback()
        except:
            pass

        conn.start_transaction()
        try:
            cursor = conn.cursor()

            # 1. Create hero
            sql = "INSERT INTO heroes (name, class_id, gold_balance, level) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, class_id, float(gold), int(level)))
            hero_id = cursor.lastrowid

            # 2. Starter item
            cursor.execute("SELECT id FROM items LIMIT 1")
            item = cursor.fetchone()

            if item:
                cursor.execute("INSERT INTO inventory (hero_id, item_id, quantity) VALUES (%s, %s, 1)",
                               (hero_id, item[0]))

            conn.commit()
            cursor.close()
            return hero_id
        except Exception as e:
            conn.rollback()
            raise e

    @staticmethod
    def update_hero_stats(hero_id, new_level, new_gold):
        sql = "UPDATE heroes SET level = %s, gold_balance = %s WHERE id = %s"
        Database.execute_query(sql, (int(new_level), float(new_gold), hero_id))

    @staticmethod
    def delete_hero(hero_id):
        sql = "DELETE FROM heroes WHERE id = %s"
        Database.execute_query(sql, (hero_id,))

    @staticmethod
    def get_report():
        # UPDATED: Added gold_balance and renamed total_value to items_value
        sql = """
            SELECT h.name, h.level, h.gold_balance, COUNT(inv.id) as item_count, SUM(i.value) as items_value
            FROM heroes h
            LEFT JOIN inventory inv ON h.id = inv.hero_id
            LEFT JOIN items i ON inv.item_id = i.id
            GROUP BY h.id
        """
        return Database.execute_query(sql)

    @staticmethod
    def get_guild_stats():
        # Calculates summary statistics
        sql = """
            SELECT
                (SELECT IFNULL(SUM(i.value), 0) FROM inventory inv JOIN items i ON inv.item_id = i.id) as guild_item_value,
                (SELECT IFNULL(AVG(level), 0) FROM heroes) as avg_level,
                (SELECT IFNULL(AVG(gold_balance), 0) FROM heroes) as avg_gold
        """
        result = Database.execute_query(sql)
        return result[0] if result else {'guild_item_value': 0, 'avg_level': 0, 'avg_gold': 0}

    @staticmethod
    def import_items_from_json(json_data):
        import json
        items_list = json.loads(json_data)
        count = 0
        for i_data in items_list:
            item = Item(name=i_data['name'], rarity=i_data['rarity'], value=i_data['value'])
            item.save()
            count += 1
        return count