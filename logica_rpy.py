import socket
import threading
import requests
import time
import json
import queue

# Crear el diccionario con los valores iniciales
data2 = {
    "SKU": "",  # Valor inicial del SKU
    "RFID": ""  # Valor inicial del RFID
}


class Deposito:
    def _init_(self):
        self.conexiones = {
            12: {17: 10, 18: 13, 19: 14, 22: 15, 23: 16, 26: 17, 27: 18, 28: 19},
            18: {25: 16, 27: 12},
            17: {24: 15, 26: 12},
            16: {23: 12, 21: 14, 25: 18},
            15: {20: 13, 22: 12, 24: 17},
            14: {19: 12, 21: 16, 30: 11},
            13: {18: 12, 20: 15, 31: 7},
            11: {15: 9, 16: 10, 30: 14},
            10: {14: 8, 16: 11, 17: 12, 29: 7},
            9: {11: 6, 13: 8, 15: 11},
            8: {10: 5, 12: 7, 13: 9, 14: 10},
            7: {9: 4, 12: 8, 29: 10, 31: 13},
            6: {6: 3, 8: 5, 11: 9},
            5: {5: 2, 7: 4, 8: 6, 10: 8},
            4: {4: 1, 7: 5, 9: 7},
            3: {3: 2, 6: 6},
            2: {2: 1, 3: 3, 5: 5, 1: 20},
            1: {2: 2, 4: 4},
            20: {1: 2},
            19: {28: 12}
        }

    def obtener_zona(self, id_data):
        url = f'http://{ip_pc}:{puerto_pc}/Tesis/BackEnd/clientes/seleccionar.php?id={id_data}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('Zona')
        else:
            print("Error al obtener la información del cliente.")
            return None

    def acceder_a_zona(self, zona_actual, port_data):
        if zona_actual in self.conexiones and port_data in self.conexiones[zona_actual]:
            return self.conexiones[zona_actual][port_data]
        else:
            print("No puedes acceder a esa zona desde aquí.")
            return None

# Crear una cola de mensajes
cola_mensajes = queue.Queue()



def handle_socket_4(client_socket_1):
    try:
        while True:
            # Recibir el array de 2 bytes
            data = client_socket_1.recv(2)
            
            # Verificar si se recibieron 2 bytes completos
            if len(data) == 2:
                # Guardar los bytes en la cola de mensajes
                for byte in data:
                    cola_mensajes.put(byte)
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        print("Error:", e)
    finally:
        # Cerrar el socket cliente
        client_socket_1.close()




def handle_socket_1():
    try:
        while True:
            esta_vacia = cola_mensajes.empty()

            if esta_vacia is not True:
                # Obtener y eliminar un elemento de la cola (número de puerto)
                port_data = cola_mensajes.get()
                print("Número de puerto recibido:", port_data)
                
                # Obtener y eliminar otro elemento de la cola (número de ID)
                id_data = cola_mensajes.get()
                print("Número de ID recibido:", id_data)

                # Aquí sigue el resto de tu lógica para manejar los datos recibidos
                if port_data == 31: # Comparar con '31' como cadena
                    print("DETECTE EL PUERTO31 PERO NO VOY A HACER NADA PORQUE SOY INUTIL")
                    # URL con id_data
                    URL3 = f"http://{ip_pc}:{puerto_pc}/Tesis/BackEnd/clientes/eliminar.php?id={id_data}"
                    try:
                        response = requests.delete(URL3)
                        if response.status_code == 200:
                            print("Producto facturado correctamente.")
                        else:
                            print("Error al eliminar cliente:", response.status_code)
                    except requests.exceptions.RequestException as re:
                        print("Error de conexión HTTP:", re)
                    except Exception as e:
                        print("Error al enviar la solicitud HTTP:", e)

                    
                    
                else:
                    # Obtener la zona actual del cliente
                    zona_actual = deposito.obtener_zona(id_data)
                    if zona_actual is not None:
                        try:
                            # Convertir el número de puerto a entero
                            port_data = int(port_data)
                            # Obtener la nueva zona del cliente
                            nueva_zona = deposito.acceder_a_zona(zona_actual, port_data)
                            if nueva_zona is not None:
                                print(f"Te encuentras ahora en la Zona {nueva_zona}")
                                # Preparar los datos para enviar
                                datos = {"id": id_data, "Zona": nueva_zona}
                                url = f'http://{ip_pc}:{puerto}/Tesis/BackEnd/clientes/editarZona.php'
                                try:
                                    # Enviar los datos al servidor
                                    response = requests.put(url, json=datos)
                                    if response.status_code == 200:
                                        print("Datos enviados correctamente.")
                                    else:
                                        print("Error al enviar datos:", response.status_code)
                                except requests.exceptions.RequestException as re:
                                    print("Error de conexión HTTP:", re)
                        except ValueError:
                            print("El número de puerto debe ser un entero.")
                        except Exception as e:
                            print("Error en el manejo del socket:", e)
    except Exception as e:
        print("Error en el manejo del socket:", e)


