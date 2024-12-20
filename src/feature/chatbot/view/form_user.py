import re
import streamlit as st
from feature.chatbot.services.form_data_service import FormDataService

# Función para validar email
def is_valid_email(email):
    """Valida que el email tenga un formato correcto."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Función para validar número de teléfono ecuatoriano
def is_valid_ecuadorian_phone(phone):
    """
    Valida si el número de teléfono ingresado es un número ecuatoriano válido.
    Un número válido tiene:
    - 10 dígitos
    - Inicia con un dígito entre 2 y 7 para líneas fijas o 9 para móviles
    """
    phone_regex = r'^(?:09\d{8}|(?:02|03|04|05|06|07)\d{7})$'
    return re.match(phone_regex, phone) is not None

def verified_indetification(cedula=""):
    # Verificar que la cédula tenga 10 dígitos y sea numérica
    if len(cedula) != 10 or not cedula.isdigit():
        return False

    # Extraer los dígitos necesarios
    provincia = int(cedula[0:2])
    tercer_digito = int(cedula[2])
    digito_verificador = int(cedula[9])
    coeficientes = [int(d) for d in cedula[0:9]]

    # Validar el código de provincia (01-24, 30, 31)
    if provincia < 1 or (provincia > 24 and provincia not in [30, 31]):
        return False

    # Validar el tercer dígito (0-6)
    if tercer_digito > 6:
        return False

    suma = 0
    for i in range(9):
        num = coeficientes[i]
        if i % 2 == 0:  # Posiciones impares (0 indexado)
            num *= 2
            if num > 9:
                num -= 9
        suma += num

    # Calcular el dígito verificador
    residuo = suma % 10
    if residuo == 0:
        digito_calculado = 0
    else:
        digito_calculado = 10 - residuo

    # Verificar si el dígito calculado coincide con el dígito verificador
    return digito_calculado == digito_verificador

def show_form_user():
    """Formulario para recopilar información del usuario."""
    with st.form("Petición de información"):
        # Campos de entrada del formulario
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        telefono = st.text_input("Número Teléfono")
        identificacion = st.text_input("Identificación")
        
        # Botón para enviar
        enviar = st.form_submit_button("Enviar")
        
        # Validaciones individuales
        errors = []
        if enviar:
            if not nombre:
                errors.append("El campo 'Nombre' es obligatorio.")
            if not email or not is_valid_email(email):
                errors.append("El campo 'Email' no es válido.")
            if not telefono or not is_valid_ecuadorian_phone(telefono):
                errors.append("El campo 'Número Teléfono' no es válido.")
            if not identificacion or not verified_indetification(identificacion):
                errors.append("El campo 'Identificación' no es válido.")

            # Mostrar errores individuales
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Crear un diccionario con los datos del formulario si todo es válido
                form_data = {
                    'nombre': nombre,
                    'email': email,
                    'id': identificacion,
                    'telefono': telefono
                }
                
                # Ejecutar el servicio para procesar los datos
                form_service = FormDataService(form_data)
                form_service.process_form_data()

                # Restablecer el estado para evitar que el formulario se muestre de nuevo
                st.session_state['show_form_user'] = False
                st.rerun()

def get_form_data_user():
    return {
        'nombre': st.session_state.get('nombre', ''),
        'email': st.session_state.get('email', ''),
        'id': st.session_state.get('id', ''),
        'telefono': st.session_state.get('telefono', '')
    }

def activate_form_user():
    st.session_state['show_form_user'] = True
