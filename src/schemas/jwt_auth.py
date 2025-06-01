from typing import Optional

from pydantic import BaseModel

from src.database.enums import TokenType


class JWTBase(BaseModel):
    access_token: bytes | str
    token_type: TokenType
    user_id: int


class JWTRead(JWTBase):
    pass


class JWTTokenCreate(JWTBase):
    pass


class JWTTokenUpdate(BaseModel):
    access_token: Optional[bytes | str] = None
    token_type: Optional[TokenType] = None

