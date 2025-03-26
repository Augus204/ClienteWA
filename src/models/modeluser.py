import pymysql.cursors
from .user import User

class ModelUser():
    ## Inicializar la clase Modeluser con las credenciales de la base de datos
    def __init__(self):
        self.conection = pymysql.connect(
            host='localhost',
            user='Maxwell',
            password='123456',
            database='whatsapp_client')
        # cursorclass=pymysql.cursors.DictCursor)

    ## Desconexión con la base de datos
    def close_connection(self):
        if self.conection:
            self.conection.close()


    # @classmethod
    def login(self, user):
        try:
            with self.conection.cursor() as cursor:
                sql = "SELECT id, username, password, role FROM users WHERE username = %s"
                cursor.execute(sql, (user.username,))
                row = cursor.fetchone()

            if row != None:
                value = row[2] == user.password
                user = User(row[0], row[1], value, row[3])
                return user
            else:
                return None
            
        except Exception as ex:
            raise Exception(ex)

    # @classmethod
    def get_by_id(self, id):
        try:
            with self.conection.cursor() as cursor:
                sql = "SELECT id, username, role FROM users WHERE id = %s"
                cursor.execute(sql, (id, ))
                row = cursor.fetchone()

            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
            
        except Exception as ex:
            raise Exception(ex)
        
    ## Funcion para ingresar los mensajes recibidos por la aplicación de WhatsApp
    def insert_db(self, message): ## Funcion en revision
        try:
            if message['isGroup'] == 0:
                with self.conection.cursor() as cursor:
                    sql = "INSERT  messages(sender, message, message_type, isGroup, groupParticipant) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, ('Chat privado', message['message'], 'text' , message['isGroup'], message['sender']))
                    self.conection.commit()

            else:
                with self.conection.cursor() as cursor:
                    sql = "INSERT  messages(sender, message, message_type, isGroup, groupParticipant) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (message['sender'], message['message'], 'text' , message['isGroup'], message['groupParticipant']))
                    self.conection.commit()
                        
        except Exception as ex:
            self.conection.rollback()
            raise Exception(ex)
        
    ## Funcion para ingresar a clientes a la base de datos
    def insert_client(self, form): ## Funcion en revision 
        try:
            with self.conection.cursor() as cursor:
                sql = "INSERT  clients(name, celphone, nick, user_type) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (form['nameClient'], form['numClient'], form['nickClient'], form['typeClient']))
                self.conection.commit()
                        
        except Exception as ex:
            self.conection.rollback()
            raise Exception(ex)
        
    ## Funcion para obtener los datos para la tabla de mensajes
    def get_data_table(self):
        try:
            with self.conection.cursor() as cursor:
                # if data:                   
                # messages.groupParticipant
                # if filter:
                # WHERE messages.status = 'Unread' 
                sql = """
                    SELECT messages.id, messages.sender, messages.message, clients.name , DATE_FORMAT(messages.uploaded_at, '%d/%m/%Y %H:%i'), messages.status
                    FROM messages
                    INNER JOIN clients
                    
                    ON REPLACE(REPLACE(REPLACE(REPLACE(messages.groupParticipant, ' ', ''), '+', ''), '-', ''), '(', '') 
                    LIKE CONCAT('%', REPLACE(REPLACE(REPLACE(REPLACE(clients.celphone, ' ', ''), '+', ''), '-', ''), '(', ''), '%')
                    OR messages.groupParticipant = clients.nick
                    ORDER BY messages.uploaded_at DESC
                """
                # ON messages.groupParticipant = clients.celphone
                cursor.execute(sql)
                rows = cursor.fetchall()
          
            if rows != None:
                return [{"id": row[0], "grupo": row[1], "mensaje": row[2], "cliente": row[3], "fecha": row[4], "estado": row[5]} for row in rows]
            else:
                return None
            
        except Exception as ex:
            raise Exception(ex)
        
    def prueba_filtros(self, filter):
        filtros = []
        parametros = {}
        sql_base = """
                    FROM messages
                    INNER JOIN clients
                    ON ( REPLACE(REPLACE(REPLACE(REPLACE(messages.groupParticipant, ' ', ''), '+', ''), '-', ''), '(', '') 
                    LIKE CONCAT('%%', REPLACE(REPLACE(REPLACE(REPLACE(clients.celphone, ' ', ''), '+', ''), '-', ''), '(', ''), '%%')
                    OR messages.groupParticipant = clients.nick ) 
                """

        if filter.get("first_date"):
            filtros.append("messages.uploaded_at >= %s")
            parametros["first_date"] = f"{filter['first_date']} 00:00:00"

        if filter.get("last_date"):
            filtros.append("messages.uploaded_at <= %s")
            parametros["last_date"] = f"{filter['last_date']} 23:59:59"

        if filter.get("client"):
            filtros.append("clients.name = %s")
            parametros["client"] = filter["client"]

        if filter.get("status"):
            filtros.append("messages.status = %s")
            parametros["status"] = filter["status"]

        if filtros:
            sql_base = "SELECT messages.id, messages.sender, messages.message, clients.name , DATE_FORMAT(messages.uploaded_at, '%%d/%%m/%%Y %%H:%%i') , messages.status" + sql_base + ' WHERE ' + ' AND '.join(filtros)
        else:
            sql_base = "SELECT messages.id, messages.sender, messages.message, clients.name , DATE_FORMAT(messages.uploaded_at, '%d/%m/%Y %H:%i') , messages.status" + sql_base

        sql_base += " ORDER BY messages.uploaded_at DESC"
        
        # print(filter)
        # print(sql_base)
        # print(tuple(parametros.values()))
            
        try:
            with self.conection.cursor() as cursor:
                if parametros:
                    cursor.execute(sql_base, tuple(parametros.values()))
                else:
                    cursor.execute(sql_base)

                rows = cursor.fetchall()
          
            if rows != None:
                return [{"id": row[0], "grupo": row[1], "mensaje": row[2], "cliente": row[3], "fecha": row[4], "estado": row[5]} for row in rows]
            else:
                return None
            
        except Exception as ex:
            raise Exception(ex)
                
        
    ## Funcion para obtener los datos para la tabla de clientes
    def get_client_table(self):
        try:
            with self.conection.cursor() as cursor:
            # messages.groupParticipant
                sql = "SELECT id, name, celphone, user_type FROM clients"
                cursor.execute(sql)
                rows = cursor.fetchall()
            
            if rows != None:
                return [{"id": row[0], "nombre": row[1], "numero": row[2], "tipo": row[3]} for row in rows]
            else:
                return None
            
        except Exception as ex:
            raise Exception(ex)

    ## Funcion para obtener solo a los clientes registrados 
    def get_clients(self):
        try:
            with self.conection.cursor() as cursor:
                sql = "SELECT id, name FROM clients"
                cursor.execute(sql)
                rows = cursor.fetchall()
            
            if rows != None:
                return rows
            else:
                return None
            
        except Exception as ex:
            raise Exception(ex)
    
    ## Funcion para actualizar el estado de los mensajes revisados
    def update_data(self, id):
        try:
            with self.conection.cursor() as cursor:
                sql = "UPDATE messages SET status = 'Read' WHERE id = %s;"
                cursor.execute(sql, (id,))
                self.conection.commit()

        except Exception as ex:
            self.conection.rollback()
            raise Exception(ex)