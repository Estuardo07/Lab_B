from tokens import TipoDeToken
from nodos import *


class Analizador:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.Next()

    def Next(self):
        try:
            self.curr_token = next(self.tokens) # iterar tokens generados
        except StopIteration:
            self.curr_token = None

    def NuevoSimbolo(self):
        token = self.curr_token

        if token.type == TipoDeToken.PARENT_IZQ:
            self.Next()
            res = self.Expresion()

            if self.curr_token.type != TipoDeToken.PARENT_DER:
                raise Exception('Hace falta un parentesis derecho.')

            self.Next()
            return res

        elif token.type == TipoDeToken.SIMBOLO:
            self.Next()
            return Simbolo(token.value)

    def NuevoOperador(self):
        res = self.NuevoSimbolo()

        while self.curr_token != None and \
                (
                    self.curr_token.type == TipoDeToken.KLEENE or
                    self.curr_token.type == TipoDeToken.PLUS or
                    self.curr_token.type == TipoDeToken.SIGNO_INT
                ):
            if self.curr_token.type == TipoDeToken.KLEENE:
                self.Next()
                res = Kleene(res)
            elif self.curr_token.type == TipoDeToken.SIGNO_INT:
                self.Next()
                res = SignoInt(res)
            else:
                self.Next()
                res = Plus(res)

        return res

    def Expresion(self):
        res = self.NuevoOperador()

        while self.curr_token != None and \
                (
                    self.curr_token.type == TipoDeToken.CONCAT or
                    self.curr_token.type == TipoDeToken.OR
                ):
            if self.curr_token.type == TipoDeToken.OR:
                self.Next()
                res = Or(res, self.NuevoOperador())

            elif self.curr_token.type == TipoDeToken.CONCAT:
                self.Next()
                res = Concat(res, self.NuevoOperador())

        return res

    def Postfix(self):
        if self.curr_token == None:
            return None

        res = self.Expresion()

        return res
