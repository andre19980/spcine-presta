import streamlit as st
from openpyxl import load_workbook
# from base64 import b64encode

from pages.gerador_relatorio import gerador_relatorio
from pages.gerador_conciliacao_bancaria import gerador_conciliacao_bancaria
from layout.login_screen import login_screen

st.set_page_config(
  page_title="SpcinePresta",
  layout="wide"
)

if not st.user.is_logged_in:
  pg = st.navigation([st.Page(login_screen)])
else:
  pg = st.navigation([
    st.Page(gerador_relatorio, title="Gerador de Relatório"),
    st.Page(gerador_conciliacao_bancaria, title="Gerador de Conciliação Bancária")
  ])

pg.run()