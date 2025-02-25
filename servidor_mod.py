import socket
import threading

# Diccionario para almacenar clientes por sala
salas = {f"Sala {i}": [] for i in range(1, 100)}  # Crear 99 salas

def enviar_salas_a_todos():
    lista_salas = "SALAS:" + ",".join(salas.keys())
    for sala in salas:
        for cliente, _ in salas[sala]:
            try:
                cliente.send(lista_salas.encode())
            except:
                pass  # Si no se puede enviar, el cliente probablemente se desconectó

def manejar_cliente(cliente_socket, direccion):
    global salas
    nombre = None
    sala_actual = None
    try:
        cliente_socket.send("Ingrese su nombre: ".encode())
        nombre = cliente_socket.recv(1024).decode().strip()
        cliente_socket.send("Ingrese la sala a la que desea unirse: ".encode())
        sala_actual = cliente_socket.recv(1024).decode().strip()

        def cambiar_sala(nueva_sala):
            nonlocal sala_actual
            if sala_actual in salas and (cliente_socket, nombre) in salas[sala_actual]:
                salas[sala_actual].remove((cliente_socket, nombre))
            if nueva_sala not in salas:
                salas[nueva_sala] = []
            salas[nueva_sala].append((cliente_socket, nombre))
            sala_actual = nueva_sala
            cliente_socket.send(f"Cambiaste a la sala: {sala_actual}\n".encode())
            enviar_salas_a_todos()

        cambiar_sala(sala_actual)
        print(f"{nombre} se unió a la sala {sala_actual}")
        enviar_salas_a_todos()

        while True:
            mensaje = cliente_socket.recv(1024).decode().strip()
            if not mensaje:
                break

            if mensaje.lower() == "/users":
                usuarios_sala = [user for _, user in salas.get(sala_actual, [])]
                cliente_socket.send(f"Usuarios en {sala_actual}: {', '.join(usuarios_sala)}\n".encode())
                continue

            if mensaje.lower() == "/allusers":
                todos_los_usuarios = [user for users in salas.values() for _, user in users]
                cliente_socket.send(f"Usuarios conectados: {', '.join(todos_los_usuarios)}\n".encode())
                continue

            print(f"[{sala_actual}] {nombre}: {mensaje}")
            for cliente, _ in salas.get(sala_actual, []):
                if cliente != cliente_socket:
                    try:
                        cliente.send(f"[{sala_actual}] {nombre}: {mensaje}\n".encode())
                    except:
                        pass
    except Exception as e:
        print(f"Error con {nombre}: {e}")
    finally:
        if nombre and sala_actual:
            print(f"{nombre} en sala {sala_actual} desconectado")
            if sala_actual in salas and (cliente_socket, nombre) in salas[sala_actual]:
                salas[sala_actual].remove((cliente_socket, nombre))
            enviar_salas_a_todos()
        cliente_socket.close()

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("0.0.0.0", 12345))
servidor.listen(5)
print("Servidor en espera de conexiones")

while True:
    cliente_socket, direccion = servidor.accept()
    print(f"Conexión aceptada desde {direccion}")
    hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
    hilo.start()
