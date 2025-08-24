from decimal import Decimal
import msvcrt
from data.data import cargar_users, guardar_user, crear_cuenta, get_conversion_rate, cargar_cuentas, guardar_cuentas, tiene_cuenta_moneda
import bcrypt # type: ignore

# Registrar un nuevo usuario
def registrar_usuario(username, password, password2):
    usuarios = cargar_users()
    # Revisa si el usuario ya existe
    if username_existente(username, usuarios):
        return False, "usuario_existente"
    # Revisa si la confirmación de contraseña está bien
    if not password_coincide(password, password2):
        return False, "password_no_coincide"
    
    # Crea el usuario y hashea la contraseña
    usuarios.append({
        "username": username.lower(),
        "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    })
    # Crea sus cuentas
    user_cuentas = {
        "username": username.lower(),
        "ARS": "0"
    }
    guardar_user(usuarios)
    guardar_cuentas(username.lower(), user_cuentas)
    return True, "ok"

# Iniciar sesión con un usuario
def iniciar_sesion(username, password):
    usuarios = cargar_users()
    # Verifica si el usuario existe
    for user in usuarios:
        if user['username'] == username:
            # Verifica si la contraseña es correcta
            if bcrypt.checkpw(password.encode(), user['password'].encode()):
                return True, "ok"
            else:
                return False, "password_incorrecta"
    return False, "usuario_no_encontrado"

# Función para ingresar ARS al saldo
def ingresar_ars(username, cantidad):
    user_cuentas = cargar_cuentas(username)
    if user_cuentas is None:
        return False, "usuario_no_encontrado"
    
    try:
        cantidad_decimal = Decimal(cantidad)
        if cantidad_decimal <= 0:
            return False, "cantidad_invalida"
        
        # Si no tiene cuenta ARS, la crea
        if "ARS" not in user_cuentas:
            user_cuentas["ARS"] = "0"
        
        user_cuentas["ARS"] = str(Decimal(user_cuentas["ARS"]) + cantidad_decimal)
        guardar_cuentas(username, user_cuentas)
        return True, "ok"
    except Exception:
        return False, "monto_invalido"

# Hace que el decimal tenga dos decimales
def formatear_monto(monto):
    return f"{Decimal(str(monto)):.2f}"

# Función para consultar saldos
def consultar_saldos(username):
    cuentas = cargar_cuentas(username)
    if cuentas is None:
        return None
    
    saldos_formateados = {}
    for moneda, saldo in cuentas.items():
        if moneda != "username":
            saldos_formateados[moneda] = formatear_monto(saldo)
    
    return saldos_formateados

# Función para comprar moneda extranjera
def comprar_extranjera(username, cantidad, moneda):
    # Verifica si la cantidad es válida
    try:
        cantidad_decimal = Decimal(cantidad)
        if cantidad_decimal <= 0:
            return False, "cantidad_invalida"
    except:
        return False, "monto_invalido"

    user_cuentas = cargar_cuentas(username)
    # Verifica si el usuario existe
    if user_cuentas is None:
        return False, "usuario_no_encontrado"
    # Verifica si el usuario tiene cuenta en ARS
    elif "ARS" not in user_cuentas:
        return False, "sin_ars"
    
    # Verifica si el usuario tiene cuenta en la moneda que quiere comprar
    if not tiene_cuenta_moneda(username, moneda):
        return False, "sin_cuenta_moneda"

    cuentas = cargar_cuentas(username)
    saldo_ars = Decimal(cuentas.get("ARS", "0.00"))

    rate_ars = get_conversion_rate("USD", "ARS")
    rate_target = get_conversion_rate("USD", moneda)

    # Verifica si se pudo obtener la tasa de conversión
    if rate_ars is None or rate_target is None:
        return False, "sin_tasa"

    # Verifica si el usuario tiene suficiente saldo en ARS
    conversion = (cantidad_decimal * rate_target) / rate_ars
    if saldo_ars < cantidad_decimal:
        return False, "saldo_insuficiente"
    
    # Realiza la conversión de ARS a la moneda extranjera
    cuentas["ARS"] = str(Decimal(cuentas["ARS"]) - cantidad_decimal)
    cuentas[moneda] = str(Decimal(cuentas.get(moneda, "0.00")) + conversion)
    guardar_cuentas(username, cuentas)
    return True, formatear_monto(conversion)

# Función para vender moneda extranjera
def vender_extranjera(username, cantidad, moneda):
    # Verifica si la cantidad es válida
    try:
        cantidad_decimal = Decimal(cantidad)
        if cantidad_decimal <= 0:
            return False, "cantidad_invalida"
    except:
        return False, "monto_invalido"

    user_cuentas = cargar_cuentas(username)
    # Verifica si el usuario existe
    if user_cuentas is None:
        return False, "usuario_no_encontrado"
    # Verifica si el usuario tiene saldo en la moneda extranjera
    elif moneda not in user_cuentas or Decimal(user_cuentas[moneda]) < cantidad_decimal:
        return False, "saldo_insuficiente"

    # se obtiene la tasa de conversión
    rate_ars = get_conversion_rate("USD", "ARS")
    rate_target = get_conversion_rate("USD", moneda)

    # Verifica si se pudo obtener la tasa de conversión
    if rate_ars is None or rate_target is None:
        return False, "sin_tasa"

    # Realiza la conversión de la moneda extranjera a ARS
    conversion = (cantidad_decimal * rate_ars) / rate_target
    user_cuentas["ARS"] = str(Decimal(user_cuentas["ARS"]) + conversion)
    user_cuentas[moneda] = str(Decimal(user_cuentas[moneda]) - cantidad_decimal)
    guardar_cuentas(username, user_cuentas)    
    return True, formatear_monto(conversion)

# Función para crear una nueva cuenta de moneda
def crear_cuenta_moneda(username, moneda):
    return crear_cuenta(username, moneda)

# Función para verificar si un nombre de usuario ya existe al registrarse
def username_existente(username, usuarios):
    return any(user["username"] == username for user in usuarios)

# Función para verificar si las contraseñas coinciden al registrarse
def password_coincide(pass1, pass2):
    return pass1 == pass2

# Función para ingresar una contraseña con asteriscos
def password_asteriscos(prompt):
    print(prompt, end='', flush=True)
    password = ''
    while True:
        ch = msvcrt.getch()
        if ch == b'\r':  # Enter
            print()
            break
        elif ch == b'\x08':  # Boton de borrar
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        else:
            try:
                char = ch.decode('utf-8')
                if char.isprintable():
                    password += char
                    print('*', end='', flush=True)
            except:
                continue
    return password

# Si tiene espacios o es mayor a 30 es invalido
def usuario_invalido(username):
    return (
        bool(username)
        and username.strip() == username
        and " " not in username
        and len(username) <= 30
    )

# Si tiene espacios o es mayor a 30 es invalida
def password_invalida(password):
    return (
        bool(password)
        and password.strip() == password
        and " " not in password
        and len(password) <= 30
    )