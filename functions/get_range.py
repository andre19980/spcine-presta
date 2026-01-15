def get_range(start_indicator_text, end_indicator_text, worksheet):
  interval = None
  start_line = None
  end_line = None

  for row in worksheet.iter_rows():
    for cell in row:
      if cell.value is not None:
        cell_value = str(cell.value).strip().lower()

        if cell_value == start_indicator_text:
          start_line = cell.row

        if cell_value == end_indicator_text:
          end_line = cell.row
          break
      
    if end_line is not None:
      interval = (start_line, end_line)
      break

  return interval

def get_range_conciliacao_bancaria(start_indicator_text, end_indicator_text, worksheet):
  interval = None
  start_line = None
  start_col = None
  end_line = None
  end_col = None

  for row in worksheet.iter_rows():
    for cell in row:
      if cell.value is not None:
        cell_value = str(cell.value).strip().lower()

        if cell_value == start_indicator_text:
          start_line = cell.row
          start_col = cell.column

        if start_line is not None and cell.row == start_line and cell_value == 'saldo':
          end_col = cell.column

        if cell_value == end_indicator_text:
          end_line = cell.row
          break
      
    if end_line is not None:
      interval = [(start_line, start_col), (end_line, end_col)]
      break

  return interval