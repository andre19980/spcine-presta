import streamlit as st

def login_screen():
  with st.container(horizontal=True, horizontal_alignment="center"):
    st.image("login-img.png", width=600)

  st.header("Programa SpcinePresta", text_alignment="center")
  st.subheader("Por favor, faça o login.", text_alignment="center")

  with st.container(horizontal=True, horizontal_alignment="center"):
    st.button("Login com Microsoft", on_click=st.login)