import pandas as pd
import os

# Verificar possíveis localizações do arquivo
possiveis_caminhos = [
    'dataset_teste.xlsx',           # Raiz
    'ml/dataset_teste.xlsx',        # Pasta ml
    'Dataset_Teste.xlsx',           # Variação de nome
    'ml/Dataset_Teste.xlsx'
]

# Encontrar arquivo
arquivo_encontrado = None
for caminho in possiveis_caminhos:
    if os.path.exists(caminho):
        arquivo_encontrado = caminho
        print(f"✓ Arquivo encontrado: {caminho}")
        break

if not arquivo_encontrado:
    print("❌ ERRO: Arquivo dataset_teste.xlsx não encontrado!")
    print("\nLocais verificados:")
    for caminho in possiveis_caminhos:
        print(f"  - {caminho}")
    print("\nPor favor, coloque o arquivo em uma das localizações acima.")
    exit(1)

# Ler o arquivo de teste
print(f"\nLendo arquivo: {arquivo_encontrado}")
df = pd.read_excel(arquivo_encontrado)

# Verificar estrutura
print("\n" + "="*60)
print("ESTRUTURA DO DATASET")
print("="*60)
print(df.head())
print(f"\nTotal de registros: {len(df)}")
print(f"Colunas: {df.columns.tolist()}")

# Padronizar nomes de colunas
# Mapear possíveis variações de nome
coluna_texto = None
coluna_label = None

for col in df.columns:
    col_lower = col.lower().strip()
    if 'texto' in col_lower or 'text' in col_lower:
        coluna_texto = col
    if 'label' in col_lower or 'classe' in col_lower or 'categoria' in col_lower:
        coluna_label = col

# Se não encontrou coluna de texto, usar a primeira que não seja ID
if not coluna_texto:
    for col in df.columns:
        if col.lower() != 'id':
            coluna_texto = col
            break

if not coluna_texto:
    print("❌ ERRO: Não foi possível identificar a coluna de texto!")
    exit(1)

print(f"\n✓ Coluna de texto identificada: '{coluna_texto}'")

# Renomear colunas para padronizar
df_processado = pd.DataFrame()
df_processado['texto'] = df[coluna_texto]

# Se tem label, usar; senão, criar coluna vazia
if coluna_label:
    df_processado['label'] = df[coluna_label]
    print(f"✓ Coluna de label identificada: '{coluna_label}'")
    
    # Contar distribuição de classes
    print("\n" + "="*60)
    print("DISTRIBUIÇÃO DE CLASSES")
    print("="*60)
    print(df_processado['label'].value_counts())
    print(f"\nPositivos (label=1): {(df_processado['label'] == 1).sum()}")
    print(f"Negativos (label=0): {(df_processado['label'] == 0).sum()}")
else:
    print("\n⚠️  AVISO: Dataset não possui coluna 'label'")
    print("   Será criada uma coluna 'label' vazia para compatibilidade")
    print("   Este dataset será usado APENAS para predição, não para treinamento")
    df_processado['label'] = -1  # -1 indica que não tem label

# Criar pasta ml se não existir
if not os.path.exists('ml'):
    os.makedirs('ml')
    print("\n✓ Pasta ml/ criada")

# Salvar em CSV para uso no treinamento/teste
df_processado.to_csv('ml/dataset.csv', index=False, encoding='utf-8')
print("\n✓ Dataset salvo em ml/dataset.csv")

# Análise de padrões (apenas se tiver labels)
if coluna_label:
    print("\n" + "="*60)
    print("ANÁLISE DE PADRÕES")
    print("="*60)

    positivos = df_processado[df_processado['label'] == 1]['texto'].tolist()
    print(f"\nExemplos COM dados pessoais ({len(positivos)}):")
    for i, texto in enumerate(positivos[:3], 1):
        print(f"{i}. {texto[:100]}...")

    negativos = df_processado[df_processado['label'] == 0]['texto'].tolist()
    print(f"\nExemplos SEM dados pessoais ({len(negativos)}):")
    for i, texto in enumerate(negativos[:3], 1):
        print(f"{i}. {texto[:100]}...")
else:
    print("\n" + "="*60)
    print("AMOSTRA DE TEXTOS")
    print("="*60)
    print("\nPrimeiros 5 textos:")
    for i, texto in enumerate(df_processado['texto'].head(), 1):
        print(f"{i}. {texto[:100]}...")

print("\n" + "="*60)
print("✓ PREPARAÇÃO CONCLUÍDA COM SUCESSO")
print("="*60)

# Informação adicional
if not coluna_label:
    print("\n" + "="*60)
    print("⚠️  IMPORTANTE: Dataset sem labels")
    print("="*60)
    print("Como o dataset não possui a coluna 'label', você tem 2 opções:")
    print("\n1. PREDIÇÃO (usar modelo já treinado):")
    print("   - Treine o modelo com outro dataset que tenha labels")
    print("   - Use este dataset apenas para fazer predições")
    print("\n2. ROTULAÇÃO MANUAL:")
    print("   - Abra ml/dataset.csv")
    print("   - Adicione valores 0 ou 1 na coluna 'label'")
    print("   - 0 = sem dados pessoais, 1 = com dados pessoais")
    print("   - Salve e execute o treinamento")