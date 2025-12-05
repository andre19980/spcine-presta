import streamlit as st
import pandas as pd
import numpy as np

from functions.formatters import format_currency, format_df
from functions.utils import style_df

def analise(analise_dfs, analise_vars):
  # Análise e Cruzamentos
  st.header("Análise")

  st.subheader("Demonstrativo Orçamentário x Relação de Pagamentos")
  st.markdown("Valores por rubrica na Relação de Pagamentos")

  df_rp, df_do = analise_dfs
  total_orcamento_aprovado, rend_aplicacao, creditos_total, devolucao_valor, tarifas_bancarias, valor_executado_rp = analise_vars

  refs = df_rp[["RUBRICA", "VALOR"]]
  valores_por_rubrica = refs.groupby("RUBRICA").sum().reset_index()

  formatted_valores_por_rubrica = format_df(
    valores_por_rubrica,
    show_total=True,
    currency_cols=['VALOR'],
    columns_to_sum=['VALOR']
  )

  st.write(formatted_valores_por_rubrica)

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

  formatted_result = format_df(
    result,
    show_total=False,
    currency_cols=[
      'ORÇAMENTO APROVADO',
      'ORÇAMENTO REALIZADO',
      'VARIAÇÃO',
      'VALOR',
      'Diferença Inteira'
    ],
    percentage_cols=['Desvio Percentual (%)']
  )

  styled_result = formatted_result.style.apply(
    style_df,
    axis=1
  )

  df_balance_result = pd.DataFrame({
    'Aporte Spcine': [total_orcamento_aprovado],
    'Rendimentos': [rend_aplicacao],
    'Valor de fomento [1]': [creditos_total],
    'Valor Executado [2]': [valor_executado_rp],
    'Tarifas Bancárias': [tarifas_bancarias],
    'Valor possível de devolução [3]': [devolucao_valor]
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
      'Valor possível de devolução [3]',
    ]
  )

  st.markdown("Cruzamento das planilhas 'Demonstrativo Orçamentário' e 'Relação de Pagamentos'")
  st.table(styled_result)

  st.subheader("Balanço Geral")

  table_balance_result = '''
    | Aporte Spcine | Rendimentos | Valor de fomento<sup>[1]</sup> | Valor Executado<sup>[2]</sup> | Tarifas Bancárias | Valor possível de devolução<sup>[3]</sup> |
    | --- | :---  | :--- | :--- | :--- | :---: |
    | %s | %s | %s| %s | %s| %s |
  ''' % (
    format_currency(total_orcamento_aprovado),
    format_currency(rend_aplicacao),
    format_currency(creditos_total),
    format_currency(valor_executado_rp),
    format_currency(tarifas_bancarias),
    format_currency(devolucao_valor),
  )

  st.markdown(table_balance_result, unsafe_allow_html=True)
  st.caption("[1] Valor de fomento = Transferências + Aplicações [Conciliação Bancária]<br>[2] Valor Total [Relação de Pagamentos]<br>[3] Valor possível de devolução = Valor de Fomento - Pagamentos [Conciliação Bancária]", unsafe_allow_html=True)

  return [
    formatted_valores_por_rubrica,
    formatted_result,
    formatted_df_balance_result
  ]