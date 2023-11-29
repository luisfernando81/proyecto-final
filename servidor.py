import socket
import threading
import serial
import time

# Configuración del servidor
SERVER_IP = '192.168.68.192'
SERVER_PORT = 12345

# Configuración del puerto serial
SERIAL_PORT = 'COM10'
ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)

# Variable global para la conexión con Arduino
arduino_lock = threading.Lock()
arduino_connected = False

# Función para manejar la conexión con Arduino
def handle_arduino_connection():
    global arduino_connected
    while True:
        try:
            with arduino_lock:
                ser.write(b'1')  # Enviar comando para mantener la conexión
                time.sleep(1)
            arduino_connected = True
        except serial.SerialException:
            arduino_connected = False
            time.sleep(2)

# Iniciar el hilo para manejar la conexión con Arduino
arduino_thread = threading.Thread(target=handle_arduino_connection)
arduino_thread.daemon = True
arduino_thread.start()

# Función para manejar la conexión con el cliente
def handle_client(client_socket):
    global arduino_connected

    while True:
        command = client_socket.recv(1024).decode('utf-8')
        
        if not command:
            break

        if arduino_connected:
            with arduino_lock:
                ser.write(command.encode('utf-8'))  # Enviar comando al Arduino
                response = ser.readline().decode('utf-8').strip()
                client_socket.send(response.encode('utf-8'))
        else:
            client_socket.send(b'Arduino not connected')

# Configurar el servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

print(f"Servidor escuchando en {SERVER_IP}:{SERVER_PORT}")

# Aceptar conexiones entrantes
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Conexión aceptada desde {client_address}")

    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.daemon = True
    client_handler.start()
v