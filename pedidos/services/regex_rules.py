import re

# CPF - formatos: 123.456.789-00, 12345678900, 123456789-00
CPF_REGEX = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'

# RG - formatos: 1234567, 12.345.678-9, MG-12.345.678, 1.234.567
RG_REGEX = r'\b([A-Z]{2}[-\s]?)?\d{1,2}\.?\d{3}\.?\d{3}[-\s]?[0-9Xx]?\b'

# Email - padrão completo
EMAIL_REGEX = r'\b[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

# Telefone - (61) 99999-9999, 61999999999, 9999-9999, +55 61 99999-9999
PHONE_REGEX = r'\b(\+?55\s?)?(\(?\d{2}\)?\s?)?([9]\d{4}|\d{4})[-\s]?\d{4}\b'

# Matrícula funcional - padrões: "matrícula 123456", "matricula: 123456"
MATRICULA_REGEX = r'\bmatr[ií]cula\s*:?\s*\d{4,8}\b'

# Endereço residencial - padrões expandidos
ADDRESS_PATTERNS = [
    r'\b(rua|avenida|av\.?|travessa|alameda|quadra|sq|cln|cls|clsw|shln)\s+[a-zA-Z0-9\s/]+,?\s*n[°º]?\s*\d+',
    r'\bCEP:?\s*\d{5}-?\d{3}\b',
    r'\b(apt|apto|apartamento|casa|bloco)\s*\d+',
    r'\b(Asa\s+(Sul|Norte)|Plano\s+Piloto|Taguatinga|Ceilândia|Samambaia)\b',
    r'\b(QS|QN|QR|QI|QE)\s*\d+',  # Quadras do DF
]

# Nomes próprios com contexto expandido
NAME_CONTEXT_PATTERNS = [
    r'\b(nome|paciente|servidor|servidora|beneficiário|beneficiária|requerente|solicitante|cidadão|cidadã|aluno|aluna|professor|professora|diretor|diretora|coordenador|coordenadora)\s*:?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    r'\b(Sr\.|Sra\.|Dr\.|Dra\.)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    r'\b(do\s+servidor|da\s+servidora|do\s+aluno|da\s+aluna)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
]

NAME_PATTERNS = [
    # Padrões formais
    r'\b(nome|paciente|servidor|servidora|beneficiário|beneficiária|requerente|solicitante|cidadão|cidadã|aluno|aluna)\s*:?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    r'\b(Sr\.|Sra\.|Dr\.|Dra\.)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    r'\b(do\s+servidor|da\s+servidora|do\s+aluno|da\s+aluna)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    
    # ← ADICIONAR NOVOS PADRÕES
    r'\b(me\s+chamo|meu\s+nome\s+é|eu\s+sou|chamo-me)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    r'\bEu,?\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){2,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+,',  # "Eu, Pablo Souza Ramos,"
    r'\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){2,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+,?\s+(portador|portadora|CPF|RG|matrícula)',  # "Pablo Souza Ramos, portador do CPF"
]

# Data de nascimento - contextos como "nascido em 01/01/1990"
BIRTHDATE_REGEX = r'\b(nascid[oa]|data\s+de\s+nascimento|DN)\s*(em|:)?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'

# Prontuários e números de identificação
ID_NUMBERS_PATTERNS = [
    r'\bprontu[áa]rio\s*:?\s*\d{4,10}\b',
    r'\bn[úu]mero\s+de\s+(registro|identifica[çc][ãa]o)\s*:?\s*\d{4,10}\b',
]


def contains_personal_data_regex(text):
    """
    Detecta dados pessoais usando regex otimizado para o dataset Participa DF.
    Retorna: (bool, list) - (contém_dados, tipos_detectados)
    """
    detected_types = []
    
    # CPF
    if re.search(CPF_REGEX, text, re.IGNORECASE):
        detected_types.append('CPF')
    
    # RG
    if re.search(RG_REGEX, text, re.IGNORECASE):
        detected_types.append('RG')
    
    # Email
    if re.search(EMAIL_REGEX, text, re.IGNORECASE):
        detected_types.append('Email')
    
    # Telefone
    if re.search(PHONE_REGEX, text):
        detected_types.append('Telefone')
    
    # Matrícula
    if re.search(MATRICULA_REGEX, text, re.IGNORECASE):
        detected_types.append('Matrícula')
    
    # Endereço
    for pattern in ADDRESS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            detected_types.append('Endereço')
            break
    
    # Nome próprio contextualizado
    for pattern in NAME_CONTEXT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            detected_types.append('Nome')
            break
    
    # Data de nascimento
    if re.search(BIRTHDATE_REGEX, text, re.IGNORECASE):
        detected_types.append('Data_Nascimento')
    
    # Prontuários e IDs
    for pattern in ID_NUMBERS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            detected_types.append('ID_Registro')
            break
    
    return len(detected_types) > 0, detected_types


