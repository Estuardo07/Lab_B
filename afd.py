from graphviz import *
from pythomata import SimpleDFA

ESTADOS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def WriteToFile(filename: str, content: str):
    with open(filename, 'w') as _file:
        _file.write(content)

    return f'Archivo "{filename}" creado.'

class DFA:
    def __init__(self, tabal_transiciones, simbolos, estados, estado_final_afn, expr_reg):

        # Proveniente del NFA
        self.tabal_transiciones = tabal_transiciones
        self.estado_final_afn = estado_final_afn

        # Propiedades de un AF
        self.simbolos = simbolos
        self.func_trans = dict()
        self.estados = dict()
        self.estados_aceptacion = list()
        self.estado_inicial = 'A'

        try:
            self.simbolos.remove('e')
        except:
            pass

        self.nodos = []
        self.iteraciones = 0
        self.expr_reg = expr_reg

    def Trasladar(self, id_nodo, evaluar_simbolo='e', array=[], agregar_inicial=False, mover=False):

        arr = array
        nodo = self.nodos[id_nodo]
        # Recorremos el nodo si no está visitado
        if not nodo.visited and evaluar_simbolo in nodo.next_estados:

            # Marcamos el nodo
            nodo.Marcar()
            # Obtenemos los siguientes estados
            next_estados = [int(s) for s in nodo.next_estados[evaluar_simbolo]]
            if evaluar_simbolo == 'e':
                arr = [*next_estados]
            else:
                arr = [*next_estados]

            # ¿Tenemos que agregar el nodo inicial?
            if agregar_inicial:
                arr = [*next_estados, id_nodo]

            # Si tenemos que movernos varias veces, habrá que hacerlo de forma recursiva
            if not mover:
                for new_id_nodo in nodo.next_estados[evaluar_simbolo]:
                    arr += [*self.Trasladar(int(new_id_nodo), evaluar_simbolo, arr)]

        return list(set(arr))

    def EvaluarCierre(self, cierre, nodo,  estado_actual):

        # Estado inicial no creado?
        if not cierre:
            cierre = self.Trasladar(0, agregar_inicial=True)
            cierre.append(0)
            self.estados[estado_actual] = cierre
            if self.estado_final_afn in cierre:
                self.estados_aceptacion.append(estado_actual)

        # Por cada símbolo dentro del set...
        for simbolo in self.simbolos:
            cerrar_simbolo = list()
            new_set = list()

            # Clausura con el símbolo y el estado
            for valor in cierre:
                cerrar_simbolo += self.Trasladar(valor, simbolo, mover=True)
                [nodo.Desmarcar() for nodo in self.nodos]

            # Clausura con epsilon y el estado
            if cerrar_simbolo:
                cerradura_e = list()
                for valor_e in cerrar_simbolo:
                    cerradura_e += self.Trasladar(valor_e)
                    [nodo.Desmarcar() for nodo in self.nodos]

                new_set += list(set([*cerrar_simbolo, *cerradura_e]))

                # Si este nuevo estado no existe es nuevo...
                if not new_set in self.estados.valores():
                    self.iteraciones += 1
                    nuevo_estado = ESTADOS[self.iteraciones]

                    # Se crea la entrada en la función de transición
                    try:
                        dic_actual = self.func_trans[estado_actual]
                        dic_actual[simbolo] = nuevo_estado
                    except:
                        self.func_trans[estado_actual] = {simbolo: nuevo_estado}

                    try:
                        self.func_trans[nuevo_estado]
                    except:
                        self.func_trans[nuevo_estado] = {}

                    # Se agrega dicha entrada
                    self.estados[nuevo_estado] = new_set

                    # Si posee el estado final del AFN, entonces agregarlo al set
                    if self.estado_final_afn in new_set:
                        self.estados_aceptacion.append(nuevo_estado)

                    # Repetir con el nuevo set
                    self.EvaluarCierre(new_set, valor, nuevo_estado)

                # Este estado ya existe, se agrega la transición.
                else:
                    for S, V in self.estados.items():
                        if new_set == V:

                            try:
                                dic_actual = self.func_trans[estado_actual]
                            except:
                                self.func_trans[estado_actual] = {}
                                dic_actual = self.func_trans[estado_actual]

                            dic_actual[simbolo] = S
                            self.func_trans[estado_actual] = dic_actual
                            break

    def EvaluarExpr(self):
        estado_actual = 'A'

        for simbolo in self.expr_reg:
            # El símbolo no está dentro del set
            if not simbolo in self.simbolos:
                return 'El simbolo NO está dentro del set'
            # Intentamos hacer una transición a un nuevo estado
            try:
                estado_actual = self.func_trans[estado_actual][simbolo]
            except:
                # Volvemos al inicio y verificamos que sea un estado de aceptacion
                if estado_actual in self.estados_aceptacion and simbolo in self.func_trans['A']:
                    estado_actual = self.func_trans['A'][simbolo]
                else:
                    return 'No hay estado de aceptacion'

        return 'Aceptada' if estado_actual in self.estados_aceptacion else 'Rechazada'

    def GetEstados(self):
        for estado, valores in self.tabal_transiciones.items():
            self.nodos.append(Nodo(int(estado), valores))

    def AFNtoAFD(self):
        self.GetEstados()
        self.EvaluarCierre([], 0, 'A')

    def GaficarAFD(self):
        estados = set(self.func_trans.keys())
        alfabeto = set(self.simbolos)
        estado_inicial = 'A'

        afd = SimpleDFA(estados, alfabeto, estado_inicial,
                        set(self.estados_aceptacion), self.func_trans)

        grafico = afd.trim().to_graphviz()
        grafico.attr(rankdir='LR')

        source = grafico.source
        WriteToFile('./output/AFD.gv', source)
        grafico.render('./output/AFD.gv', format='pdf', view=True)


class Nodo:
    def __init__(self, estado, next_estados):
        self.estado = estado
        self.visited = False
        self.next_estados = next_estados

    def Marcar(self):
        self.visited = True

    def Desmarcar(self):
        self.visited = False

    def __repr__(self):
        return f'{self.estado} - {self.visited}: {self.next_estados}'