def handle_socket_2(server_socket):
    try:
        url = f'http://{ip_pc}:{puerto_pc}/Tesis/BackEnd/clientes/seleccionar.php'

        # Aceptamos la conexión desde el cliente
        client_socket, addr = server_socket.accept()
        print(f"Conexión establecida desde {addr}")

        # Obtener datos iniciales
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  
            for item in data:
                time.sleep(0.2)
                id_cliente = item.get('id')
                client_socket.sendall(str(id_cliente).encode())
                print(f"ID enviado: {id_cliente}")
                time.sleep(0.2)
                zona_cliente = item.get('Zona')
                client_socket.sendall(str(zona_cliente).encode())
                print(f"Zona enviada: {zona_cliente}")
        else:
            print("Error al obtener la respuesta del servidor HTTP:", response.status_code)

        # Bucle principal para manejar actualizaciones
        while True:
            try:
                datos_viejos = hacer_peticion_get()  # Obtener datos iniciales
                time.sleep(5)
                datos_nuevos = hacer_peticion_get()  # Obtener datos nuevos en cada iteración
                
                nuevos_elementos = comparacion(datos_viejos, datos_nuevos)

                if nuevos_elementos:
                    for elemento in nuevos_elementos:
                        # Enviamos los datos al cliente
                        client_socket.sendall(str(elemento).encode())
                        client_socket.sendall(str(19).encode())
                        print("Enviando dato:", elemento)

                datos_viejos = datos_nuevos  # Actualizamos los datos viejos con los nuevos
            except Exception as e:
                print("Error en el manejo del segundo socket:", e)

    except Exception as e:
        print("Error en el manejo del primer socket:", e)
    finally:
        # Cerramos el socket al finalizar
        client_socket.close()

def handle_socket_3():
    barcode_recibido = False
    rfid_recibido = False
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print('Esperando datos...')
    
        while True:
            if not rfid_recibido:
                rfid_data2, addr = s.recvfrom(1024)  # Recibir datos del tamaño máximo de 1024 bytes
                data2["RFID"] = rfid_data2.decode()  # Cambiar el valor del RFID al recibido
                rfid_recibido = True
                print("RFID recibido:", data2["RFID"])

            if not barcode_recibido:
                sku_input = input("Por favor, ingresa el valor del SKU: ")
                data2["SKU"] = sku_input
                barcode_recibido = True
                
            # Verificar si se han recibido ambos datos
            if rfid_recibido and barcode_recibido:
                # Enviar los datos al servidor utilizando una solicitud HTTP POST
                try:
                    response = requests.post(URL2, json=data2)
                    print("Respuesta del servidor:", response.text)
                except Exception as e:
                    print("Error al enviar la solicitud HTTP:", e)
                
                # Reiniciar las banderas para la próxima iteración
                rfid_recibido = False
                barcode_recibido = False



def comparacion(anterior, actual):
    nuevos_elementos = []
    for elemento_actual in actual:
        if elemento_actual not in anterior:
            nuevos_elementos.append(elemento_actual)
    return nuevos_elementos

def hacer_peticion_get():
    # Dirección IP y puerto de la PC
    ip_pc = '192.168.88.254'
    puerto_http = '80'
    urlCAM = f'http://{ip_pc}:{puerto_http}/Tesis/BackEnd/clientes/seleccionar.php'
    
    try:
        # Realizar la solicitud GET
        response = requests.get(urlCAM)
        
        # Verificar si la solicitud fue exitosa (código de respuesta 200)
        if response.status_code == 200:
            # Convertir la respuesta a formato JSON
            data = response.json()
            ids=[]
            for item in data:
                ids.append(item['id'])
            return ids  # Devolver los datos obtenidos
        else:
            print("Error al realizar la solicitud GET:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error en la solicitud GET:", e)
        return None

# Dirección IP y puerto de la PC
ip_pc = '192.168.88.254'
puerto_pc = '80'
puerto = '80'

URL2 = f"http://{ip_pc}:{puerto_pc}/Tesis/BackEnd/clientes2/agregar.php"



# Crear un objeto de la clase Deposito
deposito = Deposito()

# Dirección y puerto para el socket
HOST = '192.168.88.245'  # Cambia esto por la dirección de tu servidor
PORT = 3008  # Cambia esto por el puerto que deseas utilizar

# Configuración del servidor para el primer socket
host_socket_1 = "192.168.88.245"
port_socket_1 = 3000
server_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket_1.bind((host_socket_1, port_socket_1))
    server_socket_1.listen(1)  # Permitir solo una conexión simultánea
    print(f"Servidor escuchando en {host_socket_1}:{port_socket_1}...")
except Exception as e:
    print("Error al iniciar el servidor del primer socket:", e)

# Configuración del servidor para el segundo socket
host_socket = '192.168.88.245'
puerto_socket = 3001
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host_socket, puerto_socket))
server_socket.listen(1)  # Permitir solo una conexión simultánea
print(f"Servidor escuchando en {host_socket}:{puerto_socket}...")

# Iniciar un hilo para manejar el tercer socket
thread_1 = threading.Thread(target=handle_socket_1)
thread_1.start()

# Iniciar un hilo para manejar el segundo socket
thread_2 = threading.Thread(target=handle_socket_2, args=(server_socket,))
thread_2.start()

# Iniciar un hilo para manejar el tercer socket
thread_3 = threading.Thread(target=handle_socket_3)
thread_3.start()

# Iniciar un hilo para manejar el primer socket
thread_4 = threading.Thread(target=handle_socket_4, args=(server_socket_1.accept()[0],))
thread_4.start()

# Esperar a que todos los hilos terminen
thread_1.join()
thread_2.join()
thread_3.join()
thread_4.join()