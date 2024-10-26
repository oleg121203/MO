import aiosqlite
import asyncio
import logging
from typing import Optional, Any, List, Tuple

class DatabaseModule:
    def __init__(self, config: dict):
        """
        Инициализирует модуль базы данных с заданной конфигурацией.

        :param config: Словарь конфигурации, содержащий путь к базе данных.
        """
        self.db_path: str = config.get('path', 'app_database.db')
        self.lock: asyncio.Lock = asyncio.Lock()
        logging.debug(f"DatabaseModule initialized with DB path: {self.db_path}")

    async def connect(self) -> Optional[aiosqlite.Connection]:
        """
        Устанавливает асинхронное соединение с базой данных.

        :return: Объект соединения или None в случае ошибки.
        """
        try:
            connection: aiosqlite.Connection = await aiosqlite.connect(self.db_path)
            await connection.execute('PRAGMA journal_mode = WAL;')
            await connection.commit()
            logging.info("Asynchronous connection to the database established.")
            return connection
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            return None

    async def initialize(self) -> bool:
        """
        Инициализирует базу данных, создавая необходимые таблицы.

        :return: True, если инициализация успешна, иначе False.
        """
        connection = await self.connect()
        if not connection:
            logging.error("Database initialization failed due to connection error.")
            return False

        try:
            # Создание таблицы 'groups' с необходимыми полями
            await self.execute_query(
                connection,
                """
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    username TEXT,
                    date TEXT,
                    participants_count INTEGER,
                    description TEXT,
                    restricted BOOLEAN,
                    verified BOOLEAN,
                    megagroup BOOLEAN,
                    gigagroup BOOLEAN,
                    scam BOOLEAN
                );
                """
            )
            # Создание таблицы 'accounts' с необходимыми полями
            await self.execute_query(
                connection,
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    phone TEXT,
                    status TEXT,
                    bot BOOLEAN,
                    verified BOOLEAN,
                    restricted BOOLEAN,
                    scam BOOLEAN,
                    fake BOOLEAN,
                    access_hash TEXT,
                    last_online TEXT
                );
                """
            )
            # Создание таблицы связи 'group_user'
            await self.execute_query(
                connection,
                """
                CREATE TABLE IF NOT EXISTS group_user (
                    group_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (group_id, user_id),
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    FOREIGN KEY (user_id) REFERENCES accounts(id)
                );
                """
            )

            logging.info("Database tables initialized successfully.")
            return True
        except Exception as e:
            logging.error(f"Error during database initialization: {e}")
            return False
        finally:
            await self.disconnect(connection)

    async def execute_query(self, connection: aiosqlite.Connection, query: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
        """
        Выполняет асинхронный SQL-запрос с параметрами.

        :param connection: Объект соединения с базой данных.
        :param query: SQL-запрос.
        :param params: Кортеж параметров для запроса.
        :return: Результат запроса.
        """
        async with self.lock:
            try:
                async with connection.execute(query, params) as cursor:
                    result = await cursor.fetchall()
                    await connection.commit()
                    logging.debug(f"Executed query: {query} with params {params}")
                    return result
            except aiosqlite.OperationalError as e:
                logging.error(f"Operational error during query execution: {e}")
                raise e
            except Exception as e:
                logging.error(f"Unexpected error during query execution: {e}")
                raise e

    async def disconnect(self, connection: aiosqlite.Connection) -> None:
        """
        Закрывает соединение с базой данных.

        :param connection: Объект соединения с базой данных.
        """
        try:
            await connection.close()
            logging.info("Asynchronous connection to the database closed.")
        except Exception as e:
            logging.error(f"Error while disconnecting from the database: {e}")

    async def is_connected(self) -> bool:
        """
        Проверяет, установлено ли соединение с базой данных.

        :return: True, если соединение установлено, иначе False.
        """
        try:
            connection = await self.connect()
            if connection:
                await self.disconnect(connection)
                logging.debug("Database connection check: Successful.")
                return True
            else:
                logging.debug("Database connection check: Failed.")
                return False
        except Exception as e:
            logging.error(f"Error while checking connection status: {e}")
            return False