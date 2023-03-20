from pythomata import SimpleDFA

def WriteToFile(filename: str, content: str):
    with open(filename, 'w') as _file:
        _file.write(content)

    return f'Archivo "{filename}" creado.'

ESTADOS_D = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class AFDD:
    def __init__(self, tree, simbolos, expr_reg):

        # Para la sintaxis del arbol
        self.nodos = list()

        # Propiedades del automata
        self.simbolos = simbolos
        self.estados = list()
        self.func_trans = dict()
        self.estados_aceptacion = set()
        self.estado_inicial = 'A'

        # Propiedades de la clase
        self.tree = tree
        self.expr_reg = expr_reg
        self.estado_aumentado = None
        self.iter = 1

        self.ESTADOS = iter(ESTADOS_D)
        try:
            self.simbolos.remove('e')
        except:
            pass

        # Construccion del AFD
        self.ParseTree(self.tree)
        self.CalcSiguientePos()

    def CalcSiguientePos(self):
        for nodo in self.nodos:
            if nodo.value == '*':
                for i in nodo.ultimaPos:
                    nodo_hijo = next(filter(lambda x: x._id == i, self.nodos))
                    nodo_hijo.siguientePos += nodo.primeraPos
            elif nodo.value == '.':
                for i in nodo.c1.ultimaPos:
                    nodo_hijo = next(filter(lambda x: x._id == i, self.nodos))
                    nodo_hijo.siguientePos += nodo.c2.primeraPos

        # Estados
        estado_inicial = self.nodos[-1].primeraPos

        # Filtrar los nodos Simbolo
        self.nodos = list(filter(lambda x: x._id, self.nodos))
        self.estado_aumentado = self.nodos[-1]._id

        # Recursion
        self.CalcNuevosEstados(estado_inicial, next(self.ESTADOS))

    def CalcNuevosEstados(self, estado, estado_actual):

        if not self.estados:
            self.estados.append(set(estado))
            if self.estado_aumentado in estado:
                self.estados_aceptacion.update(estado_actual)

        # Iteramos por cada símbolo
        for simbolo in self.simbolos:

            # Obtener todos los nodos que tienen el mismo simbolo en SiguientePos
            simbolos_iguales = list(
                filter(lambda x: x.value == simbolo and x._id in estado, self.nodos))

            # Crear nuevo estado
            new_estado = set()
            for nodo in simbolos_iguales:
                new_estado.update(nodo.siguientePos)

            # Verificar si el nuevo estado no esta en la lista
            if new_estado not in self.estados and new_estado:

                # Obtener la letra del nuevo estado
                self.estados.append(new_estado)
                next_estado = next(self.ESTADOS)

                # Agregar el estado a la funcion transicion
                try:
                    self.func_trans[next_estado]
                except:
                    self.func_trans[next_estado] = dict()

                try:
                    estados_existentes = self.func_trans[estado_actual]
                except:
                    self.func_trans[estado_actual] = dict()
                    estados_existentes = self.func_trans[estado_actual]

                estados_existentes[simbolo] = next_estado
                self.func_trans[estado_actual] = estados_existentes

                # Verificar si es un estado de aceptacion
                if self.estado_aumentado in new_estado:
                    self.estados_aceptacion.update(next_estado)

                self.CalcNuevosEstados(new_estado, next_estado)

            elif new_estado:
                # Verificar si existe el estado
                for i in range(0, len(self.estados)):

                    if self.estados[i] == new_estado:
                        estado_ref = ESTADOS_D[i]
                        break

                # Agregar el simbolo de transicion
                try:
                    estados_existentes = self.func_trans[estado_actual]
                except:
                    self.func_trans[estado_actual] = {}
                    estados_existentes = self.func_trans[estado_actual]

                estados_existentes[simbolo] = estado_ref
                self.func_trans[estado_actual] = estados_existentes

    def ParseTree(self, nodo):
        nombreDelMetodo = nodo.__class__.__name__ + 'Nodo'
        metodo = getattr(self, nombreDelMetodo)
        return metodo(nodo)

    def SimboloNodo(self, nodo):
        new_nodo = Nodo(self.iter, [self.iter], [
                        self.iter], value=nodo.value, nullable=False)
        self.nodos.append(new_nodo)
        return new_nodo

    def OrNodo(self, nodo):
        nodo_a = self.ParseTree(nodo.a)
        self.iter += 1
        nodo_b = self.ParseTree(nodo.b)

        is_nullable = nodo_a.nullable or nodo_b.nullable
        primeraPos = nodo_a.primeraPos + nodo_b.primeraPos
        ultimaPos = nodo_a.ultimaPos + nodo_b.ultimaPos

        self.nodos.append(Nodo(None, primeraPos, ultimaPos,
                               is_nullable, '|', nodo_a, nodo_b))
        return Nodo(None, primeraPos, ultimaPos, is_nullable, '|', nodo_a, nodo_b)

    def ConcatNodo(self, nodo):
        nodo_a = self.ParseTree(nodo.a)
        self.iter += 1
        nodo_b = self.ParseTree(nodo.b)

        is_nullable = nodo_a.nullable and nodo_b.nullable
        if nodo_a.nullable:
            primeraPos = nodo_a.primeraPos + nodo_b.primeraPos
        else:
            primeraPos = nodo_a.primeraPos

        if nodo_b.nullable:
            ultimaPos = nodo_b.ultimaPos + nodo_a.ultimaPos
        else:
            ultimaPos = nodo_b.ultimaPos

        self.nodos.append(
            Nodo(None, primeraPos, ultimaPos, is_nullable, '.', nodo_a, nodo_b))

        return Nodo(None, primeraPos, ultimaPos, is_nullable, '.', nodo_a, nodo_b)

    def KleeneNodo(self, nodo):
        nodo_a = self.ParseTree(nodo.a)
        primeraPos = nodo_a.primeraPos
        ultimaPos = nodo_a.ultimaPos
        self.nodos.append(Nodo(None, primeraPos, ultimaPos, True, '*', nodo_a))
        return Nodo(None, primeraPos, ultimaPos, True, '*', nodo_a)

    def PlusNodo(self, nodo):
        nodo_a = self.ParseTree(nodo.a)

        self.iter += 1

        nodo_b = self.KleeneNodo(nodo)

        is_nullable = nodo_a.nullable and nodo_b.nullable
        if nodo_a.nullable:
            primeraPos = nodo_a.primeraPos + nodo_b.primeraPos
        else:
            primeraPos = nodo_a.primeraPos

        if nodo_b.nullable:
            ultimaPos = nodo_b.ultimaPos + nodo_a.ultimaPos
        else:
            ultimaPos = nodo_b.ultimaPos

        self.nodos.append(
            Nodo(None, primeraPos, ultimaPos, is_nullable, '.', nodo_a, nodo_b))

        return Nodo(None, primeraPos, ultimaPos, is_nullable, '.', nodo_a, nodo_b)

    def SignoIntNodo(self, nodo):
        # Node_a is epsilon
        nodo_a = Nodo(None, list(), list(), True)
        self.iter += 1
        nodo_b = self.ParseTree(nodo.a)

        is_nullable = nodo_a.nullable or nodo_b.nullable
        primeraPos = nodo_a.primeraPos + nodo_b.primeraPos
        ultimaPos = nodo_a.ultimaPos + nodo_b.ultimaPos

        self.nodos.append(Nodo(None, primeraPos, ultimaPos,
                               is_nullable, '|', nodo_a, nodo_b))
        return Nodo(None, primeraPos, ultimaPos, is_nullable, '|', nodo_a, nodo_b)

    def EvaluarExprReg(self):
        estado_actual = 'A'
        for simbolo in self.expr_reg:

            if not simbolo in self.simbolos:
                return 'Rechazada'

            try:
                estado_actual = self.func_trans[estado_actual][simbolo]
            except:
                if estado_actual in self.estados_aceptacion and simbolo in self.func_trans['A']:
                    estado_actual = self.func_trans['A'][simbolo]
                else:
                    return 'Rechazada'

        return 'Aceptada' if estado_actual in self.estados_aceptacion else 'Rechazada'

    def GraficarAFDD(self):
        estados = set(self.func_trans.keys())
        alfabeto = set(self.simbolos)

        afd = SimpleDFA(estados, alfabeto, self.estado_inicial,
                        self.estados_aceptacion, self.func_trans)

        grafica = afd.trim().to_graphviz()
        grafica.attr(rankdir='LR')

        source = grafica.source
        WriteToFile('./output/AFDD.gv', source)
        grafica.render('./output/AFDD.gv', format='pdf', view=True)


class Nodo:
    def __init__(self, _id, primeraPos=None, ultimaPos=None, nullable=False, value=None, c1=None, c2=None):
        self._id = _id
        self.primeraPos = primeraPos
        self.ultimaPos = ultimaPos
        self.siguientePos = list()
        self.nullable = nullable
        self.value = value
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return f'''
    id: {self._id}
    value: {self.value}
    primeraPos: {self.primeraPos}
    ultimaPos: {self.ultimaPos}
    siguientePos: {self.siguientePos}
    nullabe: {self.nullable}
    '''
