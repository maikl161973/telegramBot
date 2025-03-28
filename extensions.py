from typing import Optional, Dict, Any

import requests

from utils import params_from_config


class ServerCryptoException(Exception):
    """Ошибка сервера получения котировок"""


class SystemException(Exception):
    """Ошибка приложения"""


class CryptoCurrency:
    """Получение котировок"""

    def __init__(self):
        params = self._read_config()

        self.host: Optional[str] = params.get('host', None)
        self.api_url: Optional[str] = params.get('api_url', None)
        self.fsim_param: Optional[str] = params.get('fsim_param', None)
        self.tsim_param: Optional[str] = params.get('tsim_param', None)
        self.timeout: int = params.get('timeout', 300)

    @staticmethod
    def _read_config() -> Dict[str, Any]:
        """Чтение настроек"""
        return params_from_config('CryptoCurrencyParams')

    def _check_params(self) -> None:
        """Проверка параметров настроек"""
        if not all([self.host, self.api_url, self.fsim_param, self.tsim_param]):
            raise SystemException(
                'Не все параметры заполнены в настройках получения котировок'
            )

    def _err_server(self, message: str = '') -> ServerCryptoException:
        """Форматирование серверной ошибки"""
        raise ServerCryptoException(
            f'Ошибка получения котировки с сервера {message}'
        )

    def get_price(self, fsim: str, tsims: str, amount: float) -> float:
        """Запрос котировок"""
        self._check_params()

        try:
            response = requests.get(
                f'{self.host}{self.api_url}?{self.fsim_param}='
                f'{fsim}&{self.tsim_param}={tsims}',
                timeout=self.timeout
            )
        except Exception as err:
            self._err_server(str(err))
            return None

        if response.status_code != 200:
            self._err_server(
                f'HTTP статус: {response.status_code}, Ответ: {response.content}')

        response_data = response.json()
        if tsims not in response_data:
            self._err_server(f'Отсутствует параметр "{tsims}" в ответе сервера')

        return float(response_data[tsims]) * amount
