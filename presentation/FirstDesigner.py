from business.business import (registrar_usuario, iniciar_sesion, ingresar_ars, comprar_extranjera, 
                               vender_extranjera, consultar_saldos, password_coincide, password_invalida, 
                               usuario_invalido, monedas_disponibles, crear_cuenta_usuario)

from PyQt6.QtWidgets import QApplication,QMainWindow,QPushButton,QLineEdit,QLabel, QTableWidgetItem, QDialog, QMessageBox, QAbstractItemView,QListView
from PyQt6.QtCore import Qt, QStringListModel, QTimer
import sys
from presentation.screens.Login_ui import Ui_LoginWindow
from presentation.screens.Main_ui import Ui_MainWindow
from presentation.screens.dialogRegister_ui import Ui_dialogRegister
from presentation.screens.dialogIngresarARS_ui import Ui_dialogIngresarARS
from presentation.screens.dialogCrearCuenta_ui import Ui_dialogCrearCuenta
from PyQt6.QtGui import QKeySequence

# Ventana de login (primera ventana que se muestra)
class LoginWindow(QMainWindow, Ui_LoginWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lineditPass.setEchoMode(QLineEdit.EchoMode.Password)  # Oculta con asteriscos
        self.btnRegister.clicked.connect(self.btnRegisterClick)
        self.btnLogin.clicked.connect(self.btnLoginClick)
        self.username = "" # Para pasar el nombre de usuario a la ventana principal
        self.show()

    # Lógica del botón Registrar
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
    
    # Lógica del botón Iniciar Sesión
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
                self.username = username
                self.main_window = MainWindow(self.username)
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
        # Oculta con asteriscos
        self.lineditPass.setEchoMode(QLineEdit.EchoMode.Password)
        self.lineditPassConfirm.setEchoMode(QLineEdit.EchoMode.Password)

# Diálogo para ingresar ARS
class dialogIngresarARS(QDialog, Ui_dialogIngresarARS):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

# Diálogo para crear cuenta de moneda
class dialogCrearCuenta(QDialog, Ui_dialogCrearCuenta):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Obtenemos las monedas desde la capa de negocio
        monedas = monedas_disponibles()
        if monedas:
            self.comboxMoneda.addItems(monedas)
        else:
            QMessageBox.warning(self, "Error", "No se pudieron cargar las monedas disponibles.")

# Ventana principal (se accede si se logra iniciar sesión)
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, username):
        super().__init__()
        self.setupUi(self)
        self.username = username
        self.setWindowTitle(f"Operaciones - {self.username}")
        self.btnIngresarARS.clicked.connect(self.btnIngresarARSClick)
        self.btnCrearCuenta.clicked.connect(self.btnCrearCuentaClick)
        self.btnComprar.clicked.connect(self.btnComprarClick)
        self.btnVender.clicked.connect(self.btnVenderClick)
        self.listviewMonedas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Hace que la lista no sea editable
        self.actualizar_saldos_y_monedas() # Carga inicial de saldos y monedas
        self.show()

    def actualizar_saldos_y_monedas(self):
        self.actualizar_saldos_listview()
        self.actualizar_monedas_combobox()

    def actualizar_saldos_listview(self):
        saldos = consultar_saldos(self.username)
        if saldos:
            # Formateamos cada línea para mostrar moneda y saldo
            items_lista = [f"{moneda}: {saldo}" for moneda, saldo in saldos.items()]
            # Usamos un QStringListModel para manejar los datos de la lista
            modelo = QStringListModel(items_lista)
            self.listviewMonedas.setModel(modelo)
        else:
            # Si no hay saldos, limpiamos la lista
            self.listviewMonedas.setModel(QStringListModel([]))

    def actualizar_monedas_combobox(self):
        saldos = consultar_saldos(self.username)
        self.comboxMoneda.clear()
        if saldos:
            # Añadimos todas las monedas que no sean ARS al combobox
            monedas_usuario = [moneda for moneda in saldos.keys() if moneda != "ARS"]
            self.comboxMoneda.addItems(monedas_usuario)

    def btnCrearCuentaClick(self):
        dialogo = dialogCrearCuenta()
        res = dialogo.exec()

        if res == QDialog.DialogCode.Accepted:
            moneda_seleccionada = dialogo.comboxMoneda.currentText()
            exito = crear_cuenta_usuario(self.username, moneda_seleccionada)

            if exito:
                QMessageBox.information(self, "Éxito", f"Cuenta para {moneda_seleccionada} creada correctamente.")
                self.actualizar_saldos_y_monedas() # Actualizamos la UI
            else:
                QMessageBox.warning(self, "Atención", f"Ya tienes una cuenta para {moneda_seleccionada} o ocurrió un error.")
        else:
            QMessageBox.information(self, "Cancelado", "La operación fue cancelada.")
    
    # Lógica del botón Ingresar ARS
    def btnIngresarARSClick(self):
        dialogo = dialogIngresarARS()
        res = dialogo.exec()
        
        if res == QDialog.DialogCode.Accepted:
            cantidad = dialogo.lineditARS.text()
            exito, motivo = ingresar_ars(self.username, cantidad)
            if exito:
                QMessageBox.information(self, "Éxito", "Ingreso realizado correctamente.")
                self.actualizar_saldos_y_monedas() # Actualizamos la UI
            else:
                mensaje = "No se pudo realizar el ingreso."
                if motivo == "cantidad_invalida":
                    mensaje = "La cantidad debe ser un número mayor que cero."
                elif motivo == "monto_invalido":
                    mensaje = "Por favor, ingrese un monto numérico válido."
                QMessageBox.warning(self, "Error", mensaje)
        else:
            QMessageBox.information(self, "Cancelado", "La operación fue cancelada.")
            
    def btnComprarClick(self):
        moneda = self.comboxMoneda.currentText()
        cantidad = self.lineditCantidad.text()

        if not moneda:
            QMessageBox.warning(self, "Atención", "No has seleccionado ninguna moneda para comprar.")
            return

        # Diálogo de confirmación
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar Compra")
        msg_box.setText(f"¿Confirmas la compra de {moneda} utilizando {cantidad} ARS?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Timer para cancelar automáticamente después de 2 minutos (120000 ms)
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(msg_box.reject)
        timer.start(120000)

        reply = msg_box.exec()
        timer.stop()

        if reply == QMessageBox.StandardButton.Yes:
            exito, resultado = comprar_extranjera(self.username, cantidad, moneda)
            if exito:
                QMessageBox.information(self, "Compra Exitosa", f"Has comprado {resultado} {moneda}.")
                self.actualizar_saldos_y_monedas()
            else:
                # Mensajes de error segun el motivo
                mensajes_error = {
                    "cantidad_invalida": "La cantidad debe ser un número mayor que cero.",
                    "monto_invalido": "Por favor, ingrese un monto numérico válido.",
                    "sin_ars": "No tienes una cuenta en ARS para realizar la compra.",
                    "sin_tasa": "No se pudo obtener la tasa de conversión. Intente más tarde.",
                    "saldo_insuficiente": "No tienes suficiente saldo en ARS para esta compra.",
                    "sin_cuenta_moneda": f"No tienes una cuenta de {moneda} para comprar. Créala primero."
                }
                mensaje = mensajes_error.get(resultado, "Ocurrió un error inesperado al intentar comprar.")
                QMessageBox.critical(self, "Error en la Compra", mensaje)
        else:
            QMessageBox.information(self, "Operación Cancelada", "La compra ha sido cancelada.")

    def btnVenderClick(self):
        moneda = self.comboxMoneda.currentText()
        cantidad = self.lineditCantidad.text()

        if not moneda:
            QMessageBox.warning(self, "Atención", "No has seleccionado ninguna moneda para vender.")
            return

        # Diálogo de confirmación
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar Venta")
        msg_box.setText(f"¿Confirmas la venta de {cantidad} {moneda}?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(msg_box.reject)
        timer.start(120000)

        reply = msg_box.exec()
        timer.stop()

        if reply == QMessageBox.StandardButton.Yes:
            exito, resultado = vender_extranjera(self.username, cantidad, moneda)
            if exito:
                QMessageBox.information(self, "Venta Exitosa", f"Has recibido {resultado} ARS.")
                self.actualizar_saldos_y_monedas()
            else:
                mensajes_error = {
                    "cantidad_invalida": "La cantidad debe ser un número mayor que cero.",
                    "monto_invalido": "Por favor, ingrese un monto numérico válido.",
                    "saldo_insuficiente": f"No tienes suficiente saldo en {moneda} para vender.",
                    "sin_tasa": "No se pudo obtener la tasa de conversión. Intente más tarde."
                }
                mensaje = mensajes_error.get(resultado, "Ocurrió un error inesperado al intentar vender.")
                QMessageBox.critical(self, "Error en la Venta", mensaje)
        else:
            QMessageBox.information(self, "Operación Cancelada", "La venta ha sido cancelada.")

if __name__ == '__main__':
    app = QApplication([])
    ventana = LoginWindow()
    sys.exit(app.exec())