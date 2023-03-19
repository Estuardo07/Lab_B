from enum import Enum


class TipoDeToken(Enum):
    SIMBOLO = 0
    CONCAT = 1
    OR = 2
    KLEENE = 3
    PLUS = 4
    SIGNO_INT = 5
    PARENT_IZQ = 6
    PARENT_DER = 7


class Token:
    def __init__(self, type: TipoDeToken, value=None):
        self.type = type
        self.value = value
        self.precedence = type.value

    def __repr__(self):
        return f'{self.type.name}: {self.value}'
