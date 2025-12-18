import re

float_to_percentage_pattern = r"-?\d+\.\d{1,2}"

def format_currency(x):
  if x == "":
    return ""
  return f"R$ {x:,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")

def brl_to_float(brl_string):
  if not brl_string:
    return None
  
  cleaned_string = brl_string.replace('R$', '').replace('.', '').replace(',', '.').strip()

  return float(cleaned_string)


def format_percentage(s):
  if (re.match(float_to_percentage_pattern, s)):
    float_value = float(s)
    abs_value = abs(float_value)

    return f"{abs_value}%"
  return s

def format_df_cb(df, show_total=True):
  new_df = df.copy()
  new_df['DATA DE PAGAMENTO'] = new_df['DATA DE PAGAMENTO'].dt.strftime('%d-%m-%Y')

  columns_to_sum = [
    'TRANSFERÊNCIAS',
    'APLICAÇÕES / RESGATES',
    'PAGAMENTOS',
    'TARIFAS BANCÁRIAS'
  ]

  if show_total:
    numeric_sums = new_df[columns_to_sum].sum(axis=0)
    new_df.loc['Total', numeric_sums.index] = numeric_sums

  new_df = new_df.fillna('')

  number_columns = [
    'TRANSFERÊNCIAS',
    'APLICAÇÕES / RESGATES',
    'PAGAMENTOS',
    'TARIFAS BANCÁRIAS',
    'SALDO',
  ]

  new_df[number_columns] = new_df[number_columns].map(lambda x : format_currency(x))

  return new_df

def format_df(
    df,
    show_total=True,
    date_cols=None,
    currency_cols=None,
    columns_to_sum=None,
    percentage_cols=None
  ):
  new_df = df.copy()

  if date_cols:
    for col in date_cols:
      new_df[col] = new_df[col].dt.strftime('%d-%m-%Y')

  if show_total:
    numeric_sums = new_df[columns_to_sum].sum(axis=0)
    new_df.loc['Total', numeric_sums.index] = numeric_sums

  new_df = new_df.fillna('')

  if currency_cols:
    new_df[currency_cols] = new_df[currency_cols].map(lambda x : format_currency(x))

  if percentage_cols:
    new_df[percentage_cols] = new_df[percentage_cols].map(lambda x : format_percentage(x))

  return new_df
