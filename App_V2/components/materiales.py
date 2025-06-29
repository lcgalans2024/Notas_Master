import streamlit as st
import qrcode
from io import BytesIO
import streamlit.components.v1 as components
import base64
from utils.visual_helpers import mostrar_pdf


def mostrar():
    #st.header("📎 Material del área y comunicados")
    st.subheader("📂 Materiales disponibles")
    st.markdown("- [Eva_Operaciones_Básicas](#)")
    with open("materiales/Eva_Operaciones_Básicas_VA.pdf", "rb") as file:
        st.download_button(
            label="- [📥 Descargar Eva_Operaciones_Básicas](#)",
            data=file,
            file_name="Eva_Operaciones_Básicas_VA.pdf",
            mime="application/pdf"
        )
    st.markdown("[📥 Descargar Guía de Álgebra 10°](ENLACE_DE_DESCARGA_DIRECTA)")
    st.subheader("📄 Vista previa - Guía de Álgebra 10°")
    mostrar_pdf("materiales/Eva_Operaciones_Básicas_VA.pdf")
    st.markdown("- 📝 [Autoevaluación](#)")
    st.markdown("[👉 Ir a la Autoevaluación](https://forms.office.com/r/Mpy6gSrerC)", unsafe_allow_html=True)
    st.subheader("📱 Autoevaluación - escanea el QR")
    qr = qrcode.make("https://forms.office.com/r/Mpy6gSrerC")
    buf = BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Escanea para abrir la autoevaluación")
    st.subheader("📝 Autoevaluación integrada")
    components.html(
        '''
        <iframe width="640px" height="480px" 
        src="https://forms.office.com/r/Mpy6gSrerC?embed=true" 
        frameborder="0" marginwidth="0" marginheight="0" 
        style="border: none; max-width:100%; max-height:100vh" 
        allowfullscreen webkitallowfullscreen mozallowfullscreen msallowfullscreen> 
        </iframe>
        ''',
        height=500,
    )
    st.subheader("📢 Comunicaciones importantes")
    st.info("Semana de evaluaciones del 20 al 24 de junio.")