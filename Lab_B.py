from lector import Lector
from analizador import Analizador
from afn import AFN

if __name__ == "__main__":
    expr_reg = None
    expr_reg = input('Ingrese una expresion regular: ')
    try:
        lector = Lector(expr_reg)
        tokens = lector.CrearTokens()
        e = Analizador(tokens)
        arbol = e.Postfix()
        print('\n\tExpresion aceptada')
        print('\tArbol: ', arbol)

    except AttributeError as e:
        print(f'\n\tERR: Expresion invalida (falta un parentesis)')

    except Exception as e:
        print(f'\n\tERR: {e}')

    afn = AFN(arbol, lector.get_simbolos(), expr_reg)
    afn_expr = afn.EvaluarExpr()
    afn.DiagramaAFN()
    

    exit(1)
