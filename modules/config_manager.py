import json
import os
import logging
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = 'config.json'):
        """
        Initializes the ConfigManager with a default or specified configuration file path.

        :param config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {
            'database': {
                'path': 'app_database.db'
            },
            'telegram': {
                'api_id': '',
                'api_hash': '',
                'phone_number': ''
            }
        }

    def load_config(self) -> bool:
        """
        Loads the configuration from the specified JSON file.

        :return: True if the configuration was loaded successfully, False otherwise.
        """
        if not os.path.exists(self.config_path):
            logging.warning(f"Configuration file '{self.config_path}' not found. A new one will be created.")
            self.save_config()
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            logging.info("Configuration loaded successfully.")
            return True
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error while loading configuration: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while loading configuration: {e}")
            return False

    def save_config(self) -> None:
        """
        Saves the current configuration to the specified JSON file.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=4, ensure_ascii=False)
            logging.info("Configuration saved successfully.")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")

    def is_config_complete(self) -> bool:
        """
        Checks if the Telegram configuration is complete.

        :return: True if all Telegram configurations are filled, False otherwise.
        """
        telegram_config = self.config.get('telegram', {})
        is_complete = all([
            telegram_config.get('api_id'),
            telegram_config.get('api_hash'),
            telegram_config.get('phone_number')
        ])
        if not is_complete:
            logging.warning("Telegram configuration is incomplete.")
        return is_complete

    def get_config(self) -> Dict[str, Any]:
        """
        Returns the current configuration.

        :return: Dictionary containing the current configuration.
        """
        return self.config

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Updates the current configuration with new values.

        :param new_config: Dictionary containing the new configuration values.
        """
        self.config.update(new_config)
        self.save_config()
        logging.info("Configuration updated successfully.")

    def reset_config(self) -> None:
        """
        Resets the configuration to default values.
        """
        self.config = {
            'database': {
                'path': 'app_database.db'
            },
            'telegram': {
                'api_id': '',
                'api_hash': '',
                'phone_number': ''
            }
        }
        self.save_config()
        logging.info("Configuration reset to default values.")