def validate_cpf(cpf_string):
    """
    Valida CPF com dígitos verificadores (opcional - para reduzir falsos positivos).
    """
    cpf = re.sub(r'[^\d]', '', cpf_string)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Cálculo dos dígitos verificadores
    def calc_digit(cpf_partial):
        soma = sum(int(cpf_partial[i]) * (len(cpf_partial) + 1 - i) for i in range(len(cpf_partial)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    return calc_digit(cpf[:9]) == int(cpf[9]) and calc_digit(cpf[:10]) == int(cpf[10])

def detect_personal_data_regex(text):
    """
    Detecta dados pessoais usando apenas regex.
    """
    if not isinstance(text, str):
        return {'detected': False, 'tipos_detectados': [], 'detalhes': {}}
    
    tipos_detectados = []
    detalhes = {}
    
    # CPF
    cpf_match = re.search(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', text, re.IGNORECASE)
    if cpf_match:
        tipos_detectados.append('CPF')
        detalhes['cpf'] = cpf_match.group()
    
    # RG
    rg_match = re.search(r'\b([A-Z]{2}[-\s]?)?\d{1,2}\.?\d{3}\.?\d{3}[-\s]?[0-9Xx]?\b', text, re.IGNORECASE)
    if rg_match and not re.search(r'(processo|protocolo|licitação|contrato)\s*n?[°º]?\s*\d', text, re.IGNORECASE):
        tipos_detectados.append('RG')
        detalhes['rg'] = rg_match.group()
    
    # Email
    email_match = re.search(r'\b[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text, re.IGNORECASE)
    if email_match:
        tipos_detectados.append('Email')
        detalhes['email'] = email_match.group()
    
    # Telefone
    telefone_match = re.search(r'\b(\+?55\s?)?(\(?\d{2}\)?\s?)?([9]\d{4}|\d{4})[-\s]?\d{4}\b', text)
    if telefone_match:
        tipos_detectados.append('Telefone')
        detalhes['telefone'] = telefone_match.group()
    
    # Matrícula funcional
    matricula_match = re.search(r'\bmatr[ií]cula\s*:?\s*\d{4,8}\b', text, re.IGNORECASE)
    if matricula_match:
        tipos_detectados.append('Matrícula')
        detalhes['matricula'] = matricula_match.group()
    
    # Endereço residencial
    enderecos_patterns = [
        r'\b(rua|avenida|av\.?|travessa|alameda|quadra)\s+[a-zA-Z0-9\s/]+,?\s*n[°º]?\s*\d+',
        r'\bCEP:?\s*\d{5}-?\d{3}\b',
        r'\b(apt|apto|apartamento|casa|bloco)\s*\d+',
        r'\b(QS|QN|QR|QI|QE)\s*\d+\s+(conjunto|casa|lote)',
    ]
    for pattern in enderecos_patterns:
        endereco_match = re.search(pattern, text, re.IGNORECASE)
        if endereco_match:
            tipos_detectados.append('Endereço')
            detalhes['endereco'] = endereco_match.group()
            break
    
    # Nome próprio contextualizado - PADRÕES EXPANDIDOS
    nomes_contexto_patterns = [
        # Padrões formais
        r'\b(nome|paciente|servidor|servidora|beneficiário|beneficiária|requerente|solicitante|cidadão|cidadã|aluno|aluna)\s*:?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        r'\b(Sr\.|Sra\.|Dr\.|Dra\.)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        r'\b(do\s+servidor|da\s+servidora|do\s+aluno|da\s+aluna)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        
        # ← NOVOS PADRÕES
        r'\b(me\s+chamo|meu\s+nome\s+é|eu\s+sou|chamo-me)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        r'\bEu,?\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){2,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+,',
        r'\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){2,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+,?\s+(portador|portadora|CPF|RG|matrícula)',
    ]
    for pattern in nomes_contexto_patterns:
        nome_match = re.search(pattern, text, re.IGNORECASE)
        if nome_match:
            tipos_detectados.append('Nome')
            detalhes['nome'] = nome_match.group()
            break
    
    # Data de nascimento
    data_nasc_match = re.search(r'\b(nascid[oa]|data\s+de\s+nascimento|DN)\s*(em|:)?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text, re.IGNORECASE)
    if data_nasc_match:
        tipos_detectados.append('Data de Nascimento')
        detalhes['data_nascimento'] = data_nasc_match.group()
    
    # Prontuários
    prontuario_match = re.search(r'\bprontu[áa]rio\s*:?\s*\d{4,10}\b', text, re.IGNORECASE)
    if prontuario_match:
        tipos_detectados.append('Prontuário')
        detalhes['prontuario'] = prontuario_match.group()
    
    # Número SEI
    sei_match = re.search(r'\b(processo\s+SEI|SEI)\s*n?[°º]?\s*:?\s*\d{5,6}[-/]\d{8}[-/]\d{4}[-/]?\d{2}\b', text, re.IGNORECASE)
    if sei_match:
        tipos_detectados.append('Processo SEI')
        detalhes['processo_sei'] = sei_match.group()
    
    return {
        'detected': len(tipos_detectados) > 0,
        'tipos_detectados': tipos_detectados,
        'detalhes': detalhes
    }


def get_regex_patterns():
    """
    Retorna dicionário com todos os padrões regex usados.
    """
    return {
        'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'rg': r'\b([A-Z]{2}[-\s]?)?\d{1,2}\.?\d{3}\.?\d{3}[-\s]?[0-9Xx]?\b',
        'email': r'\b[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        'telefone': r'\b(\+?55\s?)?(\(?\d{2}\)?\s?)?([9]\d{4}|\d{4})[-\s]?\d{4}\b',
        'matricula': r'\bmatr[ií]cula\s*:?\s*\d{4,8}\b',
        'cep': r'\bCEP:?\s*\d{5}-?\d{3}\b',
        'endereco': r'\b(rua|avenida|av\.?|travessa|alameda|quadra)\s+[a-zA-Z0-9\s/]+,?\s*n[°º]?\s*\d+',
        'nome': r'\b(nome|paciente|servidor|servidora)\s*:?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        'data_nascimento': r'\b(nascid[oa]|data\s+de\s+nascimento|DN)\s*(em|:)?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'prontuario': r'\bprontu[áa]rio\s*:?\s*\d{4,10}\b',
        'processo_sei': r'\b(processo\s+SEI|SEI)\s*n?[°º]?\s*:?\s*\d{5,6}[-/]\d{8}[-/]\d{4}[-/]?\d{2}\b',
    }