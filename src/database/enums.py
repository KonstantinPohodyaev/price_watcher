from enum import StrEnum


class Marketplace(StrEnum):
    WILDBERRIES = 'wildberries'
    OZON = 'ozon'


class TokenType(StrEnum):
    BEARER = 'bearer'
