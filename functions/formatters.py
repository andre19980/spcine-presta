def format_currency(x):
  return f"R$ {x:,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
