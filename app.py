import streamlit as st
import pandas as pd
import numpy as np
from openpyxl import load_workbook

from layout.user_menu import user_menu
from layout.login_screen import login_screen
from functions.get_range import get_range
from functions.formatters import format_currency
from functions.validators import validar_documento

def main_app():
  uploaded_file = st.file_uploader("Escolha um arquivo .xlsx", type=["xlsx"])

  if uploaded_file is not None:
    handle_file(uploaded_file)

  return

def handle_file(file):
  wb = load_workbook(file, data_only=True)

  st.divider()

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

  df_cb_last_row = pd.read_excel(
    file,
    sheet_name="Conciliação bancária",
    skiprows=LAST_ROW-1,
    header=None,
    nrows=1,
    usecols="A:H",
    names=df_cb.columns.values,
    keep_default_na=False
  )

  st.header("Conciliação Bancária")
  st.table(pd.concat([df_cb, df_cb_last_row], ignore_index=True))

  st.subheader("Verificações")
  st.markdown("Verificação de fontes de receita")
  st.write(df_cb[df_cb["TRANSFERÊNCIAS"].notna()])

  st.subheader("Créditos")
  incentivos_depositos = df_cb["TRANSFERÊNCIAS"].sum()
  rend_aplicacao = df_cb["APLICAÇÕES / RESGATES"].sum()
  credits_total = incentivos_depositos + rend_aplicacao

  table_credits = '''
    | Incentivos Depósitos | Rendimento Aplicação | Total |
    | --- | :--- | :---: |
    | %s | %s | %s |
  ''' % (
    format_currency(incentivos_depositos),
    format_currency(rend_aplicacao),
    format_currency(credits_total)
  )

  st.markdown(table_credits)

  st.subheader("Débitos")
  pagamentos = df_cb["PAGAMENTOS"].sum()
  tarifas_bancarias = df_cb["TARIFAS BANCÁRIAS"].sum()

  valor_executado = pagamentos + tarifas_bancarias

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
  diff_value = credits_total - valor_executado

  table_balance = '''
    | Créditos | Débitos | Balanço<sup>[1]</sup> |
    | --- | :--- | :---: |
    | %s | %s | %s |
  ''' % (
    format_currency(credits_total),
    format_currency(valor_executado),
    format_currency(diff_value)
  )

  st.markdown(table_balance, unsafe_allow_html=True)
  st.caption("[1] Balanço = Créditos - Débitos")

  st.divider()

  # Relação de Pagamentos
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
    'IDENTIFICAÇÃO BANCÁRIA (Exemplo: TED XXX.XXX)': str,        
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
    usecols="A:L",
    dtype=dtypes_rp
  )

  df_rp_last_row = pd.read_excel(
    file,
    sheet_name="Relação de Pagamentos",
    skiprows=LAST_ROW-1,
    header=None,
    nrows=1,
    usecols="A:L",
    names=df_rp.columns.values,
    keep_default_na=False
  )

  st.table(pd.concat([df_rp, df_rp_last_row], ignore_index=True))

  st.subheader("Validações")
  st.markdown("Verificação de CNPJ / CPF")
  has_valid_doc = df_rp["CNPJ / CPF"].apply(validar_documento)

  st.table(df_rp[~has_valid_doc])

  st.subheader("Valor Executado")
  
  valor_executado_rp = df_rp["VALOR"].sum()

  table_rp = '''
    | Valor executado |
    | :---: |
    | %s |
  ''' % (
    format_currency(valor_executado_rp)
  )

  st.markdown(table_rp)

  st.divider()

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

  df_do_last_row = pd.read_excel(
    file,
    sheet_name="Demonstrativo Orçamentário",
    skiprows=LAST_ROW-1,
    header=None,
    nrows=1,
    usecols="A:E",
    names=df_do.columns.values,
    keep_default_na=False
  )

  st.table(pd.concat([df_do, df_do_last_row], ignore_index=True))

  total_orcamento_aprovado = df_do["ORÇAMENTO APROVADO"].sum()

  st.divider()

  # Análise e Cruzamentos
  st.header("Análise")

  st.subheader("Demonstrativo Orçamentário x Relação de Pagamentos")
  st.markdown("Valores por rubrica na Relação de Pagamentos")

  refs = df_rp[["RUBRICA", "VALOR"]]
  valores_por_rubrica = refs.groupby("RUBRICA").sum().reset_index()

  st.table(valores_por_rubrica)

  # Cruza "Orçamento Aprovação" x "Relação de Pagamentos"
  result = pd.merge(df_do, valores_por_rubrica, right_on="RUBRICA", left_on="RUBRICA", how="outer")

  # Calcula diferença entre orçamento aprovado e executado
  result["Diferença Inteira"] = result["ORÇAMENTO APROVADO"] - result["VALOR"]

  conditions = [
    result["ORÇAMENTO APROVADO"].isna(),
    result["VALOR"].isna(),
    result["ORÇAMENTO APROVADO"] != 0,
    result["ORÇAMENTO APROVADO"] == 0
  ]

  choices = [
    "Item não aprovado",
    "Não executado",
    ((result["Diferença Inteira"] / result["ORÇAMENTO APROVADO"]) * 100).round(2),
    "Gasto não previsto"
  ]

  result['Desvio Percentual (%)'] = np.select(conditions, choices, default="Indefinido")

  st.markdown("Cruzamento das planilhas 'Demonstrativo Orçamentário' e 'Relação de Pagamentos'")
  st.table(result)

  st.subheader("Balanço Geral")

  table_balance_result = '''
    | Valor Aprovado | Rendimentos | Valor Declarado* | Valor Executado<sup>[1]</sup> |
    | --- | :---  | :--- | :---: |
    | %s | %s | %s| %s |
  ''' % (
    format_currency(total_orcamento_aprovado),
    format_currency(rend_aplicacao),
    format_currency(valor_executado_rp),
    format_currency(valor_executado),
  )

  st.markdown(table_balance_result, unsafe_allow_html=True)
  st.caption("*Na planilha Relação de Pagamentos<br>[1] Valor Executado = Pagamentos + Tarifas Bancárias", unsafe_allow_html=True)

if not st.user.is_logged_in:
  login_screen()
else:
  user_menu()
  main_app()
