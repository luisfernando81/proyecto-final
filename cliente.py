import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket
import threading
import time

# Configuración del cliente
SERVER_IP = '192.168.68.192'
SERVER_PORT = 12345

# Crear la ventana principal
window = tk.Tk()
window.title("Cliente")

# Crear un widget de pestañas
tab_control = ttk.Notebook(window)

# Pestaña 1: Control de Motor
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Control de Motor")

# Etiqueta para mostrar la velocidad actual
speed_label = tk.Label(tab1, text="Velocidad actual: ")
speed_label.pack()

# Variable para almacenar la velocidad actual
current_speed = tk.StringVar()
current_speed.set("0")

# Etiqueta que muestra la velocidad actual
current_speed_label = tk.Label(tab1, textvariable=current_speed)
current_speed_label.pack()



# Botones para controlar el motor
start_motor_button = tk.Button(tab1, text="Encender Motor", command=lambda: send_command('start_motor'))
start_motor_button.pack()

increase_speed_button = tk.Button(tab1, text="Aumentar Velocidad", command=lambda: send_command('increase_speed'))
increase_speed_button.pack()

stop_motor_button = tk.Button(tab1, text="Detener Motor", command=lambda: send_command('stop_motor'))
stop_motor_button.pack()

# Pestaña 2: Lectura de Sensores cada 4 segundos
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="Lectura de Sensores")

# Etiqueta para mostrar la lectura de sensores
sensor_label = tk.Label(tab2, text="Lectura de Sensores: ")
sensor_label.pack()

# Variable para almacenar la lectura de sensores
current_sensor_reading = tk.StringVar()
current_sensor_reading.set("0")

# Etiqueta que muestra la lectura de sensores
current_sensor_label = tk.Label(tab2, textvariable=current_sensor_reading)
current_sensor_label.pack()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Función para obtener la lectura de sensores del servidor
def get_sensor_reading():
    try:
        while True:
            client_socket.send('get_sensor_reading'.encode('utf-8'))
            sensor_reading = client_socket.recv(1024).decode('utf-8')
            current_sensor_reading.set(sensor_reading)
        
            # (usando ax_sensor.plot() y canvas_sensor.draw())
            time.sleep(4)  # Esperar 4 segundos antes de la próxima lectura
    except socket.error:
        messagebox.showerror('Error', 'Error de conexión con el servidor')

# Hilo para obtener la lectura de sensores en segundo plano
sensor_thread = threading.Thread(target=get_sensor_reading)
sensor_thread.daemon = True
sensor_thread.start()

# Funciones de los botones
def send_command(command):
    try:
        client_socket.send(command.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        # Actualizar la velocidad actual si es necesario
        if command == 'increase_speed':
            update_speed()
    except socket.error:
        messagebox.showerror('Error', 'Error de conexión con el servidor')

# Función para actualizar la velocidad actual
def update_speed():
    client_socket.send('get_speed'.encode('utf-8'))
    speed = client_socket.recv(1024).decode('utf-8')
    current_speed.set(speed)

# Configurar la función de cierre
def close_window():
    client_socket.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", close_window)

# Iniciar la ventana
tab_control.pack(expand=1, fill="both")
window.mainloop()