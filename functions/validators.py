import re

def validar_cpf(cpf):
  cpf = re.sub(r'\D', '', cpf)

  if len(cpf) != 11:
    return False

  if cpf == cpf[0] * 11:
    return False

  def calcular_digito(cpf, peso):
    soma = sum(int(cpf[i]) * peso[i] for i in range(len(peso)))
    resto = soma % 11
  
    return '0' if resto < 2 else str(11 - resto)

  peso_1 = list(range(10, 1, -1))
  peso_2 = list(range(11, 1, -1))

  digito1 = calcular_digito(cpf, peso_1)
  digito2 = calcular_digito(cpf, peso_2)

  return cpf[-2:] == digito1 + digito2


def validar_cnpj(cnpj):
  cnpj = re.sub(r'\D', '', cnpj)

  if len(cnpj) != 14:
    return False

  if cnpj == cnpj[0] * 14:
    return False

  def calcular_digito(cnpj, peso):
    soma = sum(int(cnpj[i]) * peso[i] for i in range(len(peso)))
    resto = soma % 11

    return '0' if resto < 2 else str(11 - resto)

  peso_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
  peso_2 = [6] + peso_1

  digito1 = calcular_digito(cnpj, peso_1)
  digito2 = calcular_digito(cnpj, peso_2)

  return cnpj[-2:] == digito1 + digito2

def validar_documento(doc):
  if doc == None or str(doc) == 'nan':
    return False
  
  len_digits = len(re.sub(r'\D', '', doc))

  if len_digits == 11:
    return validar_cpf(doc)
  elif len_digits == 14:
    return validar_cnpj(doc)
  else:
    return False
