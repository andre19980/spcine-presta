import streamlit as st
import pandas as pd

from functions.get_range import get_range

def cabecalho(wb, file):
  ws = wb["Demonstrativo Orçamentário"]

  HEADER_ROW, LAST_ROW = get_range("nome do projeto:", "edital/linha:", ws)
  nrows = LAST_ROW - HEADER_ROW

  df = pd.read_excel(
    file,
    sheet_name="Demonstrativo Orçamentário",
    skiprows=HEADER_ROW - 1,
    header=None,
    nrows=nrows + 1,
    usecols="A:B",
  )

  nome_projeto = df.iloc[0, 1]
  nome_proponente = df.iloc[1, 1]
  num_contrato = df.iloc[2, 1]
  edital = df.iloc[3, 1] if pd.notna(df.iloc[3, 1]) else '-'
  relator = st.user.name

  st.markdown(f"**Nome do projeto:** {nome_projeto}")
  st.markdown(f"**Nome do proponente:** {nome_proponente}")
  st.markdown(f"**Nº do contrato:** {num_contrato}")
  st.markdown(f"**Edital/Linha:** {edital}")
  st.markdown(f"**Relator Spcine** {relator}")

  return [
    nome_projeto,
    nome_proponente,
    num_contrato,
    edital,
    relator,
  ]