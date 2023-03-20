from lector import Lector
from analizador import Analizador
from afn import AFN
from afd import AFD
from afdDirecto import AFDD
from lectorDirecto import LectorDirecto

if __name__ == "__main__":
    expr_reg = None
    expr_reg = input('Ingrese una expresion regular: ')
    cadena = input('Ingrese una cadena a evaluar: ')

    try:
        lector = Lector(expr_reg)
        tokens = lector.CrearTokens()
        analizador = Analizador(tokens)
        arbol = analizador.Postfix()

        print('\n\tExpresion aceptada')
        print('\tArbol: ', arbol)

        lector_directo = LectorDirecto(expr_reg)
        tokens_directo = lector_directo.CrearTokens()
        analizador_directo = Analizador(tokens_directo)
        arbol_directo = analizador_directo.Postfix()

        print('\n\tExpresion aceptada')
        print('\tArbol: ', arbol_directo)

    except AttributeError as e:
        print(f'\n\tERR: Expresion invalida (falta un parentesis)')

    except Exception as e:
        print(f'\n\tERR: {e}')

    afn = AFN(arbol, lector.get_simbolos(), cadena)
    afn_expr = afn.EvaluarExpr()
    print('La cadena es aceptada o rechazada por la expresion regular?')
    print(afn_expr)

    afd = AFD(afn.funcion_transicion, afn.simbolos, afn.estado_actual, afn.estados_de_aceptacion, cadena)
    afd.AFNtoAFD()
    afd_expr = afd.EvaluarExpr()
    print('La cadena es aceptada o rechazada por la expresion regular?')
    print(afd_expr)

    afdd = AFDD(arbol_directo, lector_directo.GetSimbolos(), cadena)
    afdd_expr = afdd.EvaluarExprReg()
    print('La cadena es aceptada o rechazada por la expresion regular?')
    print(afdd_expr)

    afn.DiagramaAFN()
    afd.GaficarAFD()
    afdd.GraficarAFDD()

    print('\nEND')

    exit(0)
