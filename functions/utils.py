import streamlit as st
import numpy as np
import pandas as pd
import re
import io
from fpdf import FPDF
from fpdf.fonts import FontFace
from functions.formatters import brl_to_float

POSITIVE_COLOR = (0, 128, 0)
NEGATIVE_COLOR = (255, 0, 0)
negative_currency_pattern = r"R\$ -\d*.?\d+,\d+"
positive_currency_pattern = r"R\$ (?:[1-9]\d{0,2}(?:\.\d{3})*),\d{2}"

def style_df(row):
  if row.name == 'Total':
    return np.repeat(f"background-color: rgb(248, 249, 251)", len(row))

  np_row = row.to_numpy()
  vmatch = np.vectorize(lambda x: bool(re.match(negative_currency_pattern, x)))

  return np.where(vmatch(np_row), f"color: red;", f"color: rgb(49, 51, 63);")

def style_analise_df(row):
  if row.name == 'Total':
    return np.repeat(f"background-color: rgb(248, 249, 251)", len(row))

  np_row = row.to_numpy()
  vmatch = np.vectorize(lambda x: bool(re.match(negative_currency_pattern, x)))
  styles_np = np.where(vmatch(np_row), f"color: red;", f"color: rgb(49, 51, 63);")

  variacao = brl_to_float(np_row[3])

  if not variacao:
    return styles_np
  elif variacao > 0:
    styles_np[4] = f"color: green;"
  else:
    styles_np[4] = f"color: red;"

  return styles_np

def style_doc_error(col):
  return np.repeat(f"color: red;", len(col))

def create_pdf_table(pdf, dataframe, width=None, align='center', highlight_col=None, highlight_color=NEGATIVE_COLOR):
  DF = dataframe.map(str)
  COLUMNS = [list(DF)]
  ROWS = DF.values.tolist()
  DATA = COLUMNS + ROWS

  has_total_row = 'Total' in DF.index

  headings_style = FontFace(
    emphasis="BOLD",
    color=(131,133,140),
    fill_color=(248, 249, 251),
    size_pt=5
  )

  pdf.set_font('Arial', '', 6)
  pdf.set_line_width(0.1)
  pdf.set_draw_color(234, 234, 235)
  pdf.set_fill_color(0, 0, 0)

  with pdf.table(
    borders_layout="ALL",
    text_align="LEFT",
    headings_style=headings_style,
    width=width,
    align=align
  ) as table:
    for index, data_row in enumerate(DATA):
      row = table.row()

      for i, datum in enumerate(data_row):
        if re.match(negative_currency_pattern, datum):
          pdf.set_text_color(*NEGATIVE_COLOR)
        else:
          pdf.set_text_color(49, 51, 63)

        # GAMBIARRA: tratamento para estilização da coluna "Desvio" (index 4) da tabela "Demonstrativo Orçamentário x Relação de Pagamentos"
        if 'Desvio' in COLUMNS[0] and i == 4:
          if re.match(negative_currency_pattern, data_row[3]):
            pdf.set_text_color(*NEGATIVE_COLOR)
          elif re.match(positive_currency_pattern, data_row[3]):
            pdf.set_text_color(*POSITIVE_COLOR)
          else:
            pdf.set_text_color(49, 51, 63)

        if highlight_col != None and highlight_col == i:
          pdf.set_text_color(*highlight_color)

        if has_total_row and index == len(DF) and i == 0:
          pdf.set_fill_color(248, 249, 251)
          row.cell('Total')
        else:
          row.cell(datum)

  return pdf

def set_header(pdf):
  pdf.set_font('Helvetica', 'B', 16)
  pdf.set_text_color(49, 51, 63)

  return pdf

def set_subheader(pdf):
  pdf.set_font('Helvetica', 'B', 12)
  pdf.set_text_color(49, 51, 63)

  return pdf

def set_text(pdf):
  pdf.set_font('Helvetica', '', 9)
  pdf.set_text_color(49, 51, 63)

  return pdf

def set_caption(pdf):
  pdf.set_font('Helvetica', '', 5)
  pdf.set_text_color(49, 51, 63)

  return pdf

def divider(pdf):
  pdf.cell(0, 10, '', new_x="LMARGIN", new_y="NEXT")
  pdf.cell(0, 0, "", border="B", new_x="LMARGIN", new_y="NEXT")
  pdf.cell(0, 10, '', new_x="LMARGIN", new_y="NEXT")

  return pdf

