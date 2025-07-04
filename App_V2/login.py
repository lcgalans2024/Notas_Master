import streamlit as st
from utils.usuarios import construir_usuarios
import pandas as pd

# Validación simple de usuario y clave con un archivo csv

def validarUsuario(usuario): #, clave):  
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        # clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """
    # Cargamos la tabla de usuarios desde el diccionario de usuarios
    dict_usuarios = construir_usuarios()
    documentos = list(dict_usuarios.keys())
    nombres = list(dict_usuarios.values())
    # Cargamos la tabla de usuarios desde el archivo csv
    dfusuarios = pd.DataFrame({
        'DOCUMENTO': documentos,
            'nombre': nombres})
    if len(dfusuarios[(dfusuarios['DOCUMENTO']==usuario)
                       #& (dfusuarios['clave']==clave)
                       ])>0:
        # guardar nombre del usuario en session state
        st.session_state['nombre'] = dfusuarios[(dfusuarios['DOCUMENTO']==usuario)]['nombre'].values[0]
    
        return True
    else:
        return False
    #return dfusuarios

def generarMenu(usuario):
    """Genera el menú dependiendo del usuario

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar:
        # Cargamos la tabla de usuarios
        dfusuarios = pd.read_csv('usuarios.csv')
        # Filtramos la tabla de usuarios
        dfUsuario =dfusuarios[(dfusuarios['usuario']==usuario)]
        # Cargamos el nombre del usuario
        nombre= dfUsuario['nombre'].values[0]
        #Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{nombre}]** ")
        # Mostramos los enlaces de páginas
        #st.page_link("inicio.py", label="Inicio")
        st.subheader("Tableros")
        st.page_link("components/consulta_notas.py", label="Ventas", icon=":material/sell:")
        st.page_link("components/materiales.py", label="Compras", icon=":material/shopping_cart:")
        #st.page_link("pages/pagina3.py", label="Personal", icon=":material/group:")    
        # Botón para cerrar la sesión
        btnSalir=st.button("Salir")
        if btnSalir:
            st.session_state.clear()
            # Luego de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
            st.rerun()

def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es valido
    """    
    # Validamos si el usuario ya fue ingresado    
    if 'usuario' in st.session_state:
        #generarMenu(st.session_state['usuario']) # Si ya hay usuario cargamos el menu
        st.write(f"Hola **:blue-background[{st.session_state['nombre']}]** con documento **:blue-background[{st.session_state['usuario']}]**")
        st.write("Bienvenido a la aplicación")        
    else: 
        # Cargamos el formulario de login       
        with st.form('frmLogin'):
            parUsuario = st.text_input('Usuario',type='password')
            #parPassword = st.text_input('Password',type='password')
            btnLogin=st.form_submit_button('Ingresar',type='primary')
            if btnLogin:
                #st.write(validarUsuario(parUsuario))
                #Verificamos si el usuario es valido               
                if validarUsuario(parUsuario):#,parPassword):
                    st.session_state['usuario'] = parUsuario
                    if parUsuario == "0":
                        st.session_state['grupo1'] = ""
                        st.session_state['adm'] = "Administrador"
                    else:
                        # obtener grupo del usuario str(int(valor[:4]))
                        st.session_state['grupo1'] = st.session_state.df_estudiantes[st.session_state.df_estudiantes['DOCUMENTO'] == parUsuario]['GRUPO'].values[0][:3]
                    # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                    st.rerun()
                else:
                    # Si el usuario es invalido, mostramos el mensaje de error
                    st.error("Usuario o clave inválidos",icon=":material/gpp_maybe:")