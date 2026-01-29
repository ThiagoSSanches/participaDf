"""
Script principal para executar teste completo no dataset do hackathon.
"""

import subprocess
import sys
import os

def executar_comando(comando, descricao):
    """Executa um comando shell e exibe o status."""
    print(f"\n{'='*70}")
    print(f">>> {descricao}")
    print(f"{'='*70}")
    
    resultado = subprocess.run(comando, shell=True)
    
    if resultado.returncode != 0:
        print(f"\n❌ ERRO ao executar: {comando}")
        sys.exit(1)
    
    print(f"✓ Concluído com sucesso")


def main():
    print("\n" + "="*70)
    print("    EXECUÇÃO COMPLETA - HACKATHON PARTICIPA DF")
    print("="*70)
    
    # Verificar pré-requisitos
    print("\n>>> Verificando pré-requisitos...")
    
    dataset_paths = [
        'dataset_teste.xlsx',
        'ml/dataset_teste.xlsx',
        'Dataset_Teste.xlsx',
        'ml/Dataset_Teste.xlsx'
    ]
    
    dataset_encontrado = None
    for caminho in dataset_paths:
        if os.path.exists(caminho):
            dataset_encontrado = caminho
            print(f"✓ Dataset encontrado: {caminho}")
            break
    
    if not dataset_encontrado:
        print("\n❌ ERRO: dataset_teste.xlsx não encontrado!")
        sys.exit(1)
    
    if not os.path.exists("ml"):
        os.makedirs("ml")
    
    # Passo 1: Rotular dataset automaticamente
    executar_comando(
        "python rotular_dataset.py",
        "PASSO 1/4: Rotulando dataset automaticamente (usando regex)"
    )
    
    # Passo 2: Treinar modelo
    executar_comando(
        "python manage.py treinar_modelo",
        "PASSO 2/4: Treinando modelo ML com dataset rotulado"
    )
    
    # Passo 3: Testar apenas regex
    executar_comando(
        "python manage.py testar_dataset --only-regex",
        "PASSO 3/4: Testando APENAS REGEX (baseline)"
    )
    
    # Passo 4: Testar híbrido com diferentes thresholds
    print(f"\n{'='*70}")
    print(">>> PASSO 4/4: Testando Modelo Híbrido")
    print(f"{'='*70}")
    
    executar_comando(
        "python manage.py testar_dataset --threshold 0.35",
        "  4a) Threshold 0.35 (Balanceado - RECOMENDADO)"
    )
    
    executar_comando(
        "python manage.py testar_dataset --threshold 0.30",
        "  4b) Threshold 0.30 (Alta Sensibilidade)"
    )
    
    executar_comando(
        "python manage.py testar_dataset --threshold 0.40",
        "  4c) Threshold 0.40 (Alta Precisão)"
    )
    
    # Resumo
    print("\n" + "="*70)
    print("    ✓ TESTES CONCLUÍDOS COM SUCESSO!")
    print("="*70)
    
    print("\n📂 ARQUIVOS GERADOS:")
    print("   ✓ ml/dataset.csv              - Dataset rotulado")
    print("   ✓ ml/dataset_rotulado.xlsx    - Dataset rotulado (Excel)")
    print("   ✓ ml/modelo.pkl               - Modelo treinado")
    print("   ✓ ml/vectorizer.pkl           - Vetorizador TF-IDF")
    print("   ✓ resultado_teste.xlsx        - Resultados dos testes")
    
    print("\n📊 PRÓXIMOS PASSOS:")
    print("   1. Abra 'resultado_teste.xlsx' para análise detalhada")
    print("   2. Verifique métricas P1 (F1-Score) no console acima")
    print("   3. Se necessário, ajuste labels em ml/dataset_rotulado.xlsx")
    print("   4. Execute API: python manage.py runserver")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)