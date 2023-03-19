from graphviz import Digraph

def gen_diagrama(filename: str, content: str):
    with open(filename, 'w') as _file:
        _file.write(content)

    return f'Diagrama "{filename}" creado con exito.'

class AFN:
    def __init__(self, arbol, simbolos, expr_reg):
        # Propiedades de un autómata finito no determinista
        self.estados_de_aceptacion = []
        self.simbolos = simbolos
        self.funcion_transicion = None
        self.estado_actual = 1

        # Árbol de nodos y expresión regular
        self.expr_reg = expr_reg
        self.arbol = arbol
        self.expr_aceptada = None

        # Propiedades para crear el diagrama
        self.dot = Digraph(comment='Diagrama AFN', strict=True)
        self.dot.attr(rankdir='LR')
        self.dot.attr('node', shape='circle')

        # Se ejecuta el algoritmo
        self.Render(arbol)
        self.funcion_transicion = self.gen_tabla_transiciones()
        self.estados_de_aceptacion = self.get_estado_aceptacion()

    def Render(self, nodo):
        self.estado_previo = self.estado_actual
        nombre_metodo = nodo.__class__.__name__ + 'Nodo'
        metodo = getattr(self, nombre_metodo)
        return metodo(nodo)

    def SimboloNodo(self, nodo):
        return nodo.value

    def ConcatNodo(self, nodo):

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.a)
        )

        self.estado_actual += 1
        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.b)
        )

    def OrNodo(self, nodo):
        nodo_i = self.estado_actual - 1
        mid_node = None

        self.dot.edge(
            str(nodo_i),
            str(self.estado_actual),
            'e'
        )
        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.a)
        )

        mid_node = self.estado_actual
        self.estado_actual += 1

        self.dot.edge(
            str(nodo_i),
            str(self.estado_actual),
            'e'
        )

        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.b)
        )

        self.estado_actual += 1

        self.dot.edge(
            str(mid_node),
            str(self.estado_actual),
            'e'
        )

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            'e'
        )

    def KleeneNodo(self, nodo):

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            'e'
        )

        primer_nodo = self.estado_actual - 1
        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.a)
        )

        self.dot.edge(
            str(self.estado_actual),
            str(primer_nodo + 1),
            'e'
        )

        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            'e'
        )

        self.dot.edge(
            str(primer_nodo),
            str(self.estado_actual),
            'e'
        )

    def PlusNodo(self, nodo):
        self.KleeneNodo(nodo)
        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.a)
        )

    def SignoIntNodo(self, nodo):
        nodo_i = self.estado_actual - 1
        mid_node = None

        self.dot.edge(
            str(nodo_i),
            str(self.estado_actual),
            'e'
        )
        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            self.Render(nodo.a)
        )

        mid_node = self.estado_actual
        self.estado_actual += 1

        self.dot.edge(
            str(nodo_i),
            str(self.estado_actual),
            'e'
        )

        self.estado_actual += 1

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            'e'
        )

        self.estado_actual += 1

        self.dot.edge(
            str(mid_node),
            str(self.estado_actual),
            'e'
        )

        self.dot.edge(
            str(self.estado_actual - 1),
            str(self.estado_actual),
            'e'
        )

    # def NoneTypeNodo(self, nodo):
    #     print("ERR: Expresion invalida ", nodo)

    def gen_tabla_transiciones(self):

        estados = [i.replace('\t', '')
                  for i in self.dot.source.split('\n') if '->' in i and '=' in i]

        self.funcion_transicion = dict.fromkeys(
            [str(s) for s in range(self.estado_actual + 1)])

        self.funcion_transicion[str(self.estado_actual)] = dict()

        for estado in estados:
            splitted = estado.split(' ')
            inicial = splitted[0]
            final = splitted[2]

            index_simbolo = splitted[3].index('=')
            simbolo = splitted[3][index_simbolo + 1]

            try:
                self.funcion_transicion[inicial][simbolo].append(final)
            except:
                self.funcion_transicion[inicial] = {simbolo: [final]}

        return self.funcion_transicion

    def EvaluarExpr(self):
        try:
            self.EvaluarNext(self.expr_reg[0], '0', self.expr_reg)
            return 'Aceptada' if self.expr_aceptada else 'Rechazada'
        except RecursionError:
            if self.expr_reg[0] in self.simbolos and self.expr_reg[0] != 'e':
                return 'Aceptada'
            else:
                return 'Rechazada'

    def EvaluarNext(self, evaluar_simbolo, estado_actual, evaluar_expr):

        if self.expr_aceptada != None:
            return

        transiciones = self.funcion_transicion[estado_actual]
        for simbolo_transicion in transiciones:

            if simbolo_transicion == 'e':
                if not evaluar_expr and str(self.estados_de_aceptacion) in transiciones['e']:
                    self.expr_aceptada = True
                    return

                for estado in transiciones['e']:
                    if self.expr_aceptada != None:
                        break
                    self.EvaluarNext(evaluar_simbolo, estado, evaluar_expr)

            elif simbolo_transicion == evaluar_simbolo:
                next_expr = evaluar_expr[1:]
                try:
                    next_simbolo = next_expr[0]
                except:
                    next_simbolo = None

                if not next_simbolo:
                    if str(self.estados_de_aceptacion) in transiciones[simbolo_transicion]:
                        self.expr_aceptada = True
                        return

                    elif str(self.estados_de_aceptacion) != estado_actual:
                        for estado in transiciones[simbolo_transicion]:
                            self.EvaluarNext('e', estado, None)
                        if self.expr_aceptada != None:
                            return

                if self.expr_aceptada != None:
                    return

                for estado in transiciones[simbolo_transicion]:
                    if not next_simbolo and str(estado) == self.estados_de_aceptacion:
                        self.expr_aceptada = True
                        return

                    self.EvaluarNext(next_simbolo, estado, next_expr)

    def get_estado_aceptacion(self):
        self.dot.node(str(self.estado_actual), shape='doublecircle')
        self.estados_de_aceptacion.append(self.estado_actual)
        return self.estado_actual

    def DiagramaAFN(self):
        source = self.dot.source
        debug_string = f'''
AFN:
- Símbolos: {self.simbolos}
- Estado final: {self.estados_de_aceptacion}
- Tabla de transición:
        '''
        gen_diagrama('./output/AFN.gv', source)
        self.dot.render('./output/AFN.gv', view=True)
