import xml.etree.ElementTree as ET
from graphviz import Digraph
import pydot


class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None

    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente


class Piso:
    def __init__(self, nombre, R, C, F, S):
        self.nombre = nombre
        self.R = R
        self.C = C
        self.F = F
        self.S = S
        self.patrones = ListaEnlazada()

class Patron:
    def __init__(self, codigo, patron):
        self.codigo = codigo
        self.patron = patron

class PisosGuatemala:
    def __init__(self):
        self.pisos = ListaEnlazada()

    def cargar_desde_xml(self, archivo):
        tree = ET.parse(archivo)
        root = tree.getroot()

        for piso_xml in root.findall('piso'):
            nombre = piso_xml.attrib['nombre']
            R = int(piso_xml.find('R').text)
            C = int(piso_xml.find('C').text)
            F = int(piso_xml.find('F').text)
            S = int(piso_xml.find('S').text)

            piso = Piso(nombre, R, C, F, S)
            patrones_xml = piso_xml.find('patrones')
            for patron_xml in patrones_xml.findall('patron'):
                codigo = patron_xml.attrib['codigo']
                patron = patron_xml.text.strip()
                piso.patrones.agregar(Patron(codigo, patron))

            self.pisos.agregar(piso)

def mostrar_patron(patron):
    print("  Patrón:")
    for fila in patron:
        print("   ", " ".join(fila))

    dot = Digraph()
    dot.attr(rankdir='LR')
    dot.node_attr.update(shape='square')

    # Agregar nodos al gráfico
    for i, fila in enumerate(patron):
        for j, color in enumerate(fila):
            if color == 'B':
                dot.node(f'{i}_{j}', style='filled', fillcolor='white')
            elif color == 'N':
                dot.node(f'{i}_{j}', style='filled', fillcolor='black')

    # Agregar conexiones entre nodos
    for i in range(len(patron)):
        for j in range(len(patron[0])):
            if j < len(patron[0]) - 1:
                dot.edge(f'{i}_{j}', f'{i}_{j+1}')
            if i < len(patron) - 1:
                dot.edge(f'{i}_{j}', f'{i+1}_{j}')

    dot.render('patron', format='png', view=True)


def encontrar_patron_por_codigo(piso, codigo):
    for patron in piso.patrones:
        if patron.codigo == codigo:
            return patron.patron
    return None

def contar_diferencias(patron_origen, patron_destino):
    count = 0
    for fila_origen, fila_destino in zip(patron_origen, patron_destino):
        for azulejo_origen, azulejo_destino in zip(fila_origen, fila_destino):
            if azulejo_origen != azulejo_destino:
                count += 1
    return count

def calcular_costo_minimo(piso, codigo_origen, codigo_destino):
    patron_origen = encontrar_patron_por_codigo(piso, codigo_origen)
    patron_destino = encontrar_patron_por_codigo(piso, codigo_destino)

    if patron_origen is None or patron_destino is None:
        return None, "Patrón origen o destino no encontrado"

    num_diferencias = contar_diferencias(patron_origen, patron_destino)
    costo_volteo = piso.F
    costo_intercambio = piso.S

    num_operaciones_intercambio = num_diferencias // 2
    num_operaciones_volteo = num_diferencias % 2

    costo_total = (num_operaciones_intercambio * costo_intercambio) + (num_operaciones_volteo * costo_volteo)

    return costo_total, ""

