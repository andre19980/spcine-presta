import streamlit as st
import pandas as pd

from functions.get_range import get_range
from functions.formatters import format_currency, format_df_cb, format_df
from functions.utils import style_df

def conciliacao_bancaria(wb, file):
  # Conciliação Bancária
  ws_cb = wb["Conciliação bancária"]

  HEADER_ROW, LAST_ROW = get_range("data de pagamento", "total", ws_cb)
  nrows = LAST_ROW - HEADER_ROW - 1

  dtypes_cb = {
    'DATA DE PAGAMENTO': 'datetime64[ns]',
    'IDENTIFICAÇÃO BANCÁRIA': str,
    'FAVORECIDO': str,
    'TRANSFERÊNCIAS': 'float64',
    'APLICAÇÕES / RESGATES': 'float64',
    'PAGAMENTOS': 'float64',
    'TARIFAS BANCÁRIAS': 'float64',
    'SALDO': 'float64'
  }

  df_cb = pd.read_excel(
    file,
    sheet_name="Conciliação bancária",
    skiprows=HEADER_ROW - 1,
    header=0,
    nrows=nrows,
    usecols="A:H",
    dtype=dtypes_cb
  )

  formatted_df_cb = format_df_cb(df_cb)
  styled_df_cb = formatted_df_cb.style.apply(
    style_df,
    axis=1
  )

  st.header("Conciliação Bancária")
  st.table(styled_df_cb)

  st.subheader("Verificações")
  st.markdown("Verificação de fontes de receita")

  fontes_receita = format_df_cb(df_cb[df_cb["TRANSFERÊNCIAS"].notna()], False)
  styled_fontes_receita = fontes_receita.style.apply(
    style_df,
    axis=1
  )

  st.write(styled_fontes_receita)

  st.subheader("Créditos")
  incentivos_depositos = df_cb["TRANSFERÊNCIAS"].sum()
  rend_aplicacao = df_cb["APLICAÇÕES / RESGATES"].sum()
  creditos_total = incentivos_depositos + rend_aplicacao

  df_cb_creditos = pd.DataFrame({
    'Incentivos Depósitos': [incentivos_depositos],
    'Rendimento Aplicação': [rend_aplicacao],
    'Total': [creditos_total]
  })

  formatted_df_cb_creditos = format_df(
    df_cb_creditos,
    show_total=False,
    currency_cols=['Incentivos Depósitos', 'Rendimento Aplicação', 'Total']
  )

  table_creditos = '''
    | Incentivos Depósitos | Rendimento Aplicação | Total |
    | --- | :--- | :---: |
    | %s | %s | %s |
  ''' % (
    format_currency(incentivos_depositos),
    format_currency(rend_aplicacao),
    format_currency(creditos_total)
  )

  st.markdown(table_creditos)

  st.subheader("Débitos")
  pagamentos = df_cb["PAGAMENTOS"].sum()
  tarifas_bancarias = df_cb["TARIFAS BANCÁRIAS"].sum()

  valor_executado = pagamentos + tarifas_bancarias
  devolucao_valor = creditos_total - pagamentos

  df_cb_debitos = pd.DataFrame({
    'Pagamentos': [pagamentos],
    'Tarifas Bancárias': [tarifas_bancarias],
    'Total': [valor_executado]
  })

  formatted_df_cb_debitos = format_df(
    df_cb_debitos,
    show_total=False,
    currency_cols=['Pagamentos', 'Tarifas Bancárias', 'Total']
  )

  table_debits = '''
    | Pagamentos | Tarifas Bancárias | Total |
    | --- | :--- | :---: |
    | %s | %s | %s |
  ''' % (
    format_currency(pagamentos),
    format_currency(tarifas_bancarias),
    format_currency(valor_executado)
  )

  st.markdown(table_debits)

  st.subheader("Balanço Final")
  diff_value = creditos_total - valor_executado

  df_cb_balance = pd.DataFrame({
    'Créditos': [creditos_total],
    'Débitos': [valor_executado],
    'Balanço [1]': [diff_value]
  })

  formatted_df_cb_balance = format_df(
    df_cb_balance,
    show_total=False,
    currency_cols=['Créditos', 'Débitos', 'Balanço [1]']
  )

  table_balance = '''
    | Créditos | Débitos | Balanço<sup>[1]</sup> |
    | --- | :--- | :---: |
    | %s | %s | %s |
  ''' % (
    format_currency(creditos_total),
    format_currency(valor_executado),
    format_currency(diff_value)
  )

  st.markdown(table_balance, unsafe_allow_html=True)
  st.caption("[1] Balanço = Créditos - Débitos")

  return [
    [
      formatted_df_cb,
      fontes_receita,
      formatted_df_cb_creditos,
      formatted_df_cb_debitos,
      formatted_df_cb_balance
    ],
    [
      rend_aplicacao,
      creditos_total,
      devolucao_valor,
      tarifas_bancarias
    ]
  ]
