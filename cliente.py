import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, Listbox

# Función para obtener el nombre y abrir la ventana de chat
def Obtener_nombre():
    nombre_usuario = nombre.get()
    if nombre_usuario:
        ventana.destroy()  # Cierra la ventana de login
        iniciar_chat(nombre_usuario)
    else:
        messagebox.showwarning("Error", "Debes ingresar un nombre.")

# Función para iniciar la ventana de chat
def iniciar_chat(nombre_usuario):
    try:
        # Configuración del cliente
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect(("192.168.106.64", 12345))  # IP del servidor

        # Enviar el nombre al servidor
        cliente_socket.send(nombre_usuario.encode())

        # Crear la ventana de la interfaz gráfica
        ventana_chat = tk.Tk()
        ventana_chat.title(f"Chat - {nombre_usuario}")

        # Área de texto donde se mostrarán los mensajes
        texto = scrolledtext.ScrolledText(ventana_chat, width=50, height=20, wrap=tk.WORD, state=tk.DISABLED)
        texto.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Panel lateral para mostrar las salas activas
        panel_salas = Listbox(ventana_chat, width=20, height=20)
        panel_salas.grid(row=0, column=2, padx=10, pady=10, sticky="ns")

        # Función para cambiar de sala cuando el usuario selecciona una sala en el Listbox
        def cambiar_sala(event):
            seleccion = panel_salas.curselection()
            if seleccion:
                sala_seleccionada = panel_salas.get(seleccion[0])
                cliente_socket.send(f"/cambiar {sala_seleccionada}".encode())

        # Vincular el evento de selección en el Listbox
        panel_salas.bind('<<ListboxSelect>>', cambiar_sala)

        # Campo de entrada de texto
        entrada_mensaje = tk.Entry(ventana_chat, width=40)
        entrada_mensaje.grid(row=1, column=0, padx=10, pady=10)

        # Botón para enviar el mensaje
        def enviar_mensaje():
            mensaje = entrada_mensaje.get()
            if mensaje:
                texto.config(state=tk.NORMAL)
                texto.insert(tk.END, f"Tú: {mensaje}\n")  # Mostrar el nombre del usuario como "Tú"
                texto.config(state=tk.DISABLED)
                texto.yview(tk.END)
                cliente_socket.send(mensaje.encode())
                entrada_mensaje.delete(0, tk.END)

        boton_enviar = tk.Button(ventana_chat, text="Enviar", command=enviar_mensaje)
        boton_enviar.grid(row=1, column=1, padx=10, pady=10)

        # Función para actualizar el panel de salas
        def actualizar_salas(salas):
            panel_salas.delete(0, tk.END)  # Limpiar la lista actual
            for sala in salas:
                panel_salas.insert(tk.END, sala)  # Agregar cada sala al panel

        # Función para recibir mensajes y actualizar el panel de salas
        def recibir_mensajes():
            while True:
                try:
                    mensaje = cliente_socket.recv(1024).decode()
                    if mensaje:
                        if mensaje.startswith("SALAS:"):  # Si el mensaje es una lista de salas
                            salas = mensaje.split(":")[1].split(",")  # Obtener la lista de salas
                            actualizar_salas(salas)  # Actualizar el panel lateral
                        else:
                            texto.config(state=tk.NORMAL)
                            texto.insert(tk.END, f"{mensaje}\n")  # Mostrar el mensaje recibido
                            texto.config(state=tk.DISABLED)
                            texto.yview(tk.END)
                except:
                    texto.config(state=tk.NORMAL)
                    texto.insert(tk.END, "Conexión con el servidor perdida.\n")
                    texto.config(state=tk.DISABLED)
                    texto.yview(tk.END)
                    break

        # Iniciar un hilo para recibir mensajes
        hilo_recibir = threading.Thread(target=recibir_mensajes, daemon=True)
        hilo_recibir.start()

        # Ejecutar la interfaz gráfica
        ventana_chat.mainloop()

        # Cerrar la conexión cuando la ventana se cierre
        cliente_socket.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")

# Ventana de login
ventana = tk.Tk()
ventana.title("Login")

# Campo de entrada para el nombre
nombre = tk.Entry(ventana, width=40)
nombre.grid(row=1, column=0, padx=10, pady=10)

# Botón para ingresar
boton_ingresar = tk.Button(ventana, text="Ingresar", command=Obtener_nombre)
boton_ingresar.grid(row=1, column=1, padx=10, pady=10)

ventana.mainloop()