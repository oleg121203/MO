import aiosqlite
import asyncio

# Example class to interact with SQLite database using aiosqlite
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def initialize_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS example_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL
                )
            ''')
            await db.commit()

    async def insert_data(self, name: str, value: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO example_table (name, value)
                VALUES (?, ?)
            ''', (name, value))
            await db.commit()

    async def get_all_data(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM example_table')
            rows = await cursor.fetchall()
            return rows

# Example usage of DatabaseManager
if __name__ == "__main__":
    async def main():
        db_manager = DatabaseManager("example.db")
        await db_manager.initialize_db()
        await db_manager.insert_data("Test Name", "Test Value")
        data = await db_manager.get_all_data()
        print(data)

    asyncio.run(main())