@st.cache_data
def generate_pdf_from_dataframe(elements):
  pdf = FPDF()
  pdf.add_page()
  image_width = 38

 # Header
  pdf.image(name="logo_spcine-principal.png", w=image_width, x=(pdf.w - image_width) / 2)

  # Cabeçalho
  nome_projeto, nome_proponente, num_contrato, edital, analista = elements[11]
  pdf = set_text(pdf)
  pdf.cell(w=None, h=None, text=f"**Nome do projeto:** {nome_projeto}", markdown=True)
  pdf.ln(5)
  pdf.cell(w=None, h=None, text=f"**Nome do proponente:** {nome_proponente}", markdown=True)
  pdf.ln(5)
  pdf.cell(w=None, h=None, text=f"**Nº do contrato:** {num_contrato}", markdown=True)
  pdf.ln(5)
  pdf.cell(w=None, h=None, text=f"**Edital/Linha:** {edital}", markdown=True)
  pdf.ln(5)
  pdf.cell(w=None, h=None, text=f"**Analista Spcine:** {analista}", markdown=True)
  pdf.ln(10)

  # Conciliação Bancária
  pdf = set_header(pdf)
  pdf.cell(w=None, h=None, text='Conciliação Bancária')
  pdf.ln(10)
  pdf = create_pdf_table(pdf, elements[0])
  pdf.ln(10)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Verificações')
  pdf.ln(7)

  pdf = set_text(pdf)
  pdf.cell(w=None, h=None, text='Verificação de fontes de receita')
  pdf.ln(7)
  pdf = create_pdf_table(pdf, elements[1])
  pdf.ln(7)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Créditos')
  pdf.ln(7)
  pdf = create_pdf_table(pdf, elements[2], width=100, align='left')
  pdf.ln(7)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Débitos')
  pdf.ln(7)
  pdf = create_pdf_table(pdf, elements[3], width=100, align='left')
  pdf.ln(7)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Balanço')
  pdf.ln(7)
  pdf = create_pdf_table(pdf, elements[4], width=100, align='left')
  pdf = set_caption(pdf)
  pdf.ln(2)
  pdf.cell(w=None, h=None, text='[1] Balanço = Créditos - Débitos')

  pdf = divider(pdf)

  # Relação de Pagamentos
  pdf = set_header(pdf)
  pdf.cell(w=None, h=None, text='Relação de Pagamentos')
  pdf.ln(10)
  pdf = create_pdf_table(pdf, elements[5])
  pdf.ln(7)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Validações')
  pdf.ln(7)

  pdf = set_text(pdf)
  pdf.cell(w=None, h=None, text='Verificação de CNPJ / CPF')
  pdf.ln(7)

  if (elements[6].empty == False):
    pdf = create_pdf_table(pdf, elements[6], highlight_col=2) # index 2 = 'CNPJ / CPF'
  else:
    pdf.set_text_color(0, 128, 0)
    pdf.cell(w=0, h=8, text='Todos os documentos inseridos estão corretos', fill=(248, 249, 251))

  pdf.ln(7)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Valor Executado')
  pdf.ln(7)

  pdf = create_pdf_table(pdf, elements[7], width=20, align='left')

  pdf = divider(pdf)

  # Demonstrativo Orçamentário
  pdf = set_header(pdf)
  pdf.cell(w=None, h=None, text='Demonstrativo Orçamentário')
  pdf.ln(10)
  pdf = create_pdf_table(pdf, elements[8])

  pdf = divider(pdf)

  # Análise e Cruzamentos
  pdf = set_header(pdf)
  pdf.cell(w=None, h=None, text='Análise')
  pdf.ln(10)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Demonstrativo Orçamentário x Relação de Pagamentos')
  pdf.ln(7)

  pdf = set_text(pdf)
  pdf.cell(w=None, h=None, text='Cruzamento das planilhas "Demonstrativo Orçamentário" e "Relação de Pagamentos"')
  pdf.ln(7)
  pdf = create_pdf_table(pdf, elements[9])
  pdf = set_caption(pdf)
  pdf.ln(3)
  pdf.cell(w=None, h=None, text='[1] ORÇAMENTO EXECUTADO corresponde à coluna *VALOR* de Relação de Pagamentos')
  pdf.ln(3)
  pdf.cell(w=None, h=None, text='[2] Variação = ORÇAMENTO APROVADO [Demonstrativo Orçamentário] - ORÇAMENTO EXECUTADO')
  pdf.ln(7)

  pdf = set_subheader(pdf)
  pdf.cell(w=None, h=None, text='Balanço Geral')
  pdf.ln(7)
  pdf = create_pdf_table(pdf, elements[10])
  pdf = set_caption(pdf)
  pdf.ln(3)
  pdf.cell(w=None, h=None, text='[1] Valor de fomento = Transferências + Aplicações [Conciliação Bancária]')
  pdf.ln(3)
  pdf.cell(w=None, h=None, text='[2] Valor Total [Relação de Pagamentos]')
  pdf.ln(3)
  pdf.cell(w=None, h=None, text='[3] Devolução potencial = Valor de Fomento - Pagamentos [Conciliação Bancária]')
  pdf.ln(3)
  pdf.cell(w=None, h=None, text='[4] Relação de Execução Orçamentária = Valor Executado / Aporte Spcine (se maior que 100%, houve estouro de orçamento)')
  pdf.ln(3)

  return bytes(pdf.output())

def generate_excel_file(df):
  buffer = io.BytesIO()

  with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Conciliação Bancária')
    writer.close()

    st.space(size="large")
    with st.container(horizontal=True, horizontal_alignment='center'):
      st.download_button(
        label="Download",
        data=buffer,
        file_name="conciliacao_bancaria.xlsx",
        mime='mime="application/vnd.ms-excel"',
        type="primary"
      )
