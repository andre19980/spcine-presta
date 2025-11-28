import streamlit as st

def login_screen():
  st.image("login-img.png")
  st.header("Programa SpcinePresta")
  st.subheader("Por favor, faça o login.")
  st.button("Login com Microsoft", on_click=st.login)