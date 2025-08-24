import os
from dotenv import load_dotenv
from decimal import Decimal
import sqlobject as SO # type: ignore
import requests # type: ignore
load_dotenv()

database = os.getenv("DATABASE_URL")
__connection__ = SO.connectionForURI(database)

class User(SO.SQLObject):
    username = SO.StringCol(length=40, varchar=True, unique=True)
    password = SO.StringCol(length=100, varchar=False)

class Saldo(SO.SQLObject):
    user = SO.ForeignKey('User')
    moneda = SO.StringCol(length=10, dbName="Moneda")
    saldo = SO.StringCol(length=40, default="0", dbName="Saldo")

def newUser(p_username, p_password):
    try:
        user = User.selectBy(username=p_username).getOne()
    except SO.SQLObjectNotFound:
        user = User(username=p_username, password=p_password)
    return user

# Saldo.dropTable(ifExists=True)
# User.dropTable(ifExists=True)
# User.createTable()
# Saldo.createTable()

if not User.tableExists():
    User.createTable()
if not Saldo.tableExists():
    Saldo.createTable()

def cargar_users():
    return [
        {
            "username": u.username,
            "password": u.password
        }
        for u in User.select()
    ]

def guardar_user(usuarios):
    Saldo.deleteMany(None)
    User.deleteMany(None)
    for u in usuarios:
        User(username=u["username"], password=u["password"])

def guardar_cuentas(username, data):
    try:
        user = User.selectBy(username=username).getOne()
    except SO.SQLObjectNotFound:
        return
    for s in Saldo.selectBy(user=user):
        s.destroySelf()
    for moneda, saldo in data.items():
        if moneda != "username":
            Saldo(user=user, moneda=moneda, saldo=saldo)

def cargar_cuentas(username):
    try:
        user = User.selectBy(username=username).getOne()
    except SO.SQLObjectNotFound:
        return None
    cuentas = {"username": username}
    for s in Saldo.selectBy(user=user):
        cuentas[s.moneda] = s.saldo
    return cuentas

# Revisa si el usuario tiene la cuenta para la moneda
def tiene_cuenta_moneda(username, moneda):
    cuentas = cargar_cuentas(username)
    if cuentas is None:
        return False
    return moneda in cuentas

# Crea una nueva cuenta de monedas
def crear_cuenta(username, moneda, saldo_inicial="0"):
    if tiene_cuenta_moneda(username, moneda):
        return False
    
    cuentas = cargar_cuentas(username)
    if cuentas is None:
        return False
    
    cuentas[moneda] = saldo_inicial
    guardar_cuentas(username, cuentas)
    return True

# Obtiene todas las monedas que tiene un usuario
def obtener_monedas_usuario(username):
    cuentas = cargar_cuentas(username)
    if cuentas is None:
        return []
    return [moneda for moneda in cuentas.keys() if moneda != "username"]

# Usa la API de CurrencyFreaks con la apikey
def get_conversion_rate(base: str, target: str) -> Decimal | None:
    try:
        response = requests.get(
            "https://api.currencyfreaks.com/latest",
            params={
                "apikey": os.getenv("API_KEY"), 
                "symbols": f"{base},{target}"
            }
        )
        data = response.json()
        rate_base = Decimal(data["rates"][base])
        rate_target = Decimal(data["rates"][target])
        return rate_target / rate_base
    except Exception:
        return None

# DATA EN JSON
# import json
# import os

# # Crea los directorios necesarios si no existen
# def crear_directorios():
#     if not os.path.exists("./data/usuarios"):
#         os.makedirs("./data/usuarios")

# # Carga los usuarios desde users.json
# def cargar_users():
#     if not os.path.exists("./data/users.json"):
#         return []
#     with open("./data/users.json", "r") as f:
#         return json.load(f)["users"]

# # Guarda los usuarios con sus contraseñas hasheadas en users.json
# def guardar_user(usuarios):
#     crear_directorios()
#     with open("./data/users.json", "w") as f:
#         json.dump({"users": usuarios}, f, indent=4)

# # Guarda los usuarios con sus saldos en un json individual en /usuarios/
# def guardar_cuentas(username, data):
#     crear_directorios()
#     ruta = f"./data/usuarios/{username}.json"
#     with open(ruta, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)

# # Carga los saldos de un usuario desde su json individual en /usuarios/
# def cargar_cuentas(username):
#     ruta = f"./data/usuarios/{username}.json"
#     if os.path.exists(ruta):
#         with open(ruta, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return None

# # Obtiene la tasa de conversión entre dos monedas
# def get_conversion_rate(base: str, target: str) -> Decimal | None:
#     try:
#         response = requests.get(
#             "https://api.currencyfreaks.com/latest",
#             params={
#                 "apikey": "8acfe8496aec4da09f0e0fd36bf87396", 
#                 "symbols": f"{base},{target}"
#             }
#         )
#         data = response.json()
#         rate_base = Decimal(data["rates"][base])
#         rate_target = Decimal(data["rates"][target])
#         return rate_target / rate_base
#     except Exception as e:
#         print(f"\033[31mHubo un error al obtener la cotización:\033[0m {e}")
#         return None

# # Verifica si un usuario tiene cuenta en una moneda específica
# def tiene_cuenta_moneda(username, moneda):
#     user_cuentas = cargar_cuentas(username)
#     if user_cuentas is None:
#         return False
#     return moneda in user_cuentas

# # Crea una nueva cuenta de moneda para un usuario
# def crear_cuenta(username, moneda):
#     user_cuentas = cargar_cuentas(username)
#     # Verifica si el usuario existe
#     if user_cuentas is None:
#         return False, "usuario_no_encontrado"
#     # Verifica si ya tiene cuenta en esa moneda
#     if moneda in user_cuentas:
#         return False, "cuenta_existente"
    
#     # Crea la nueva cuenta con saldo 0
#     user_cuentas[moneda] = "0"
#     guardar_cuentas(username, user_cuentas)
#     return True, "ok"