def generar_instrucciones(piso, codigo_origen, codigo_destino):
    patron_origen = encontrar_patron_por_codigo(piso, codigo_origen)
    patron_destino = encontrar_patron_por_codigo(piso, codigo_destino)

    if patron_origen is None or patron_destino is None:
        return None, "Patrón origen o destino no encontrado"

    instrucciones = []

    for i in range(len(patron_origen)):
        for j in range(len(patron_origen[0])):
            if patron_origen[i][j] != patron_destino[i][j]:
                if j < len(patron_origen[0]) - 1 and patron_origen[i][j] != patron_origen[i][j+1] and patron_destino[i][j] != patron_destino[i][j+1]:
                    instrucciones.append(f"Intercambiar azulejos en posición ({i+1},{j+1}) y ({i+1},{j+2})")
                    patron_origen[i][j], patron_origen[i][j+1] = patron_origen[i][j+1], patron_origen[i][j]
                elif i < len(patron_origen) - 1 and patron_origen[i][j] != patron_origen[i+1][j] and patron_destino[i][j] != patron_destino[i+1][j]:
                    instrucciones.append(f"Intercambiar azulejos en posición ({i+1},{j+1}) y ({i+2},{j+1})")
                    patron_origen[i][j], patron_origen[i+1][j] = patron_origen[i+1][j], patron_origen[i][j]
                else:
                    instrucciones.append(f"Voltear azulejo en posición ({i+1},{j+1})")
                    patron_origen[i][j] = 'B' if patron_origen[i][j] == 'N' else 'N'

    return instrucciones, ""

def mostrar_pisos_y_patrones(pisos_guatemala):
    print("Pisos disponibles:")
    for piso in pisos_guatemala.pisos:
        print(f"- {piso.nombre}")
        print("  Patrones disponibles:")
        for patron in piso.patrones:
            print(f"  - Código: {patron.codigo}")
            print("    Patrón:")
            for fila in patron.patron:
                print("    ", " ".join(fila))
        print()


def main():
    pisos_guatemala = PisosGuatemala()
    pisos_guatemala.cargar_desde_xml("archivo.xml")

    while True:
        print("\nBienvenido a Pisos de Guatemala, S.A.")
        print("Seleccione una opción:")
        print("1. Mostrar pisos y patrones disponibles")
        print("2. Calcular costo mínimo para cambiar de patrón")
        print("3. Generar instrucciones para cambiar de patrón")
        print("4. Salir")

        opcion = input("Ingrese el número de la opción deseada: ")

        if opcion == "1":
            mostrar_pisos_y_patrones(pisos_guatemala)
        elif opcion == "2":
            nombre_piso = input("Ingrese el nombre del piso: ")
            codigo_origen = input("Ingrese el código del patrón origen: ")
            codigo_destino = input("Ingrese el código del patrón destino: ")

            piso_encontrado = None
            for piso in pisos_guatemala.pisos:
                if piso.nombre == nombre_piso:
                    piso_encontrado = piso
                    break

            if piso_encontrado:
                costo, mensaje_error = calcular_costo_minimo(piso_encontrado, codigo_origen, codigo_destino)
                if costo is not None:
                    print(f"El costo mínimo para cambiar del patrón {codigo_origen} al patrón {codigo_destino} en el piso {nombre_piso} es de {costo}.")
                else:
                    print(f"Error: {mensaje_error}")
            else:
                print("Error: El piso especificado no fue encontrado.")



            pass
        elif opcion == "3":
            nombre_piso = input("Ingrese el nombre del piso: ")
            codigo_origen = input("Ingrese el código del patrón origen: ")
            codigo_destino = input("Ingrese el código del patrón destino: ")

            piso_encontrado = None
            for piso in pisos_guatemala.pisos:
                if piso.nombre == nombre_piso:
                    piso_encontrado = piso
                    break

            if piso_encontrado:
                instrucciones, mensaje_error = generar_instrucciones(piso_encontrado, codigo_origen, codigo_destino)
                if instrucciones is not None:
                    print(f"Instrucciones para cambiar del patrón {codigo_origen} al patrón {codigo_destino} en el piso {nombre_piso}:")
                    for instruccion in instrucciones:
                        print(instruccion)
                else:
                    print(f"Error: {mensaje_error}")
            else:
                print("Error: El piso especificado no fue encontrado.")
                pass





        elif opcion == "4":
            print("Gracias por utilizar Pisos de Guatemala, S.A. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    main()
