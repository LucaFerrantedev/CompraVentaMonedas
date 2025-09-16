from PyQt6.QtWidgets import QApplication,QMainWindow,QPushButton,QLineEdit,QLabel, QTableWidgetItem, QDialog
from PyQt6.QtCore import Qt
import sys
from screens.Main_ui import Ui_MainWindow

class VentanaPrincipal(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.BtnAddAccount.clicked.connect(self.BtnCreateAccountClick)
        # for account in accounts.keys():
        #     row = self.AccountTable.rowCount()
        #     self.AccountTable.insertRow(row)
        #     self.AccountTable.setItem(row, 1, QTableWidgetItem(str(accounts[account])))
        #     self.AccountTable.setItem(row, 0, QTableWidgetItem(account))
        self.show()
    
    # def BtnCreateAccountClick(self):
    #     self.dialogo = DialogoCuenta()
    #     res = self.dialogo.exec()
    #     if res == QDialog.DialogCode.Accepted:
    #         row = self.AccountTable.rowCount()
    #         self.AccountTable.insertRow(row)
    #         self.AccountTable.setItem(row, 1, QTableWidgetItem(str("0.00")))
    #         self.AccountTable.setItem(row, 0, QTableWidgetItem(self.dialogo.AccountList.currentText()))
        
# class DialogoCuenta(QDialog, Ui_Dialog):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)

if __name__ == '__main__':
    app = QApplication([])
    ventana = VentanaPrincipal()
    sys.exit(app.exec())