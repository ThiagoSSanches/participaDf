from .regex_rules import contains_personal_data_regex, detect_personal_data_regex
from .ml_model import predict, predict_proba
import os

def detect_personal_data(text, threshold=0.35):
    """
    Detecta dados pessoais usando abordagem híbrida (regex + ML).
    
    Args:
        text (str): Texto para análise
        threshold (float): Limiar de confiança para ML (0.0 a 1.0)
        
    Returns:
        dict: {
            'contem_dados_pessoais': bool,
            'metodo': str ('regex', 'ml', 'hibrido'),
            'tipos_detectados': list,
            'confianca': float (0.0 a 1.0),
            'detalhes': dict
        }
    """
    # 1. PRIMEIRA CAMADA: Tentar regex
    resultado_regex = detect_personal_data_regex(text)
    
    if resultado_regex['detected']:
        # Se regex detectou, retornar com alta confiança
        return {
            'contem_dados_pessoais': True,
            'metodo': 'regex',
            'tipos_detectados': resultado_regex['tipos_detectados'],
            'confianca': 1.0,
            'detalhes': resultado_regex['detalhes']
        }
    
    # 2. SEGUNDA CAMADA: Se regex não detectou, tentar ML
    modelo_path = 'ml/modelo.pkl'
    vectorizer_path = 'ml/vectorizer.pkl'
    
    if os.path.exists(modelo_path) and os.path.exists(vectorizer_path):
        try:
            from .ml_model import predict_proba
            
            # Obter probabilidade do modelo ML
            confianca_ml = predict_proba(text)
            
            if confianca_ml >= threshold:
                return {
                    'contem_dados_pessoais': True,
                    'metodo': 'ml',
                    'tipos_detectados': ['Detectado por ML'],
                    'confianca': float(confianca_ml),
                    'detalhes': {'ml_score': float(confianca_ml)}
                }
            else:
                return {
                    'contem_dados_pessoais': False,
                    'metodo': 'ml',
                    'tipos_detectados': [],
                    'confianca': float(confianca_ml),
                    'detalhes': {'ml_score': float(confianca_ml)}
                }
        except Exception as e:
            # Se ML falhar, retornar resultado do regex
            return {
                'contem_dados_pessoais': False,
                'metodo': 'regex',
                'tipos_detectados': [],
                'confianca': 0.0,
                'detalhes': {'erro_ml': str(e)}
            }
    else:
        # Se modelo ML não existe, retornar apenas resultado do regex
        return {
            'contem_dados_pessoais': False,
            'metodo': 'regex',
            'tipos_detectados': [],
            'confianca': 0.0,
            'detalhes': {'modelo_nao_encontrado': True}
        }


def classify_request(text):
    """
    Classifica um pedido (compatibilidade com código legado).
    
    Args:
        text (str): Texto do pedido
        
    Returns:
        dict: Resultado da classificação
    """
    return detect_personal_data(text, threshold=0.35)


def batch_detect(texts, confidence_threshold=0.35):
    """
    Detecção em lote para processamento eficiente.
    
    Args:
        texts (list): Lista de textos
        confidence_threshold (float): Limiar ML
    
    Returns:
        list: Lista de dicionários com resultados
    """
    return [detect_personal_data(text, confidence_threshold) for text in texts]