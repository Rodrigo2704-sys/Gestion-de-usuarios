import mysql.connector 
from mysql.connector import pooling, Error

class GestionUsuarios():
    def __init__(self):
        self.conexion=mysql.connector.mysql(
        host="localhost",
        user="root",
        password="root",
        database="usuarios"
        )

    
 def conectar(self):
        return self.conexion

    def registrar_usuario(self, nombre, correo, edad):
        cursor = self.conexion.cursor(dictionary=True)

        try:
            # Nota la coma al final de (correo,) para que sea una tupla válida
            cursor.execute("SELECT correo FROM usuarios WHERE correo = %s", (correo,))
            resultado = cursor.fetchone()

            if resultado:
                return {"Exito": False, "Mensaje": "El correo ya se encuentra registrado."}

            insert_correo = """INSERT INTO usuarios (nombre, correo, edad) VALUES (%s, %s, %s)"""
            cursor.execute(insert_correo, (nombre, correo, edad))

            self.conexion.commit()
            cursor.close()
            return {"Exito": True, "Mensaje": "¡El usuario se ha registrado con éxito!"}

        except mysql.connector.Error as e:
            return {"Exito": False, "Mensaje": "Hubo un error al intentar registrarse."}

         #Leer (Read): Funciones para consultar la información, ya sea ver la lista completa de todos los usuarios registrados o buscar a uno en específico por su ID o correo.

    def Consultar_por_nombre(self, nombre):
        cursor = self.conexion(dictionary=True)
        try:
            sql = "SELECT * FROM usuarios WHERE nombre = %s"
            cursor.execute(sql, (nombre,))
            resultado = cursor.fetchone()

            if not resultado:
                return {"Exito": False, "Mensaje": "El usuario no se encuentra registrado"}

            return {"Exito": True, "Mensaje": f"Usuario encontrado: {resultado}"}

        except mysql.connector.Error as e:
            return {"Exito": False, "Mensaje": f"Hubo un error al consultar: {e}"}


            #Update (Actualizar): Modificar los datos de un usuario existente.

   def actualizar_datos(self, nuevo_nombre, nuevo_correo, nuevo_telefono, nombre_buscar, correo_buscar):
        cursor = self.conexion(dictionary=True)

        try:
            actu = """UPDATE usuarios SET nombre = %s, correo = %s, telefono = %s WHERE nombre = %s AND correo = %s"""
            
            # El orden de la tupla: primero los 3 valores que se van a actualizar (SET) 
            # y luego los valores de búsqueda (WHERE)
            cursor.execute(actu, (nuevo_nombre, nuevo_correo, nuevo_telefono, nombre_buscar, correo_buscar))

            self.conexion_bd.commit()
            
            if cursor.rowcount == 0:
                cursor.close()
                return {"Exito": False, "Mensaje": "No se encontró ningún usuario con esos datos para actualizar."}

            cursor.close()
            return {"Exito": True, "Mensaje": "Datos actualizados correctamente."}

        except mysql.connector.Error as e:
            cursor.close()
            return {"Exito": False, "Mensaje": f"Error al actualizar los datos: {e}"}






           
    
        

        
    