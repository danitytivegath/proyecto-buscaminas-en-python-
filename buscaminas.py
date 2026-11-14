
import random
import os

os.system("")  # Activa los colores en la consola de Windows

#colores (codigos ANSI) 
RESET = "\033[0m"
NEGRITA = "\033[1m"
GRIS = "\033[90m"
ROJO = "\033[91m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
MAGENTA = "\033[95m"
CIAN = "\033[96m"

#Color de cada número (el índice es el número de minas vecinas)
COLORES_NUMEROS = ["", AZUL, VERDE, ROJO, MAGENTA, AMARILLO, CIAN, ROJO, GRIS]

#niveles de dificultad 
NOMBRES_DIF = ["Muy fácil", "Fácil", "Medio", "Difícil", "Experto"]
FILAS_DIF = [4, 6, 8, 10, 12]
MINAS_DIF = [3, 6, 10, 18, 30]
MULTIPLICADOR_DIF = [1, 2, 3, 4, 5]

#funciones extra

def leer_numero(mensaje, minimo, maximo):
    """Pide un número y repite hasta que sea válido (evita que el programa se caiga)."""
    while True:
        texto = input(mensaje)
        if texto.isdigit():
            numero = int(texto)
            if numero >= minimo and numero <= maximo:
                return numero
        print(f"{ROJO}Entrada no válida. Escribe un número entre {minimo} y {maximo}.{RESET}")


def crear_matriz(filas, columnas, valor):
    matriz = []
    for i in range(0, filas):
        fila = []
        for j in range(0, columnas):
            fila.append(valor)
        matriz.append(fila)
    return matriz


def titulo(texto):
    print("\n" + CIAN + "=" * 40 + RESET)
    print(CIAN + NEGRITA + texto.center(40) + RESET)
    print(CIAN + "=" * 40 + RESET)


#registro de usuario

def registrar(usuarios, passwords, puntajes):
    titulo("REGISTRO DE NUEVO JUGADOR")
    nuevo_u = input("Crea tu usuario: ")

    if nuevo_u.strip() == "":
        print(ROJO + "El usuario no puede estar vacío." + RESET)
        return

    for i in range(0, len(usuarios)):
        if usuarios[i] == nuevo_u:
            print(ROJO + "¡Ese usuario ya existe! Elige otro." + RESET)
            return

    nuevo_p = input("Crea tu contraseña: ")
    if nuevo_p.strip() == "":
        print(ROJO + "La contraseña no puede estar vacía." + RESET)
        return

    usuarios.append(nuevo_u)
    passwords.append(nuevo_p)
    puntajes.append(0)
    print(VERDE + "¡Registro exitoso! Ya puedes iniciar sesión." + RESET)


#iniciar sesion
def login(usuarios, passwords, puntajes):
    titulo("INICIO DE SESIÓN")
    u = input("Usuario: ")
    p = input("Contraseña: ")

    encontrado = False
    pos = 0
    for i in range(0, len(usuarios)):
        if usuarios[i] == u and passwords[i] == p:
            encontrado = True
            pos = i
            break

    if encontrado:
        print(VERDE + "\n¡Bienvenido al Buscaminas, " + u + "!" + RESET)
        menu_juego(u, pos, puntajes, usuarios)
    else:
        print(ROJO + "Error: Usuario o contraseña incorrectos." + RESET)


#tabla de puntuaciones
def mostrar_tabla_puntuaciones(usuarios, puntajes):
    titulo("TABLA DE PUNTUACIONES")

    orden = []
    for i in range(0, len(usuarios)):
        orden.append(i)

    for i in range(0, len(orden)):
        for j in range(0, len(orden) - 1 - i):
            if puntajes[orden[j]] < puntajes[orden[j + 1]]:
                temporal = orden[j]
                orden[j] = orden[j + 1]
                orden[j + 1] = temporal

    for lugar in range(0, len(orden)):
        idx = orden[lugar]
        print(f" {lugar + 1}. {usuarios[idx]:<15} {AMARILLO}{puntajes[idx]:>6} pts{RESET}")
    print(CIAN + "=" * 40 + RESET)


#funcionamiento del buscaminas

