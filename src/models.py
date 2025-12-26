from orm import ActiveRecord
from database import Database


class Hero(ActiveRecord):
    table = "heroes"


class Item(ActiveRecord):
    table = "items"


class GuildManager:
    @staticmethod
    def create_hero_with_starter_pack(name, class_id):
        # TRANSAKCE: Vytvori hrdinu a da mu prvni item
        conn = Database.get_connection()
        try:
            # Pro jistotu zrusime jakoukoliv visici transakci z minula
            conn.rollback()
        except:
            pass
        conn.start_transaction()
        try:
            cursor = conn.cursor()

            # 1. Vytvor hrdinu
            cursor.execute("INSERT INTO heroes (name, class_id, gold_balance, level) VALUES (%s, %s, 100.0, 1)",
                           (name, class_id))
            hero_id = cursor.lastrowid

            # 2. Najdi startovni item
            cursor.execute("SELECT id FROM items LIMIT 1")
            item = cursor.fetchone()

            if item:
                # 3. Pridej do inventare (vazba M:N)
                cursor.execute("INSERT INTO inventory (hero_id, item_id, quantity) VALUES (%s, %s, 1)",
                               (hero_id, item[0]))

            conn.commit()  # Potvrdit zmeny
            cursor.close()
            return hero_id
        except Exception as e:
            conn.rollback()  # Zrusit pri chybe
            raise e

    @staticmethod
    def get_report():
        # Agregace dat (SUM, COUNT) pro report
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
        # Import dat z JSONu
        import json
        items_list = json.loads(json_data)
        count = 0
        for i_data in items_list:
            item = Item(name=i_data['name'], rarity=i_data['rarity'], value=i_data['value'])
            item.save()
            count += 1
        return count