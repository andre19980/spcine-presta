import streamlit as st
import pandas as pd

from functions.get_range import get_range
from functions.formatters import format_df
from functions.utils import style_df

def demonstrativo_orcamentario(wb, file):
  # Demonstratico Orçamentário
  st.header("Demonstrativo Orçamentário")

  ws_do = wb["Demonstrativo Orçamentário"]

  HEADER_ROW, LAST_ROW = get_range("rubrica", "total do projeto", ws_do)
  nrows = LAST_ROW - HEADER_ROW - 1

  dtypes_do = {
    'RUBRICA': str,
    'ORÇAMENTO APROVADO': 'float64',
    'ORÇAMENTO REALIZADO': 'float64',
    'VARIAÇÃO': 'float64',
    'JUSTIFICATIVA PARA VARIAÇÃO': str
  }

  df_do = pd.read_excel(
    file,
    sheet_name="Demonstrativo Orçamentário",
    skiprows=HEADER_ROW - 1,
    header=0,
    nrows=nrows,
    usecols="A:E",
    dtype=dtypes_do
  )

  formatted_df_do = format_df(
    df_do,
    show_total=True,
    currency_cols=['ORÇAMENTO APROVADO', 'ORÇAMENTO REALIZADO', 'VARIAÇÃO'],
    columns_to_sum=['ORÇAMENTO APROVADO', 'ORÇAMENTO REALIZADO', 'VARIAÇÃO']
  )

  styled_df_do = formatted_df_do.style.apply(
    style_df,
    axis=1
  )

  st.table(styled_df_do)

  total_orcamento_aprovado = df_do["ORÇAMENTO APROVADO"].sum()

  return [
    [
      formatted_df_do,

      # df bruto para cálculos
      df_do
    ],
    [total_orcamento_aprovado]
  ]