def colocar_minas(minas, filas, columnas, total_minas, f_segura, c_segura):
    """Coloca minas al azar. Nunca pone una en la primera casilla elegida."""
    colocadas = 0
    while colocadas < total_minas:
        f = random.randint(0, filas - 1)
        c = random.randint(0, columnas - 1)
        if minas[f][c] != -1 and not (f == f_segura and c == c_segura):
            minas[f][c] = -1  # -1 significa "hay mina"
            colocadas = colocadas + 1

    #calcular cuantas minas tiene cada casilla alrededor
    for f in range(0, filas):
        for c in range(0, columnas):
            if minas[f][c] != -1:
                cuenta = 0
                for df in range(-1, 2):
                    for dc in range(-1, 2):
                        nf = f + df
                        nc = c + dc
                        if nf >= 0 and nf < filas and nc >= 0 and nc < columnas:
                            if minas[nf][nc] == -1:
                                cuenta = cuenta + 1
                minas[f][c] = cuenta


def destapar(f, c, minas, visible, filas, columnas):
    """Destapa la casilla. Si no tiene minas alrededor (0), destapa también sus vecinas.
    Devuelve cuántas casillas se destaparon."""
    destapadas = 0
    pendientes = [[f, c]]

    while len(pendientes) > 0:
        actual = pendientes.pop()
        fa = actual[0]
        ca = actual[1]

        if visible[fa][ca] != "?":
            continue  #ya estaba destapada o tiene bandera

        visible[fa][ca] = "D"
        destapadas = destapadas + 1

        if minas[fa][ca] == 0:
            for df in range(-1, 2):
                for dc in range(-1, 2):
                    nf = fa + df
                    nc = ca + dc
                    if nf >= 0 and nf < filas and nc >= 0 and nc < columnas:
                        pendientes.append([nf, nc])

    return destapadas


def simbolo(visible, minas, f, c, revelar_todo):
    """Devuelve lo que se dibuja en una casilla."""
    estado = visible[f][c]
    valor = minas[f][c]

    if revelar_todo and valor == -1:
        if estado == "B":
            return VERDE + "B" + RESET   #bandera bien puesta
        return ROJO + "*" + RESET        #mina
    if estado == "B":
        return AMARILLO + "B" + RESET
    if estado == "?":
        return GRIS + "■" + RESET
    if valor == 0:
        return " "
    return COLORES_NUMEROS[valor] + str(valor) + RESET


def mostrar_tablero(visible, minas, filas, columnas, revelar_todo):
    print()
    encabezado = "    "
    for j in range(0, columnas):
        encabezado = encabezado + f"{j:^3}"
    print(NEGRITA + encabezado + RESET)
    print("    " + "---" * columnas)

    for i in range(0, filas):
        linea = f"{i:>2} |"
        for j in range(0, columnas):
            linea = linea + " " + simbolo(visible, minas, i, j, revelar_todo) + " "
        print(linea)
    print()


def elegir_dificultad():
    print("\n" + NEGRITA + "--- SELECCIONA LA DIFICULTAD ---" + RESET)
    for i in range(0, len(NOMBRES_DIF)):
        print(f"{i + 1}. {NOMBRES_DIF[i]:<10} (Tablero {FILAS_DIF[i]}x{FILAS_DIF[i]}, "
              f"{MINAS_DIF[i]} minas, puntos x{MULTIPLICADOR_DIF[i]})")
    return leer_numero("Elige opción: ", 1, len(NOMBRES_DIF)) - 1


