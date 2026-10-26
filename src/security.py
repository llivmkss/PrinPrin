"""Хеширование и проверка паролей."""

import hashlib
import hmac
import secrets

_ITERATIONS: int = 100_000
_SALT_SIZE: int = 16


class PasswordHasher:
    """Хеширует пароли алгоритмом PBKDF2 со случайной солью и проверяет их."""

    def make_hash(self, password: str) -> str:
        """Возвращает строку «соль$хеш» в шестнадцатеричном виде."""
        salt = secrets.token_bytes(_SALT_SIZE)
        return f"{salt.hex()}${self.__derive(password, salt).hex()}"

    def verify(self, password: str, stored: str) -> bool:
        """Проверяет пароль по ранее сохранённой строке «соль$хеш»."""
        salt_hex, digest_hex = stored.split("$")
        actual = self.__derive(password, bytes.fromhex(salt_hex))
        return hmac.compare_digest(actual, bytes.fromhex(digest_hex))

    @staticmethod
    def __derive(password: str, salt: bytes) -> bytes:
        """Вычисляет PBKDF2-хеш пароля для заданной соли."""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, _ITERATIONS
        )
