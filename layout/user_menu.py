import streamlit as st

def user_menu():
  flex = st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center")

  flex.subheader(f"Olá, {st.user.name}!")
  flex.button("Log out", on_click=st.logout)

  st.divider()