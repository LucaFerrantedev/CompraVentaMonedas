import os
from dotenv import load_dotenv # type: ignore
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

# Obtiene todas las monedas disponibles desde la API
def monedas_api():
    """Obtiene todas las monedas disponibles desde la API de CurrencyFreaks."""
    try:
        response = requests.get(
            "https://api.currencyfreaks.com/latest",
            params={"apikey": os.getenv("API_KEY")}
        )
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        data = response.json()
        if "rates" in data:
            return sorted(list(data["rates"].keys())) # Devuelve la lista ordenada
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar la API de monedas: {e}")
        return None


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