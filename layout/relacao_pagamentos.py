import streamlit as st
import pandas as pd

from functions.get_range import get_range
from functions.formatters import format_currency, format_df
from functions.utils import style_df, style_doc_error
from functions.validators import validar_documento

def relacao_pagamentos(wb, file):
  st.header("Relação de Pagamentos")

  ws_rp = wb["Relação de Pagamentos"]

  HEADER_ROW, LAST_ROW = get_range("rubrica", "total", ws_rp)
  nrows = LAST_ROW - HEADER_ROW - 1

  dtypes_rp = {
    'RUBRICA': str,
    'FAVORECIDO': str,
    'CNPJ / CPF': str,
    'DOC. FISCAL + NÚMERO (Exemplo: NFS 01)': str,
    'CÓDIGO DE VERIFICAÇÃO ou CHAVE DE ACESSO': str,
    'DATA DE EMISSÃO': str, # TODO: veridicar e definir regra pra dado faltante
    'DATA DE PAGAMENTO': 'datetime64[ns]',
    'VALOR': 'float64',
    'ISS (em R$)': 'int64',
    'MUNICIPIO': str,
    'ESTADO': str
  }

  df_rp = pd.read_excel(
    file,
    sheet_name="Relação de Pagamentos",
    skiprows=HEADER_ROW - 1,
    header=0,
    nrows=nrows,
    usecols="A:K",
    dtype=dtypes_rp
  )

  formatted_df_rp = format_df(
    df_rp,
    show_total=True,
    date_cols=['DATA DE PAGAMENTO'],
    currency_cols=[
      'VALOR',
      'ISS (em R$)',
    ],
    columns_to_sum=[
      'VALOR',
      'ISS (em R$)'
    ]
  )

  styled_df_rp = formatted_df_rp.style.apply(
    style_df,
    axis=1
  )

  st.write(styled_df_rp)

  st.subheader("Validações")
  st.markdown("Verificação de CNPJ / CPF")
  has_valid_doc = df_rp["CNPJ / CPF"].apply(validar_documento)
  docs_df_rp = pd.DataFrame()

  if (~has_valid_doc).any():
    invalid_docs_df_rp = df_rp[~has_valid_doc].style.apply(
      style_doc_error,
      axis=0,
      subset=['CNPJ / CPF']
    )

    docs_df_rp = df_rp[~has_valid_doc]

    st.table(invalid_docs_df_rp)
  else:
    st.markdown(
      """
        <p style="background-color:rgb(248, 249, 251);color:green;border-radius: 8px;padding:4px; padding-left:10px">
          Todos os documentos inseridos estão corretos
        </p>
      """,
      unsafe_allow_html=True
    )

  st.subheader("Valor Executado")
  
  valor_executado_rp = df_rp["VALOR"].sum()

  total_df_rp = pd.DataFrame({
    'Valor executado': [valor_executado_rp]
  })

  formatted_total_df_rp = format_df(total_df_rp, False, currency_cols=['Valor executado'])

  table_rp = '''
    | Valor executado |
    | :---: |
    | %s |
  ''' % (
    format_currency(valor_executado_rp)
  )

  st.markdown(table_rp)

  st.divider()

  return [
    [
      formatted_df_rp,
      docs_df_rp,
      formatted_total_df_rp,

      # df bruto para cálculos
      df_rp
    ],
    [
      valor_executado_rp
    ]
  ]