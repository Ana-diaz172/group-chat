import socket
import threading

# Diccionario para almacenar clientes por sala
salas = {f"Sala {i}": [] for i in range(1, 100)}  # Crear 99 salas

# Función para enviar la lista de salas a todos los clientes
def enviar_salas_a_todos():
    lista_salas = "SALAS:" + ",".join(salas.keys())  # Formato: "SALAS:sala1,sala2,sala3"
    for sala in salas:
        for cliente, _ in salas[sala]:
            try:
                cliente.send(lista_salas.encode())
            except:
                pass  # Si no se puede enviar, el cliente probablemente se desconectó

# Manejo de cliente
def manejar_cliente(cliente_socket, direccion):
    global salas
    nombre = None
    sala_actual = None

    try:
        # Pedir nombre y sala inicial
        cliente_socket.send("Ingrese su nombre: ".encode())
        nombre = cliente_socket.recv(1024).decode().strip()
        cliente_socket.send("Ingrese la sala a la que desea unirse: ".encode())
        sala_actual = cliente_socket.recv(1024).decode().strip()

        # Función para cambiar de sala
        def cambiar_sala(nueva_sala):
            nonlocal sala_actual
            if sala_actual in salas:
                # Verificar si el cliente sigue en la sala antes de eliminarlo
                if (cliente_socket, nombre) in salas[sala_actual]:
                    salas[sala_actual].remove((cliente_socket, nombre))
                # No eliminamos la sala, incluso si queda vacía

            if nueva_sala not in salas:
                salas[nueva_sala] = []
            salas[nueva_sala].append((cliente_socket, nombre))
            sala_actual = nueva_sala
            cliente_socket.send(f"Cambiaste a la sala: {sala_actual}\n".encode())
            enviar_salas_a_todos()  # Enviar la lista actualizada de salas a todos

        cambiar_sala(sala_actual)  # Unirse a la sala inicial
        print(f"{nombre} se unió a la sala {sala_actual}")

        # Enviar la lista de salas al cliente recién conectado
        enviar_salas_a_todos()

        while True:
            mensaje = cliente_socket.recv(1024).decode().strip()
            if not mensaje:
                break  # Cliente desconectado

            if mensaje.lower().startswith("/cambiar "):  # Comando para cambiar de sala
                nueva_sala = mensaje.split(" ", 1)[1]
                cambiar_sala(nueva_sala)
                continue  # Evitar enviar el mensaje de comando a la sala

            print(f"[{sala_actual}] {nombre}: {mensaje}")
            for cliente, cliente_nombre in salas.get(sala_actual, []):
                if cliente != cliente_socket:
                    try:
                        cliente.send(f"[{sala_actual}] {nombre}: {mensaje}\n".encode())
                    except:
                        # Si no se puede enviar, el cliente probablemente se desconectó
                        pass
    except Exception as e:
        print(f"Error con {nombre}: {e}")
    finally:
        if nombre and sala_actual:
            print(f"{nombre} en sala {sala_actual} desconectado")
            if sala_actual in salas:
                if (cliente_socket, nombre) in salas[sala_actual]:
                    salas[sala_actual].remove((cliente_socket, nombre))
                # No eliminamos la sala, incluso si queda vacía
            enviar_salas_a_todos()  # Enviar la lista actualizada de salas a todos
        cliente_socket.close()

# Configuración del servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("0.0.0.0", 12345))  # Escucha en todas las interfaces
servidor.listen(5)
print("Servidor en espera de conexiones")

while True:
    cliente_socket, direccion = servidor.accept()
    print(f"Conexión aceptada desde {direccion}")
    hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
    hilo.start()