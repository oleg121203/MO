import logging
import asyncio
import traceback
from typing import Optional, Any, List, Union

from telethon import TelegramClient, errors, functions, types
from telethon.tl.functions.channels import GetFullChannelRequest

class TelegramModule:
    def __init__(self, api_id: int, api_hash: str, phone_number: str):
        """
        Инициализирует модуль Telegram с предоставленными API-учетными данными и номером телефона.

        :param api_id: Telegram API ID.
        :param api_hash: Telegram API Hash.
        :param phone_number: Номер телефона, связанный с аккаунтом Telegram.
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        logging.debug("TelegramModule initialized with provided credentials.")

    async def connect(self) -> None:
        """
        Асинхронно подключается к Telegram и выполняет авторизацию, если требуется.
        """
        try:
            if not self.client.is_connected():
                await self.client.connect()
                logging.info("Connected to Telegram.")
            else:
                logging.info("Already connected to Telegram.")

            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone_number)
                logging.info("Confirmation code sent to Telegram.")
            else:
                logging.info("User is already authorized with Telegram.")
        except errors.RPCError as e:
            logging.error(f"RPC Error while connecting to Telegram: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unknown error while connecting to Telegram: {e}")
            raise e

    async def sign_in(self, code: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Асинхронно выполняет вход в Telegram с использованием предоставленного кода и/или пароля.

        :param code: Код подтверждения, полученный от Telegram.
        :param password: Пароль для Telegram (если включена двухэтапная аутентификация).
        """
        try:
            if code and not password:
                await self.client.sign_in(self.phone_number, code)
                logging.info("Successfully signed in to Telegram with code.")
            elif password and not code:
                await self.client.sign_in(password=password)
                logging.info("Successfully signed in to Telegram with password.")
            elif code and password:
                await self.client.sign_in(self.phone_number, code, password=password)
                logging.info("Successfully signed in to Telegram with code and password.")
            else:
                logging.warning("No code or password provided for sign-in.")
        except errors.SessionPasswordNeededError:
            logging.warning("Password required for Telegram sign-in.")
            raise
        except errors.RPCError as e:
            logging.error(f"RPC Error during Telegram sign-in: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unknown error during Telegram sign-in: {e}")
            raise e

    async def disconnect(self) -> None:
        """
        Асинхронно отключается от Telegram.
        """
        try:
            if self.client.is_connected():
                await self.client.disconnect()
                logging.info("Disconnected from Telegram.")
            else:
                logging.info("Telegram client was already disconnected.")
        except Exception as e:
            logging.error(f"Error while disconnecting from Telegram: {e}")
            raise e

    async def get_entity(self, identifier: Any) -> Union[types.User, types.Chat, types.Channel]:
        """
        Асинхронно получает сущность Telegram по её идентификатору.

        :param identifier: Username, user ID или приглашение на сущность.
        :return: Объект сущности Telegram (User, Chat или Channel).
        """
        try:
            entity = await self.client.get_entity(identifier)
            logging.debug(f"Retrieved entity for identifier: {identifier}")
            return entity
        except errors.RPCError as e:
            logging.error(f"RPC Error while getting entity: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unknown error while getting entity: {e}")
            raise e

    async def get_participants(self, group: Union[types.User, types.Chat, types.Channel], aggressive: bool = True) -> List[types.User]:
        """
        Асинхронно получает участников Telegram-группы.

        :param group: Сущность Telegram-группы (User, Chat или Channel).
        :param aggressive: Использовать ли агрессивное извлечение участников (по умолчанию True).
        :return: Список участников Telegram-группы.
        """
        try:
            participants = await self.client.get_participants(group, aggressive=aggressive)
            logging.debug(f"Retrieved {len(participants)} participants from group: {group.id}")
            return participants
        except errors.RPCError as e:
            logging.error(f"RPC Error while getting participants: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unknown error while getting participants: {e}")
            raise e

    async def get_dialogs(self, user: Union[types.User, types.Chat, types.Channel]) -> List[types.Dialog]:
        """
        Асинхронно получает диалоги пользователя Telegram.

        :param user: Сущность пользователя Telegram (User, Chat или Channel).
        :return: Список диалогов Telegram.
        """
        try:
            dialogs = await self.client.get_dialogs(user)
            logging.debug(f"Retrieved {len(dialogs)} dialogs for user: {user.id}")
            return dialogs
        except errors.RPCError as e:
            logging.error(f"RPC Error while getting dialogs: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unknown error while getting dialogs: {e}")
            raise e

    async def is_connected(self) -> bool:
        """
        Проверяет, подключен ли клиент Telegram.

        :return: True, если подключен, иначе False.
        """
        try:
            return self.client.is_connected()
        except Exception as e:
            logging.error(f"Error while checking connection status: {e}")
            return False

    async def is_user_authorized(self) -> bool:
        """
        Проверяет, авторизован ли пользователь в Telegram.

        :return: True, если авторизован, иначе False.
        """
        try:
            return await self.client.is_user_authorized()
        except Exception as e:
            logging.error(f"Error while checking user authorization: {e}")
            return False

    async def send_code_request(self) -> None:
        """
        Асинхронно отправляет запрос кода подтверждения на номер телефона пользователя.
        """
        try:
            await self.client.send_code_request(self.phone_number)
            logging.info("Confirmation code sent to Telegram.")
        except errors.RPCError as e:
            logging.error(f"RPC Error while sending code request: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unknown error while sending code request: {e}")
            raise e