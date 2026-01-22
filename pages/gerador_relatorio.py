import streamlit as st
from openpyxl import load_workbook
# from base64 import b64encode

from layout.user_menu import user_menu
from layout.cabecalho import cabecalho
from layout.conciliacao_bancaria import conciliacao_bancaria
from layout.relacao_pagamentos import relacao_pagamentos
from layout.demonstrativo_orcamentario import demonstrativo_orcamentario
from layout.analise import analise
from functions.utils import generate_pdf_from_dataframe

def gerador_relatorio():
  st.title("Presta Contas")
  user_menu()

  uploaded_file = st.file_uploader("Escolha um arquivo .xlsx", type=["xlsx"])

  if uploaded_file is not None:
    handle_file(uploaded_file)

  return

def handle_file(file):
  wb = load_workbook(file, data_only=True)

  st.divider()

  with st.container(horizontal=True, horizontal_alignment='center'):
    st.image("logo_spcine-principal.png", width=200)

  # Cabeçalho
  cabecalho_vars = cabecalho(wb, file)

  # Conciliação Bancária
  cb_elements, cb_vars = conciliacao_bancaria(wb, file)

  st.divider()

  # Relação de Pagamentos
  rp_elements, rp_vars = relacao_pagamentos(wb, file)
  df_rp = rp_elements.pop()

  # Demonstrativo Orçamentário
  do_elements, do_vars = demonstrativo_orcamentario(wb, file)
  df_do = do_elements.pop()

  st.divider()

  # Análise e Cruzamentos
  analise_dfs = [df_rp, df_do]
  analise_vars = [*do_vars, *cb_vars, *rp_vars]
  analise_elements = analise(analise_dfs, analise_vars)

  elements=[*cb_elements, *rp_elements, *do_elements, *analise_elements, cabecalho_vars]
  # Embed PDF to display it:
  # base64_pdf = b64encode(generate_pdf_from_dataframe(elements)).decode("utf-8")
  # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="1200" height="700" type="application/pdf">'
  # st.markdown(pdf_display, unsafe_allow_html=True)

  # Add a download button:
  st.space(size="large")
  with st.container(horizontal=True, horizontal_alignment='center'):
    st.download_button(
      label="Download PDF",
      data=generate_pdf_from_dataframe(elements),
      file_name=f"{cabecalho_vars[0]}-spcine.pdf",
      mime="application/pdf",
      type="primary"
    )