from database import Database


class ActiveRecord:
    table = ""
    pk = "id"

    def __init__(self, **kwargs):
        # Nastavi atributy objektu podle sloupcu v DB
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        data = self.__dict__.copy()
        pk_val = data.get(self.pk)

        if pk_val:
            # UPDATE (pokud ma ID)
            set_clause = ", ".join([f"{k}=%s" for k in data.keys() if k != self.pk])
            values = list(data.values())
            values.remove(pk_val)
            values.append(pk_val)

            sql = f"UPDATE {self.table} SET {set_clause} WHERE {self.pk}=%s"
            Database.execute_query(sql, tuple(values))
        else:
            # INSERT (pokud nema ID)
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})"
            new_id = Database.execute_query(sql, tuple(data.values()))
            setattr(self, self.pk, new_id)

    @classmethod
    def all(cls):
        # Vrati vsechny zaznamy jako objekty
        sql = f"SELECT * FROM {cls.table}"
        rows = Database.execute_query(sql)
        return [cls(**row) for row in rows]