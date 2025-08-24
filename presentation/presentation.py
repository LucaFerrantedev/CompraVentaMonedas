import time
import datetime
from business.business import registrar_usuario, iniciar_sesion, ingresar_ars, crear_cuenta, comprar_extranjera, vender_extranjera, consultar_saldos
from business.business import password_asteriscos, password_coincide, password_invalida, usuario_invalido

while True:
    print("╔════════════════════════════════════╗")
    print("║ 1️⃣  \033[92m\033[1mRegistrarse\033[0m                     ║")
    print("║ 2️⃣  \033[93m\033[1mIniciar sesión\033[0m                  ║")
    print("╚════════════════════════════════════╝")
    try:
        eleccion = int(input("\033[1mIngresa una opción:\033[0m "))
    except ValueError:
        print("\033[31m❌ Por favor ingrese una opción válida.\033[0m")
        continue
    # OPCION 1: REGISTRARSE
    if eleccion == 1:
        try:
            username = input("\033[1m👤 Usuario: \033[0m").lower()
            if not usuario_invalido(username):
                print("\033[31m❌ Usuario invalido.\033[0m")
                continue
            password = password_asteriscos("\033[1m🔑 Contraseña: \033[0m")
            if not password_invalida(password):
                print("\033[31m❌ La contraseña no puede estar vacía ni contener espacios.\033[0m")
                continue    
            password2 = password_asteriscos("\033[1m🔑 Confirmar contraseña: \033[0m")
            if not password_invalida(password2):
                print("\033[31m❌ La contraseña no puede estar vacía ni contener espacios.\033[0m")
                continue
            if not password_coincide(password, password2):
                print("\033[31m❌ Las contraseñas no coinciden.\033[0m")
                continue
            exito, motivo = registrar_usuario(username, password, password2)
            if exito:
                print("\033[92m✅🗒️  Registrado correctamente.\033[0m")
            else:
                if motivo == "usuario_existente":
                    print("\033[33m Ya existe ese usuario.\033[0m")
                elif motivo == "password_no_coincide":
                    print("\033[31m❌ Las contraseñas no coinciden.\033[0m")
                else:
                    print("\033[31m❌ No se pudo registrar el usuario.\033[0m")
        except Exception as e:
            print(f"\033[31m❌ Error inesperado durante el registro: {str(e)}\033[0m")

    # OPCION 2: INICIAR SESION
    elif eleccion == 2:
        try:
            username = input("\033[1m👤 Usuario: \033[0m").lower()
            if not usuario_invalido(username):
                print("\033[31m❌ Usuario invalido.\033[0m")
                continue
            password = password_asteriscos("\033[1m🔑 Contraseña: \033[0m")
            exito, motivo = iniciar_sesion(username, password)
            if exito:
                print("\033[92m✅ Acceso concedido\033[0m")
                # Menú de usuario - AHORA DENTRO DEL TRY
                while True:
                    hora = datetime.datetime.now().hour
                    if 6 <= hora < 12:
                        saludo = "Buenos días"
                    elif 12 <= hora < 20:
                        saludo = "Buenas tardes"
                    else:
                        saludo = "Buenas noches"
                    print("\n" + "═" * 40)
                    print(f"\033[92m👋 {saludo}, \033[0m{username}".center(40))
                    print("═" * 40)
                    print("1️⃣  | 🚩  Ingresar ARS")
                    print("2️⃣  | ➕  Crear cuenta de moneda")
                    print("3️⃣  | 🌎  Comprar moneda extranjera")
                    print("4️⃣  | 💱  Vender moneda extranjera")
                    print("5️⃣  | ℹ️   Consultar saldo")
                    print("6️⃣  | 🚪  Cerrar sesión")
                    print("═" * 40)
                    try:
                        opcion = int(input("\033[1mSeleccione una opción: \033[0m"))
                    except ValueError:
                        print("\033[31m❌ Por favor ingrese una opción válida.\033[0m")
                        continue

                    # Ingresar ARS
                    if opcion == 1:
                        cantidad = input("\033[1mIngrese la cantidad de ARS a ingresar: \033[0m")
                        exito, motivo = ingresar_ars(username, cantidad)
                        if exito:
                            print("\033[92m✅ Ingreso exitoso.\033[0m")
                        else:
                            if motivo == "cantidad_invalida":
                                print("\033[31m❌ La cantidad debe ser mayor que cero.\033[0m")
                            elif motivo == "monto_invalido":
                                print("\033[31m❌ Ingrese un número válido.\033[0m")
                            else:
                                print("\033[31m❌ No se pudo ingresar ARS.\033[0m")
                    
                    # Crear nueva cuenta
                    elif opcion == 2:
                        moneda = input("\033[1mIngrese la moneda para crear cuenta (USD, EUR, etc.): \033[0m").upper()
                        exito = crear_cuenta(username, moneda)
                        if exito:
                            print(f"\033[92m✅ Cuenta de {moneda} creada exitosamente.\033[0m")
                        else:
                            print(f"\033[31m❌ Ya tienes una cuenta de {moneda} o ocurrió un error.\033[0m")
                    
                    # Comprar moneda extranjera
                    elif opcion == 3:
                        moneda = input("\033[1mIngrese la moneda extranjera a comprar (USD, EUR, etc.): \033[0m").upper()
                        cantidad = input("\033[1mIngrese la cantidad en ARS a convertir: \033[0m")
                        tinicio = time.time()
                        confirmar = input("\033[1m¿Confirmás la compra? (s/n): \033[0m").lower()
                        if (time.time()-tinicio) > 120:
                            confirmar = 'n'
                        # Si el usuario confirma la compra se llama a la función comprar_extranjera
                        if confirmar in ('s', 'S'):
                            exito, resultado = comprar_extranjera(username, cantidad, moneda)
                            if exito:
                                print(f"\033[92m✅ Compra exitosa. Saldo convertido: {resultado} {moneda}.\033[0m")
                            else:
                                if resultado == "cantidad_invalida":
                                    print("\033[31m❌ La cantidad debe ser mayor que cero.\033[0m")
                                elif resultado == "monto_invalido":
                                    print("\033[31m❌ Ingrese un monto válido.\033[0m")
                                elif resultado == "usuario_no_encontrado":
                                    print("\033[31m❌ Usuario no encontrado.\033[0m")
                                elif resultado == "sin_ars":
                                    print("\033[31m❌ El usuario no tiene saldo en ARS.\033[0m")
                                elif resultado == "sin_tasa":
                                    print("\033[31m❌ Error al obtener la tasa de conversión.\033[0m")
                                elif resultado == "saldo_insuficiente":
                                    print("\033[31m❌ No tenés suficiente saldo en ARS para comprar.\033[0m")
                                elif resultado == "sin_cuenta_moneda":
                                    print(f"\033[31m❌ No tenés una cuenta de {moneda} para comprar.\033[0m")
                                else:
                                    print("\033[31m❌ No se pudo realizar la compra.\033[0m")
                        else:
                            print("\033[31m❌ Compra cancelada.\033[0m")
                    
                    # Vender moneda extranjera
                    elif opcion == 4:
                        moneda = input("\033[1mIngrese la moneda extranjera a vender (USD, EUR, etc.): \033[0m").upper()
                        cantidad = input(f"\033[1mIngrese la cantidad en {moneda} a convertir: \033[0m")
                        tinicio = time.time()
                        confirmar = input(f"\033[1m¿Confirmás la venta de {cantidad} {moneda} a ARS? (s/n): \033[0m").lower()
                        if (time.time()-tinicio) > 120:
                            confirmar = 'n'
                        # Si el usuario confirma la venta se llama a la función vender_extranjera    
                        if confirmar in ('s', 'S'):
                            exito, resultado = vender_extranjera(username, cantidad, moneda)
                            if exito:
                                print(f"\033[92m✅ Venta exitosa. Saldo convertido: {resultado} ARS.\033[0m")
                            else:
                                if resultado == "cantidad_invalida":
                                    print("\033[31m❌ La cantidad debe ser mayor que cero.\033[0m")
                                elif resultado == "monto_invalido":
                                    print("\033[31m❌ Ingrese un monto válido.\033[0m")
                                elif resultado == "usuario_no_encontrado":
                                    print("\033[31m❌ Usuario no encontrado.\033[0m")
                                elif resultado == "saldo_insuficiente":
                                    print("\033[31m❌ No tenés suficiente saldo en la moneda para vender.\033[0m")
                                elif resultado == "sin_tasa":
                                    print("\033[31m❌ Error al obtener la tasa de conversión.\033[0m")
                                elif resultado == "sin_cuenta_moneda":
                                    print(f"\033[31m❌ No tenés una cuenta de {moneda} para vender.\033[0m")
                                else:
                                    print("\033[31m❌ No se pudo realizar la venta.\033[0m")
                        else:
                            print("\033[31m❌ Venta cancelada.\033[0m")
                    
                    # Consultar saldo
                    elif opcion == 5:
                        saldos = consultar_saldos(username)
                        if saldos is None:
                            print("\033[31m❌ No se pudieron cargar los saldos.\033[0m")
                        else:
                            print("\n" + "═" * 40)
                            print(f"\033[1mSaldo actual de {username}:\033[0m".center(40))
                            print("═" * 40)
                            for moneda, saldo in saldos.items():
                                print(f"{moneda}: 💵 {saldo}")
                            print("═" * 40)
                            input("\nPresione Enter para volver al menú...")
                    
                    elif opcion == 6:
                        print("\033[92m👋 ¡Hasta luego!\033[0m")
                        break
                    else:
                        print("\033[31m❔ Opción inválida\033[0m")
            else:
                if motivo == "usuario_no_encontrado":
                    print("\033[31m❌ Usuario no encontrado.\033[0m")
                elif motivo == "password_incorrecta":
                    print("\033[31m❌ Contraseña incorrecta.\033[0m")
                else:
                    print("\033[31m❌ No se pudo iniciar sesión.\033[0m")
        except Exception as e:
            print(f"\033[31m❌ Error inesperado durante la sesión: {str(e)}\033[0m")
    
    else:
        print("\033[31m❌ Opción no válida. Por favor, seleccione 1 o 2.\033[0m")