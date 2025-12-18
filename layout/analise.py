import streamlit as st
import pandas as pd
import numpy as np

from functions.formatters import format_currency, format_df, format_percentage
from functions.utils import style_analise_df

def analise(analise_dfs, analise_vars):
  # Análise e Cruzamentos
  st.header("Análise")

  st.subheader("Demonstrativo Orçamentário x Relação de Pagamentos")

  df_rp, df_do = analise_dfs
  total_orcamento_aprovado, rend_aplicacao, creditos_total, devolucao_valor, tarifas_bancarias, valor_executado_rp = analise_vars

  refs = df_rp[["RUBRICA", "VALOR"]]

  # Cruza "Orçamento Aprovação" x "Relação de Pagamentos"
  result = pd.merge(df_do, refs, right_on="RUBRICA", left_on="RUBRICA", how="outer")

  # Calcula diferença entre orçamento aprovado e executado
  result["Variação [2]"] = result["ORÇAMENTO APROVADO"] - result["VALOR"]

  conditions = [
    result["ORÇAMENTO APROVADO"].isna(),
    result["VALOR"].isna(),
    result["ORÇAMENTO APROVADO"] != 0,
    result["ORÇAMENTO APROVADO"] == 0
  ]

  choices = [
    "Item não aprovado",
    "Não executado",
    ((result["Variação [2]"] / result["ORÇAMENTO APROVADO"]) * 100).round(2),
    "Gasto não previsto"
  ]

  result['Desvio'] = np.select(conditions, choices, default="Indefinido")

  result.rename(columns={ 'VALOR': 'ORÇAMENTO EXECUTADO [1]' }, inplace=True)
  relacao_exec_orcamentaria = ((valor_executado_rp / total_orcamento_aprovado) * 100).round(2)

  formatted_result = format_df(
    result,
    show_total=True,
    currency_cols=[
      'ORÇAMENTO APROVADO',
      'ORÇAMENTO EXECUTADO [1]',
      'Variação [2]'
    ],
    columns_to_sum=[
      'ORÇAMENTO APROVADO',
      'ORÇAMENTO EXECUTADO [1]',
    ],
    percentage_cols=['Desvio']
  )

  styled_result = formatted_result.style.apply(
    style_analise_df,
    axis=1
  )

  df_balance_result = pd.DataFrame({
    'Aporte Spcine': [total_orcamento_aprovado],
    'Rendimentos': [rend_aplicacao],
    'Valor de fomento [1]': [creditos_total],
    'Valor Executado [2]': [valor_executado_rp],
    'Tarifas Bancárias': [tarifas_bancarias],
    'Devolução potencial [3]': [devolucao_valor],
    'Relação de Execução Orçamentária [4]': [str(relacao_exec_orcamentaria)] 
  })

  formatted_df_balance_result = format_df(
    df_balance_result,
    show_total=False,
    currency_cols=[
      'Aporte Spcine',
      'Rendimentos',
      'Valor de fomento [1]',
      'Valor Executado [2]',
      'Tarifas Bancárias',
      'Devolução potencial [3]',
    ],
    percentage_cols=['Relação de Execução Orçamentária [4]']
  )

  st.markdown("Cruzamento das planilhas 'Demonstrativo Orçamentário' e 'Relação de Pagamentos'")
  st.table(styled_result)
  st.caption("[1] ORÇAMENTO EXECUTADO corresponde à coluna *VALOR* de Relação de Pagamentos<br>[2] Variação = ORÇAMENTO APROVADO [Demonstrativo Orçamentário] - ORÇAMENTO EXECUTADO", unsafe_allow_html=True)

  st.subheader("Balanço Geral")

  table_balance_result = '''
    | Aporte Spcine | Rendimentos | Valor de fomento<sup>[1]</sup> | Valor Executado<sup>[2]</sup> | Tarifas Bancárias | Devolução potencial<sup>[3]</sup> | Relação de Execução Orçamentária<sup>[4]</sup> |
    | --- | :---  | :--- | :--- | :--- | :--- | :---: |
    | %s | %s | %s| %s | %s| %s | %s |
  ''' % (
    format_currency(total_orcamento_aprovado),
    format_currency(rend_aplicacao),
    format_currency(creditos_total),
    format_currency(valor_executado_rp),
    format_currency(tarifas_bancarias),
    format_currency(devolucao_valor),
    format_percentage(str(relacao_exec_orcamentaria)),
  )

  st.markdown(table_balance_result, unsafe_allow_html=True)
  st.caption("[1] Valor de fomento = Transferências + Aplicações [Conciliação Bancária]<br>[2] Valor Total [Relação de Pagamentos]<br>[3] Devolução potencial = Valor de Fomento - Pagamentos [Conciliação Bancária]<br>[4] Relação de Execução Orçamentária = Valor Executado / Aporte Spcine (se maior que 100%, houve estouro de orçamento)", unsafe_allow_html=True)

  return [
    formatted_result,
    formatted_df_balance_result
  ]