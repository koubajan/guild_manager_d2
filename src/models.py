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

        # Safety: rollback any stuck transaction (doesn't work without it idk why)
        try:
            conn.rollback()
        except:
            pass

        # Transaction start
        conn.start_transaction()
        try:
            cursor = conn.cursor()

            # 1. Create hero with custom Level and Gold
            sql = "INSERT INTO heroes (name, class_id, gold_balance, level) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, class_id, float(gold), int(level)))
            hero_id = cursor.lastrowid

            # 2. Find starter item
            cursor.execute("SELECT id FROM items LIMIT 1")
            item = cursor.fetchone()

            if item:
                # 3. Add to inventory
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
        # Updates specific hero stats
        sql = "UPDATE heroes SET level = %s, gold_balance = %s WHERE id = %s"
        Database.execute_query(sql, (int(new_level), float(new_gold), hero_id))

    @staticmethod
    def delete_hero(hero_id):
        # Deletes hero (Inventory is removed automatically via CASCADE in DB)
        sql = "DELETE FROM heroes WHERE id = %s"
        Database.execute_query(sql, (hero_id,))

    @staticmethod
    def get_report():
        # Aggregates data for the report
        sql = """
            SELECT h.name, h.level, COUNT(inv.id) as item_count, SUM(i.value) as total_value
            FROM heroes h
            LEFT JOIN inventory inv ON h.id = inv.hero_id
            LEFT JOIN items i ON inv.item_id = i.id
            GROUP BY h.id
        """
        return Database.execute_query(sql)

    @staticmethod
    def import_items_from_json(json_data):
        # Imports items from JSON string
        import json
        items_list = json.loads(json_data)
        count = 0
        for i_data in items_list:
            item = Item(name=i_data['name'], rarity=i_data['rarity'], value=i_data['value'])
            item.save()
            count += 1
        return count