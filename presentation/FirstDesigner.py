from business.business import registrar_usuario, iniciar_sesion, ingresar_ars, crear_cuenta, comprar_extranjera, vender_extranjera, consultar_saldos
from business.business import password_asteriscos, password_coincide, password_invalida, usuario_invalido
from PyQt6.QtWidgets import QApplication,QMainWindow,QPushButton,QLineEdit,QLabel, QTableWidgetItem, QDialog, QMessageBox
from PyQt6.QtCore import Qt
import sys
from presentation.screens.Login_ui import Ui_LoginWindow
from presentation.screens.Main_ui import Ui_MainWindow
from presentation.screens.dialogRegister_ui import Ui_dialogRegister
from PyQt6.QtGui import QKeySequence

class LoginWindow(QMainWindow, Ui_LoginWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnRegister.clicked.connect(self.btnRegisterClick)
        self.btnLogin.clicked.connect(self.btnLoginClick)
        self.show()

    def btnRegisterClick(self):
        self.dialogo = dialogRegister()
        res = self.dialogo.exec()

        if res == QDialog.DialogCode.Accepted:
            try:
                username = self.dialogo.lineditUser.text()
                password = self.dialogo.lineditPass.text()
                password2 = self.dialogo.lineditPassConfirm.text()

                if not usuario_invalido(username):
                    print(QMessageBox.critical(self, "Informacion", "Usuario invalido"))
                    print("\033[31m❌ Usuario invalido.\033[0m")
                    return
                if not password_invalida(password):
                    print(QMessageBox.critical(self, "Informacion", "La contraseña no puede estar vacía ni contener espacios"))
                    return
                if not password_invalida(password2):
                    print(QMessageBox.critical(self, "Informacion", "La contraseña no puede estar vacía ni contener espacios"))
                    return
                if not password_coincide(password, password2):
                    print(QMessageBox.critical(self, "Informacion", "Las contraseñas no coinciden"))
                    return

                exito, motivo = registrar_usuario(username, password, password2)
                if exito:
                    print(QMessageBox.information(self, "Bienvenido", "Registrado correctamente."))
                else:
                    if motivo == "usuario_existente":
                        print(QMessageBox.critical(self, "Informacion", "Ya existe ese usuario."))
                    elif motivo == "password_no_coincide":
                        print(QMessageBox.critical(self, "Informacion", "Las contraseñas no coinciden."))
                    else:
                        print(QMessageBox.critical(self, "Informacion", "No se pudo registrar el usuario."))
            except Exception as e:
                print("Error al obtener los datos del diálogo de registro:", e)
        else:
            print(QMessageBox.critical(self, "Informacion", "Registro cancelado."))
    
    def btnLoginClick(self):
        username = self.lineditUser.text()
        password = self.lineditPass.text()
        exito, motivo = iniciar_sesion(username, password)
        try:
            if not usuario_invalido(username):
                print(QMessageBox.critical(self, "Informacion", "Usuario invalido"))
                return
            if exito:
                print(QMessageBox.information(self, "Bienvenido", "Inicio de sesión exitoso."))
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else:
                if motivo == "usuario_no_encontrado":
                    print(QMessageBox.critical(self, "Informacion", "Usuario no encontrado"))
                elif motivo == "password_incorrecta":
                    print(QMessageBox.critical(self, "Informacion", "Contraseña incorrecta"))
                else:
                    print(QMessageBox.critical(self, "Informacion", "No se pudo iniciar sesión"))
        except Exception as e:
            print("Error al iniciar sesión:", e)

# Diálogo de registro (se accede desde el botón Registrar en VentanaPrincipal)
class dialogRegister(QDialog, Ui_dialogRegister):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    ventana = LoginWindow()
    sys.exit(app.exec())