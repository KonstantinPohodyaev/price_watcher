import re


VALIDATE_FULL_NAME_PATTERN = '^[A-ZА-ЯЁa-zа-яё]+ [A-ZА-ЯЁa-zа-яё]+$'
VALIDATE_FULL_NAME_ERROR = 'Недопустимый формат ввода имени и фамилии.'


def validate_full_name(
    full_name: str
) -> None:
    """Проверяет формат ввода имени и фамилии."""
    return bool(
        re.match(
            VALIDATE_FULL_NAME_PATTERN,
            full_name
        )
    )
