import pyodbc
import os
import logging

class DatabaseConnection:
    """Classe para gerenciar conexão com SQL Server"""
    
    def __init__(self):
        # Configuração de conexão com SQL Server
        self.server = os.getenv('SQL_SERVER', '192.168.100.230')
        self.database = os.getenv('SQL_DATABASE', 'Sorteio_qz')
        self.username = os.getenv('SQL_USERNAME', 'sa')
        self.password = os.getenv('SQL_PASSWORD', '1820')
        self.connection = None
    
    def connect(self):
        """Estabelecer conexão com SQL Server"""
        try:
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
            self.connection = pyodbc.connect(connection_string)
            logging.info("Conexão com SQL Server estabelecida com sucesso")
            return True
        except Exception as e:
            logging.warning(f"Erro ao conectar com SQL Server: {e}")
            return False
    
    def execute_select(self, query, params=None):
        """Executar query SELECT"""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                logging.warning("Não há conexão ativa com o banco de dados")
                return []
        except Exception as e:
            logging.error(f"Erro ao executar SELECT: {e}")
            return []
    
    def execute_insert_update_delete(self, query, params=None):
        """Executar query INSERT, UPDATE ou DELETE"""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                self.connection.commit()
                cursor.close()
                return True
            else:
                logging.warning("Não há conexão ativa com o banco de dados")
                return False
        except Exception as e:
            logging.error(f"Erro ao executar modificação: {e}")
            return False
    
    def close(self):
        """Fechar conexão"""
        if self.connection:
            self.connection.close()
            logging.info("Conexão com SQL Server fechada")

# Instância global da conexão
db = DatabaseConnection()