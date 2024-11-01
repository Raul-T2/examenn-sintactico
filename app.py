from flask import Flask, render_template, request, jsonify
import ply.yacc as yacc
import re

app = Flask(__name__)

# Diccionario de entidades de nacimiento
ENTIDADES = {
    "AS": "AGUASCALIENTES", "BC": "BAJA CALIFORNIA", "BS": "BAJA CALIFORNIA SUR",
    "CC": "CAMPECHE", "CL": "COAHUILA", "CM": "COLIMA", "CS": "CHIAPAS", "CH": "CHIHUAHUA",
    "DF": "DISTRITO FEDERAL", "DG": "DURANGO", "GT": "GUANAJUATO", "GR": "GUERRERO",
    "HG": "HIDALGO", "JC": "JALISCO", "MC": "MÉXICO", "MN": "MICHOACÁN", "MS": "MORELOS",
    "NT": "NAYARIT", "NL": "NUEVO LEÓN", "OC": "OAXACA", "PL": "PUEBLA", "QT": "QUERÉTARO",
    "QR": "QUINTANA ROO", "SP": "SAN LUIS POTOSÍ", "SL": "SINALOA", "SR": "SONORA",
    "TC": "TABASCO", "TS": "TAMAULIPAS", "TL": "TLAXCALA", "VZ": "VERACRUZ", "YN": "YUCATÁN",
    "ZS": "ZACATECAS", "NE": "NACIDO EN EL EXTRANJERO"
}

# Definición de tokens
tokens = (
    'LETRAS',
    'NUMEROS'
)

# Reglas para los tokens
t_LETRAS = r'[A-Z]'
t_NUMEROS = r'[0-9]'

# Regla para manejar errores
def t_error(t):
    t.lexer.skip(1)

# Construcción del lexer
import ply.lex as lex
lexer = lex.lex()

# Definir el análisis sintáctico usando yacc
def p_curp(p):
    '''curp : LETRAS LETRAS LETRAS LETRAS NUMEROS NUMEROS NUMEROS NUMEROS NUMEROS NUMEROS LETRAS LETRAS LETRAS LETRAS LETRAS NUMEROS'''
    p[0] = p[1:]

def p_error(p):
    pass

# Construcción del parser
parser = yacc.yacc()

# Función para verificar si un año es bisiesto
def es_bisiesto(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# Función para desglosar y validar la CURP
def analizar_curp(curp):
    if len(curp) != 18 or not curp.isalnum() or not curp.isupper():
        return [], [], "La CURP es inválida: debe contener exactamente 18 caracteres alfanuméricos en mayúsculas."

    tokens = [
        curp[:2],             
        curp[2],              
        curp[3],              
        curp[4:6],            
        curp[6:8],            
        curp[8:10],           
        curp[10],             
        curp[11:13],          
        curp[13],             
        curp[14],             
        curp[15],             
        curp[16:18]           
    ]

    descripcion = [
        "Apellido paterno",
        "Apellido materno",
        "Inicial del nombre",
        "Año de nacimiento",
        "Mes de nacimiento",
        "Día de nacimiento",
        "Género: Masculino" if curp[10] == "H" else "Género: Femenino",
        f"Entidad de nacimiento: {ENTIDADES.get(curp[11:13], 'Entidad desconocida')}",
        "Consonante interna del apellido paterno",
        "Consonante interna del apellido materno",
        "Consonante interna del primer nombre",
        "Homoclave (RENAPO)"
    ]

    # Validación de fechas
    anio = int(curp[4:6]) + 1900 if int(curp[4:6]) < 50 else int(curp[4:6]) + 2000
    mes = int(curp[6:8])
    dia = int(curp[8:10])

    mensaje = ""
    if mes < 1 or mes > 12:
        mensaje = "La CURP es inválida: el mes de nacimiento debe estar entre 01 y 12."
    elif mes == 2:
        if es_bisiesto(anio):
            if dia > 29:
                mensaje = "La CURP es inválida: febrero tiene un máximo de 29 días en un año bisiesto."
        else:
            if dia > 28:
                mensaje = "La CURP es inválida: febrero tiene un máximo de 28 días en un año no bisiesto."
    elif mes in [4, 6, 9, 11] and dia > 30:
        mensaje = f"La CURP es inválida: el mes {mes:02d} tiene un máximo de 30 días."
    elif mes in [1, 3, 5, 7, 8, 10, 12] and dia > 31:
        mensaje = f"La CURP es inválida: el mes {mes:02d} tiene un máximo de 31 días."
    else:
        mensaje = "La CURP es válida y tiene un formato correcto."

    return tokens, descripcion, mensaje



# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el procesamiento de la CURP
@app.route('/analizar', methods=['POST'])
def analizar():
    curp = request.json['curp'].strip().upper()
    tokens, descripcion, mensaje = analizar_curp(curp)

    total_numeros = sum(c.isdigit() for c in curp)
    total_letras = sum(c.isalpha() for c in curp)

    return jsonify({
        'tokens': tokens,
        'descripcion': descripcion,
        'mensaje': mensaje,
        'total_numeros': total_numeros,
        'total_letras': total_letras
    })

if __name__ == '__main__':
    app.run(debug=True)