def jugar_buscaminas(pos_usuario, lista_puntajes):
    nivel = elegir_dificultad()
    filas = FILAS_DIF[nivel]
    columnas = FILAS_DIF[nivel]
    minas_totales = MINAS_DIF[nivel]
    multiplicador = MULTIPLICADOR_DIF[nivel]

    minas = crear_matriz(filas, columnas, 0)       # números y minas (-1)
    visible = crear_matriz(filas, columnas, "?")   # "?" oculta, "D" destapada, "B" bandera

    minas_colocadas = False
    juego_activo = True
    resultado = ""   # "victoria", "derrota" o "retiro"
    puntos_partida = 0
    casillas_seguras_restantes = (filas * columnas) - minas_totales
    banderas = 0

    titulo("NIVEL " + NOMBRES_DIF[nivel].upper())
    print("Acciones: " + NEGRITA + "d" + RESET + " = destapar | " + NEGRITA + "b" + RESET +
          " = poner/quitar bandera | " + NEGRITA + "r" + RESET + " = retirarte")

    while juego_activo:
        mostrar_tablero(visible, minas, filas, columnas, False)
        print(f"Minas restantes: {ROJO}{minas_totales - banderas}{RESET}   "
              f"Puntos: {AMARILLO}{puntos_partida}{RESET}")

        accion = input("Acción (d / b / r): ").lower()

        if accion == "r":
            resultado = "retiro"
            juego_activo = False

        elif accion == "d" or accion == "b":
            f_user = leer_numero(f"Elige fila (0 a {filas - 1}): ", 0, filas - 1)
            c_user = leer_numero(f"Elige columna (0 a {columnas - 1}): ", 0, columnas - 1)

            if accion == "b":
                if visible[f_user][c_user] == "?":
                    visible[f_user][c_user] = "B"
                    banderas = banderas + 1
                elif visible[f_user][c_user] == "B":
                    visible[f_user][c_user] = "?"
                    banderas = banderas - 1
                else:
                    print(ROJO + "No puedes poner bandera en una casilla destapada." + RESET)

            else:  # accion == "d"
                if visible[f_user][c_user] == "B":
                    print(ROJO + "Esa casilla tiene bandera. Quítala primero con 'b'." + RESET)
                elif visible[f_user][c_user] == "D":
                    print(ROJO + "Ya habías destapado esta casilla. Prueba otra." + RESET)
                else:
                    #las minas se colocan en el primer movimiento (así el usuario nunca pierde en el primer turno)
                    if not minas_colocadas:
                        colocar_minas(minas, filas, columnas, minas_totales, f_user, c_user)
                        minas_colocadas = True

                    if minas[f_user][c_user] == -1:
                        resultado = "derrota"
                        juego_activo = False
                    else:
                        cantidad = destapar(f_user, c_user, minas, visible, filas, columnas)
                        puntos_partida = puntos_partida + cantidad * 10 * multiplicador
                        casillas_seguras_restantes = casillas_seguras_restantes - cantidad

                        if casillas_seguras_restantes == 0:
                            resultado = "victoria"
                            juego_activo = False
        else:
            print(ROJO + "Acción no válida. Usa d, b o r." + RESET)

    #game over
    if resultado == "derrota":
        mostrar_tablero(visible, minas, filas, columnas, True)
        print(ROJO + NEGRITA + "¡BOOM!  Pisaste una mina. Perdiste la partida." + RESET)
        print("Al perder no sumas puntos. ¡Retírate a tiempo la próxima vez!")
        puntos_partida = 0
    elif resultado == "victoria":
        mostrar_tablero(visible, minas, filas, columnas, True)
        bono = 100 * multiplicador
        puntos_partida = puntos_partida + bono
        print(VERDE + NEGRITA + "¡FELICIDADES! Despejaste todo el tablero." + RESET)
        print(f"Bono de victoria: +{bono} puntos")
    else:
        print(AMARILLO + "Te retiraste a tiempo con los puntos acumulados." + RESET)

    print(f"\nPuntaje obtenido en esta partida: {AMARILLO}{puntos_partida}{RESET}")
    if puntos_partida > lista_puntajes[pos_usuario]:
        lista_puntajes[pos_usuario] = puntos_partida
        print(VERDE + "¡Nuevo récord personal guardado en la tabla!" + RESET)


#menu interno
def menu_juego(nombre, pos, puntajes, usuarios):
    op = ""
    while op != "3":
        titulo("MENÚ DEL BUSCAMINAS")
        print(f"Jugador: {NEGRITA}{nombre}{RESET}   Récord: {AMARILLO}{puntajes[pos]}{RESET} pts\n")
        print("1. Jugar partida")
        print("2. Ver tabla de puntuaciones global")
        print("3. Cerrar sesión")
        op = input("Elige una opción: ")

        if op == "1":
            jugar_buscaminas(pos, puntajes)
        elif op == "2":
            mostrar_tabla_puntuaciones(usuarios, puntajes)
        elif op == "3":
            print("Cerrando sesión...")
        else:
            print(ROJO + "Opción inválida." + RESET)


#programa principal
def main():
    usuarios = ["pro_gamer"]
    passwords = ["1234"]
    puntajes = [150]

    opcion = ""
    while opcion != "4":
        titulo("PROYECTO FINAL - BUSCAMINAS")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Ver tabla de puntuaciones")
        print("4. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            registrar(usuarios, passwords, puntajes)
        elif opcion == "2":
            login(usuarios, passwords, puntajes)
        elif opcion == "3":
            mostrar_tabla_puntuaciones(usuarios, puntajes)
        elif opcion == "4":
            print("¡Mucho éxito con la entrega del proyecto!")
        else:
            print(ROJO + "Opción no válida." + RESET)


main()
