"""
Script para rotular automaticamente o dataset_teste.xlsx usando regex.

Este script analisa cada texto e atribui:
- label = 1 se detectar dados pessoais (CPF, RG, email, telefone, etc.)
- label = 0 se NÃO detectar dados pessoais

Após rotular, o dataset pode ser usado para treinamento.
"""

import pandas as pd
import re
import os

# Importar regras de regex
import sys
sys.path.append('pedidos/services')

def detectar_dados_pessoais_regex(texto):
    """
    Detecta dados pessoais usando regex.
    Retorna True se encontrar qualquer padrão de dados pessoais.
    """
    if not isinstance(texto, str):
        return False
    
    # CPF - formatos: 123.456.789-00, 12345678900
    if re.search(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', texto, re.IGNORECASE):
        return True
    
    # RG - formatos: 1234567, 12.345.678-9
    if re.search(r'\b([A-Z]{2}[-\s]?)?\d{1,2}\.?\d{3}\.?\d{3}[-\s]?[0-9Xx]?\b', texto, re.IGNORECASE):
        # Verificar se não é apenas um número de processo ou protocolo
        if not re.search(r'(processo|protocolo|licitação|contrato)\s*n?[°º]?\s*\d', texto, re.IGNORECASE):
            return True
    
    # Email
    if re.search(r'\b[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', texto, re.IGNORECASE):
        return True
    
    # Telefone - (61) 99999-9999, 61999999999
    if re.search(r'\b(\+?55\s?)?(\(?\d{2}\)?\s?)?([9]\d{4}|\d{4})[-\s]?\d{4}\b', texto):
        return True
    
    # Matrícula funcional
    if re.search(r'\bmatr[ií]cula\s*:?\s*\d{4,8}\b', texto, re.IGNORECASE):
        return True
    
    # Endereço residencial
    enderecos = [
        r'\b(rua|avenida|av\.?|travessa|alameda|quadra)\s+[a-zA-Z0-9\s/]+,?\s*n[°º]?\s*\d+',
        r'\bCEP:?\s*\d{5}-?\d{3}\b',
        r'\b(apt|apto|apartamento|casa|bloco)\s*\d+',
        r'\b(QS|QN|QR|QI|QE)\s*\d+\s+(conjunto|casa|lote)',
    ]
    for pattern in enderecos:
        if re.search(pattern, texto, re.IGNORECASE):
            return True
    
    # Nome próprio contextualizado
    nomes_contexto = [
        r'\b(nome|paciente|servidor|servidora|beneficiário|beneficiária|requerente|solicitante|cidadão|cidadã|aluno|aluna)\s*:?\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,5}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        r'\b(Sr\.|Sra\.|Dr\.|Dra\.)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
        r'\b(do\s+servidor|da\s+servidora|do\s+aluno|da\s+aluna)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+',
    ]
    for pattern in nomes_contexto:
        if re.search(pattern, texto, re.IGNORECASE):
            return True
    
    # Data de nascimento
    if re.search(r'\b(nascid[oa]|data\s+de\s+nascimento|DN)\s*(em|:)?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', texto, re.IGNORECASE):
        return True
    
    # Prontuários
    if re.search(r'\bprontu[áa]rio\s*:?\s*\d{4,10}\b', texto, re.IGNORECASE):
        return True
    
    return False


def main():
    print("\n" + "="*70)
    print("    ROTULAÇÃO AUTOMÁTICA DO DATASET")
    print("="*70)
    
    # Verificar possíveis localizações
    possiveis_caminhos = [
        'dataset_teste.xlsx',
        'ml/dataset_teste.xlsx',
        'Dataset_Teste.xlsx',
        'ml/Dataset_Teste.xlsx'
    ]
    
    arquivo_encontrado = None
    for caminho in possiveis_caminhos:
        if os.path.exists(caminho):
            arquivo_encontrado = caminho
            print(f"\n✓ Arquivo encontrado: {caminho}")
            break
    
    if not arquivo_encontrado:
        print("\n❌ ERRO: Arquivo dataset_teste.xlsx não encontrado!")
        return
    
    # Ler arquivo
    print(f"Lendo arquivo: {arquivo_encontrado}")
    df = pd.read_excel(arquivo_encontrado)
    
    print(f"\nTotal de registros: {len(df)}")
    print(f"Colunas: {df.columns.tolist()}")
    
    # Identificar coluna de texto
    coluna_texto = None
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'texto' in col_lower or 'text' in col_lower or 'mascarado' in col_lower:
            coluna_texto = col
            break
    
    if not coluna_texto:
        for col in df.columns:
            if col.lower() != 'id':
                coluna_texto = col
                break
    
    if not coluna_texto:
        print("❌ ERRO: Não foi possível identificar a coluna de texto!")
        return
    
    print(f"✓ Coluna de texto: '{coluna_texto}'")
    
    # Rotular automaticamente
    print("\n" + "="*70)
    print("ROTULANDO TEXTOS (usando regex)...")
    print("="*70)
    
    labels = []
    deteccoes = []
    
    for idx, texto in enumerate(df[coluna_texto], 1):
        tem_dados_pessoais = detectar_dados_pessoais_regex(texto)
        label = 1 if tem_dados_pessoais else 0
        labels.append(label)
        
        status = "✓ COM dados pessoais" if label == 1 else "○ SEM dados pessoais"
        print(f"[{idx}/{len(df)}] {status} - {texto[:60]}...")
        
        deteccoes.append({
            'texto': texto,
            'label': label
        })
    
    # Criar dataset rotulado
    df_rotulado = pd.DataFrame(deteccoes)
    
    # Estatísticas
    print("\n" + "="*70)
    print("ESTATÍSTICAS DA ROTULAÇÃO")
    print("="*70)
    
    total_com_pii = (df_rotulado['label'] == 1).sum()
    total_sem_pii = (df_rotulado['label'] == 0).sum()
    
    print(f"\nTotal de textos: {len(df_rotulado)}")
    print(f"COM dados pessoais (label=1): {total_com_pii} ({total_com_pii/len(df_rotulado)*100:.1f}%)")
    print(f"SEM dados pessoais (label=0): {total_sem_pii} ({total_sem_pii/len(df_rotulado)*100:.1f}%)")
    
    # Criar pasta ml se não existir
    if not os.path.exists('ml'):
        os.makedirs('ml')
    
    # Salvar dataset rotulado
    df_rotulado.to_csv('ml/dataset.csv', index=False, encoding='utf-8')
    print(f"\n✓ Dataset rotulado salvo em: ml/dataset.csv")
    
    # Salvar também em Excel para revisão manual
    df_rotulado.to_excel('ml/dataset_rotulado.xlsx', index=False)
    print(f"✓ Cópia em Excel salva em: ml/dataset_rotulado.xlsx")
    
    # Mostrar exemplos
    print("\n" + "="*70)
    print("EXEMPLOS DE ROTULAÇÃO")
    print("="*70)
    
    print("\n▸ Exemplos COM dados pessoais (label=1):")
    exemplos_positivos = df_rotulado[df_rotulado['label'] == 1]['texto'].head(3)
    for i, texto in enumerate(exemplos_positivos, 1):
        print(f"  {i}. {texto[:80]}...")
    
    print("\n▸ Exemplos SEM dados pessoais (label=0):")
    exemplos_negativos = df_rotulado[df_rotulado['label'] == 0]['texto'].head(3)
    for i, texto in enumerate(exemplos_negativos, 1):
        print(f"  {i}. {texto[:80]}...")
    
    print("\n" + "="*70)
    print("✓ ROTULAÇÃO CONCLUÍDA COM SUCESSO")
    print("="*70)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. REVISAR (opcional): Abra ml/dataset_rotulado.xlsx e verifique se as rotulações estão corretas")
    print("   2. TREINAR: Execute 'python manage.py treinar_modelo'")
    print("   3. TESTAR: Execute 'python manage.py testar_dataset'")
    print("   4. ou execute tudo: 'python executar_teste_completo.py'")
    
    print("\n💡 DICA:")
    print("   A rotulação automática usa apenas regex (sem ML)")
    print("   Se encontrar erros, você pode corrigir manualmente em ml/dataset_rotulado.xlsx")
    print("   Depois salve como ml/dataset.csv e treine novamente")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()