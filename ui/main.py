from ast import And
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.gui import Ui_MainWindow
from app.config import Config
from app.table import Table
import mysql.connector

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox# type: ignore

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.pushButton.setStyleSheet("background-color:rgb(255, 146, 114);color:white;border-radius: 5px;")
        self.ui.pushButton_2.setStyleSheet("background-color:rgb(255, 146, 114);color:white;border-radius: 5px;")
        self.ui.textEdit.setEnabled(False)
        # Connecter des signaux aux widgets
        self.ui.pushButton.clicked.connect(self.on_button_click)
        self.ui.pushButton_2.clicked.connect(self.on_table_click)
        
    def on_button_click(self):
       DB_Name= self.ui.lineEdit_4.text().strip()
       User=self.ui.lineEdit_2.text().strip()
       Host=self.ui.lineEdit_5.text().strip()
       pwd=self.ui.lineEdit_3.text().strip()
       
       configuration=Config(User,Host,pwd,DB_Name)
       
       config={
           "user":configuration.user,
           "host":configuration.host,
           "password":configuration.password,
           "database":configuration.databaseName
       }
       try:
            # Essayer de se connecter à la base de données
            connection = mysql.connector.connect(**config)
            if connection.is_connected() and self.ui.lineEdit_2.text()!="" and self.ui.lineEdit_4.text() !="" and self.ui.lineEdit_5.text()!="":
                self.ui.textEdit.setStyleSheet("color: green;")
                self.ui.textEdit.setText(
                    f"Connexion réussie !\nUtilisateur : {configuration.user}\n"
                    f"Hôte : {configuration.host}\nBase de données : {configuration.databaseName}"
                )
                self.ui.lineEdit_2.setEnabled(False)
                self.ui.lineEdit_3.setEnabled(False)
                self.ui.lineEdit_4.setEnabled(False)
                self.ui.lineEdit_5.setEnabled(False)
                self.ui.pushButton.setEnabled(False)
                self.ui.pushButton.setStyleSheet("background-color: red; color: white; border-radius: 5px;")

            else:
                self.ui.textEdit.setStyleSheet("color: red;")
                self.ui.textEdit.setText(f"Seul le champ password peut être vide" ) if self.ui.lineEdit_4.text()=="" else self.ui.textEdit.setText(f"Seul le champ password peut être vide" )
                self.ui.textEdit.setText(f" Seul le champ password peut être vide" ) if self.ui.lineEdit_5.text()=="" else self.ui.textEdit.setText(f" Seul le champ password peut être vide" )
                self.ui.textEdit.setText(f"Seul le champ password peut être vide" ) if self.ui.lineEdit_2.text()=="" else self.ui.textEdit.setText(f"Seul le champ password peut être vide" )
       except mysql.connector.Error as err:
            # Gérer les erreurs de connexion
            self.ui.textEdit.setStyleSheet("color: red;")
            self.ui.textEdit.setText(f"Échec de connexion à la base de données :\n{err}")
            
            if err.errno == 1049:  # Erreur : Base de données inconnue
                # Demander à l'utilisateur s'il veut créer la base de données
                reply = QMessageBox.question(self, 'Base de données manquante',
                                            f"La base de données '{configuration.databaseName}' n'existe pas.\n"
                                            "Voulez-vous la créer ?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) # type: ignore

                if reply == QMessageBox.StandardButton.Yes: # type: ignore
                    try:
                        # Se reconnecter sans spécifier de base de données
                        connection = mysql.connector.connect(
                            user=configuration.user,
                            host=configuration.host,
                            password=configuration.password
                        )
                        
                        cursor = connection.cursor()
                        query = f"CREATE DATABASE `{configuration.databaseName}`"
                        cursor.execute(query)
                        connection.commit()
                        
                        self.ui.textEdit.setStyleSheet("color: green;")
                        self.ui.textEdit.append(f"Base de données '{configuration.databaseName}' créée avec succès.")
                    
                    except mysql.connector.Error as create_err:
                        self.ui.textEdit.setStyleSheet("color: red;")
                        self.ui.textEdit.append(f"Impossible de créer la base de données :\n{create_err}")
                    
                    finally:
                        if connection.is_connected(): # type: ignore
                            cursor.close() # type: ignore
                            connection.close() # type: ignore
                else:
                    self.ui.textEdit.setStyleSheet("color: yellow;")
                    self.ui.textEdit.append("L'utilisateur a choisi de ne pas créer la base de données.")
        
    def on_table_click(self):
        
        table_name = self.ui.lineEdit_6.text().strip()
        champ = self.ui.plainTextEdit.toPlainText().strip()
        
        DB_Name = self.ui.lineEdit_4.text().strip()
        User = self.ui.lineEdit_2.text().strip()
        Host = self.ui.lineEdit_5.text().strip()
        pwd = self.ui.lineEdit_3.text().strip()
            
        """_summary_
            create object
        """
        configuration = Config(User, Host, pwd, DB_Name)
        table=Table(table_name,champ)
            
        config = {
            "user": configuration.user,
            "host": configuration.host,
            "password": configuration.password,
            "database": configuration.databaseName
        }
        
        if not table_name or not champ:
            self.ui.textEdit.setStyleSheet("color: red;")
            self.ui.textEdit.setText("Le nom de la table et les champs ne peuvent pas être vides.")
            return
        
        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            
            # Construire la requête SQL en évitant les injections
            create_table_query = f"CREATE TABLE `{table.name}` ({table.champ})"
            
            cursor.execute(create_table_query)
            connection.commit()
            
            self.ui.textEdit.setStyleSheet("color: green;")
            
            self.ui.textEdit.setText(f"La table '{table.name}' a été créée avec succès.")
            self.ui.lineEdit_6.setText("")
            self.ui.plainTextEdit.setPlainText("")
            
        except mysql.connector.Error as err:
           self.ui.textEdit.setStyleSheet("color: red;")
           self.ui.textEdit.setText(f"Erreur lors de la création de la table :\n{err}")

        finally:
            if 'connection' in locals() and connection.is_connected(): # type: ignore
                cursor.close() # type: ignore
                connection.close() # type: ignore


if __name__=="__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
