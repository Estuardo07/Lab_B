from tokens import Token, TipoDeToken

SIMBOLOS = 'abcdefghijklmnopqrstuvwxyz0123456789.,:;"-/'


class LectorDirecto:

    def __init__(self, string: str):
        self.string = iter(string.replace(' ', ''))
        self.input = set()
        self.sinParentDer = False
        self.Next()

    def Next(self):
        try:
            self.char_actual = next(self.string)
        except StopIteration:
            self.char_actual = None

    def CrearTokens(self):
        while self.char_actual != None:

            if self.char_actual in SIMBOLOS:
                self.input.add(self.char_actual)
                yield Token(TipoDeToken.SIMBOLO, self.char_actual)

                self.Next()

                if self.char_actual != None and \
                        (self.char_actual in SIMBOLOS or self.char_actual == '('):
                    yield Token(TipoDeToken.CONCAT, '.')

            elif self.char_actual == '|':
                yield Token(TipoDeToken.OR, '|')

                self.Next()

                if self.char_actual != None and self.char_actual not in '()':
                    yield Token(TipoDeToken.PARENT_IZQ)

                    while self.char_actual != None and self.char_actual not in ')*+?':
                        if self.char_actual in SIMBOLOS:
                            self.input.add(self.char_actual)
                            yield Token(TipoDeToken.SIMBOLO, self.char_actual)

                            self.Next()
                            if self.char_actual != None and \
                                    (self.char_actual in SIMBOLOS or self.char_actual == '('):
                                yield Token(TipoDeToken.CONCAT, '.')

                    if self.char_actual != None and self.char_actual in '*+?':
                        self.sinParentDer = True
                    elif self.char_actual != None and self.char_actual == ')':
                        yield Token(TipoDeToken.PARENT_DER, ')')
                    else:
                        yield Token(TipoDeToken.PARENT_DER, ')')

            elif self.char_actual == '(':
                self.Next()
                yield Token(TipoDeToken.PARENT_IZQ)

            elif self.char_actual in (')*+?'):

                if self.char_actual == ')':
                    self.Next()
                    yield Token(TipoDeToken.PARENT_DER)

                elif self.char_actual == '*':
                    self.Next()
                    yield Token(TipoDeToken.KLEENE)

                elif self.char_actual == '+':
                    self.Next()
                    yield Token(TipoDeToken.PLUS)

                elif self.char_actual == '?':
                    self.Next()
                    yield Token(TipoDeToken.SIGNO_INT)

                if self.sinParentDer:
                    yield Token(TipoDeToken.PARENT_DER)
                    self.sinParentDer = False

                if self.char_actual != None and \
                        (self.char_actual in SIMBOLOS or self.char_actual == '('):
                    yield Token(TipoDeToken.CONCAT, '.')

            else:
                raise Exception(f'Entrada invalida: {self.char_actual}')

        yield Token(TipoDeToken.CONCAT, '.')
        yield Token(TipoDeToken.SIMBOLO, '#')

    def GetSimbolos(self):
        return self.input
