import streamlit as st
import qrcode
from io import BytesIO
import streamlit.components.v1 as components
import base64
from utils.visual_helpers import mostrar_pdf


def mostrar():
    #st.header("📎 Material del área y comunicados")
    # condicionar con periodo y grupo
    if st.session_state.periodo1 == "1":
        st.write("Actividades no disponibles")
        #st.subheader(f"Periodo {st.session_state.periodo1} - Grupo {st.session_state.grupo1}")
        ##st.subheader("📂 Materiales disponibles")
        #st.markdown("- [Eva_Operaciones_Básicas](#)")
        #with open("materiales/Eva_Operaciones_Básicas_VA.pdf", "rb") as file:
        #    st.download_button(
        #        label="- [📥 Descargar Eva_Operaciones_Básicas](#)",
        #        data=file,
        #        file_name="Eva_Operaciones_Básicas_VA.pdf",
        #        mime="application/pdf"
        #    )
        #st.markdown("[📥 Descargar Guía de Álgebra 10°](ENLACE_DE_DESCARGA_DIRECTA)")
        #st.subheader("📄 Vista previa - Guía de Álgebra 10°")
        #mostrar_pdf("materiales/Eva_Operaciones_Básicas_VA.pdf")
        #st.markdown("- 📝 [Autoevaluación](#)")
        #st.markdown("[👉 Ir a la Autoevaluación](https://forms.office.com/r/Mpy6gSrerC)", unsafe_allow_html=True)
        #st.subheader("📱 Autoevaluación - escanea el QR")
        #qr = qrcode.make("https://forms.office.com/r/Mpy6gSrerC")
        #buf = BytesIO()
        #qr.save(buf, format="PNG")
        #st.image(buf.getvalue(), caption="Escanea para abrir la autoevaluación")
        #st.subheader("📝 Autoevaluación integrada")
        #components.html(
        #    '''
        #    <iframe width="640px" height="480px" 
        #    src="https://forms.office.com/r/Mpy6gSrerC?embed=true" 
        #    frameborder="0" marginwidth="0" marginheight="0" 
        #    style="border: none; max-width:100%; max-height:100vh" 
        #    allowfullscreen webkitallowfullscreen mozallowfullscreen msallowfullscreen> 
        #    </iframe>
        #    ''',
        #    height=500,
        #)
        #st.subheader("📢 Comunicaciones importantes")
        #st.info("Semana de evaluaciones del 20 al 24 de junio.")
    #####################################################################################################
    elif st.session_state.periodo1 == "2":
        st.subheader(f"Periodo {st.session_state.periodo1} - Grupo {st.session_state.grupo1}")
        #st.subheader("📂 Materiales disponibles")
        ##############################################################
        st.markdown("- Criterios de divisibilidad")
        try:
            with open("App_V2/materiales/Actividad criterios.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad criterios.pdf",
                    mime="application/pdf"
                )
        except:
            with open("D:/Repositorios/Notas_Master/App_V2/materiales/Actividad criterios.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad criterios.pdf",
                    mime="application/pdf"
                )
        ##############################################################
        st.markdown("- Decomposición en factores primos")
        with open("App_V2/materiales/Actividad MCD_mcm.pdf", "rb") as file:
            st.download_button(
                label="- [📥 Descargar Actividad](#)",
                data=file,
                file_name="Actividad MCD_mcm.pdf",
                mime="application/pdf"
            )
        ##############################################################
        st.markdown("- Paginas 3, 4, 5, 6 y 7 del libro guía: Saber Matemático 7°")
        ##############################################################
        st.markdown("- Plegable figuras geométricas planas")
        with open("App_V2/materiales/Actividad plegable figuras geometricas.pdf", "rb") as file:
            st.download_button(
                label="- [📥 Descargar Actividad](#)",
                data=file,
                file_name="Actividad plegable figuras geometricas.pdf",
                mime="application/pdf"
            )
        ##############################################################
        st.markdown("- Taller números enteros")
        
        with open("App_V2/materiales/Taller números enteros.pdf", "rb") as file:
            st.download_button(
                label="- [📥 Descargar Actividad](#)",
                data=file,
                file_name="Taller números enteros.pdf",
                mime="application/pdf"
            )
        ##############################################################
        st.markdown("- Taller de valor absoluto")
        with open("App_V2/materiales/Taller de valor absoluto.pdf", "rb") as file:
            st.download_button(
                label="- [📥 Descargar Actividad](#)",
                data=file,
                file_name="Taller de valor absoluto.pdf",
                mime="application/pdf"
            )
        #####################################################################################################
    elif st.session_state.periodo1 == "3":
        st.subheader(f"Periodo {st.session_state.periodo1} - Grupo {st.session_state.grupo1}")
        #st.subheader("📂 Materiales disponibles")
        ##############################################################
        st.markdown("- Taller operaciones con fracciones")
        try:
            with open("App_V2/materiales/Taller operaciones con fracciones.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Taller operaciones con fracciones.pdf",
                    mime="application/pdf"
                )
        except:
            with open("D:/Repositorios/Notas_Master/App_V2/materiales/Taller operaciones con fracciones.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Taller operaciones con fracciones.pdf",
                    mime="application/pdf"
                )
        ##############################################################
        st.markdown("- Plan Lector 1° parte")
        try:
            with open("App_V2/materiales/Activida_PL_P2.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Activida_PL_P2.pdf",
                    mime="application/pdf"
                )
        except:
            with open("D:/Repositorios/Notas_Master/App_V2/materiales/Activida_PL_P2.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Activida_PL_P2.pdf",
                    mime="application/pdf"
                )
        ##############################################################
        st.markdown("- Números racionales")
        try:
            with open("App_V2/materiales/Actividad ubicación numeros racionales.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad ubicación numeros racionales.pdf",
                    mime="application/pdf"
                )
        except:
            with open("D:/Repositorios/Notas_Master/App_V2/materiales/Actividad ubicación numeros racionales.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad ubicación numeros racionales.pdf",
                    mime="application/pdf"
                )
        ##############################################################
        st.markdown("- Comparación de racionales")
        try:
            with open("App_V2/materiales/Actividad comparación de numeros racionales.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad comparación de numeros racionales.pdf",
                    mime="application/pdf"
                )
        except:
            with open("D:/Repositorios/Notas_Master/App_V2/materiales/Actividad comparación de numeros racionales.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad comparación de numeros racionales.pdf",
                    mime="application/pdf"
                )
        ##############################################################
        st.markdown("- De fracción a decimal")
        try:
            with open("App_V2/materiales/Actividad numeros decimales.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad numeros decimales.pdf",
                    mime="application/pdf"
                )
        except:
            with open("D:/Repositorios/Notas_Master/App_V2/materiales/Actividad numeros decimales.pdf", "rb") as file:
                st.download_button(
                    label="- [📥 Descargar Actividad](#)",
                    data=file,
                    file_name="Actividad numeros decimales.pdf",
                    mime="application/pdf"
                )
            