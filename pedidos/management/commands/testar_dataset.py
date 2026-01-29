from django.core.management.base import BaseCommand
import pandas as pd
import os
from pedidos.services.detector import detect_personal_data
from sklearn.metrics import classification_report, confusion_matrix, f1_score


class Command(BaseCommand):
    help = 'Testa o modelo no dataset de teste'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only-regex',
            action='store_true',
            help='Testa apenas com regex (sem ML)',
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.35,
            help='Threshold de confiança para classificação (padrão: 0.35)',
        )

    def handle(self, *args, **options):
        only_regex = options['only_regex']
        threshold = options['threshold']
        
        # Procurar arquivo em múltiplas localizações
        possiveis_caminhos = [
            'ml/dataset.csv',           # Dataset rotulado
            'dataset_teste.xlsx',       # Raiz
            'ml/dataset_teste.xlsx',    # Pasta ml
        ]
        
        file_path = None
        for caminho in possiveis_caminhos:
            if os.path.exists(caminho):
                file_path = caminho
                break
        
        if not file_path:
            self.stdout.write(self.style.ERROR('❌ Dataset não encontrado!'))
            self.stdout.write('\nLocais verificados:')
            for caminho in possiveis_caminhos:
                self.stdout.write(f'  - {caminho}')
            return
        
        self.stdout.write(f'\n✓ Usando dataset: {file_path}')
        
        # Carregar dataset
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Verificar se tem coluna 'label'
        if 'label' not in df.columns:
            self.stdout.write(self.style.ERROR('\n❌ Dataset não possui coluna "label"!'))
            self.stdout.write('Use o dataset rotulado em ml/dataset.csv')
            return
        
        # Identificar coluna de texto
        coluna_texto = None
        for col in ['texto', 'Texto Mascarado', 'text']:
            if col in df.columns:
                coluna_texto = col
                break
        
        if not coluna_texto:
            self.stdout.write(self.style.ERROR('❌ Coluna de texto não encontrada!'))
            return
        
        self.stdout.write(f'✓ Coluna de texto: {coluna_texto}')
        
        # Fazer predições
        self.stdout.write('\n' + '='*70)
        modo = 'APENAS REGEX' if only_regex else f'HÍBRIDO (threshold={threshold})'
        self.stdout.write(f'TESTANDO - {modo}')
        self.stdout.write('='*70)
        
        y_true = []
        y_pred = []
        resultados_detalhados = []
        
        for idx, row in df.iterrows():
            texto = row[coluna_texto]
            label_real = row['label']
            
            # Fazer predição
            if only_regex:
                # Forçar uso apenas de regex
                from pedidos.services.regex_rules import detect_personal_data_regex
                resultado = detect_personal_data_regex(texto)
                predicao = 1 if resultado['detected'] else 0
                confianca = 1.0 if predicao == 1 else 0.0
                metodo = 'regex'
            else:
                # Usar detector híbrido
                resultado = detect_personal_data(texto, threshold=threshold)
                predicao = 1 if resultado['contem_dados_pessoais'] else 0
                confianca = resultado['confianca']
                metodo = resultado['metodo']
            
            y_true.append(label_real)
            y_pred.append(predicao)
            
            resultados_detalhados.append({
                'texto': texto,  # ← TEXTO COMPLETO (SEM TRUNCAMENTO)
                'label_real': label_real,
                'predicao': predicao,
                'metodo': metodo,
                'confianca': confianca,
                'acertou': label_real == predicao
            })
            
            # Mostrar progresso (truncado apenas para exibição no terminal)
            status = '✓' if label_real == predicao else '✗'
            self.stdout.write(
                f'[{idx+1}/{len(df)}] {status} Real={label_real} Pred={predicao} '
                f'Conf={confianca:.2f} | {texto[:60]}...'
            )
        
        # Calcular métricas
        self.stdout.write('\n' + '='*70)
        self.stdout.write('RESULTADOS')
        self.stdout.write('='*70)
        
        # Relatório de classificação
        self.stdout.write('\n' + classification_report(
            y_true, y_pred,
            target_names=['Sem Dados Pessoais', 'Com Dados Pessoais'],
            digits=4
        ))
        
        # Matriz de confusão
        cm = confusion_matrix(y_true, y_pred)
        self.stdout.write('\nMatriz de Confusão:')
        self.stdout.write(f'                 Predito: Sem PII  Predito: Com PII')
        self.stdout.write(f'Real: Sem PII         {cm[0][0]:5d}           {cm[0][1]:5d}')
        self.stdout.write(f'Real: Com PII         {cm[1][0]:5d}           {cm[1][1]:5d}')
        
        # F1-Score
        f1 = f1_score(y_true, y_pred)
        self.stdout.write(f'\n📊 F1-Score: {f1:.4f}')
        
        # Salvar resultados detalhados COM TEXTO COMPLETO
        df_resultado = pd.DataFrame(resultados_detalhados)
        output_file = 'resultado_teste.xlsx'
        
        # Configurar Excel com largura de coluna maior para texto completo
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_resultado.to_excel(writer, index=False, sheet_name='Resultados')
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Resultados']
            worksheet.column_dimensions['A'].width = 120  # Coluna 'texto' - MUITO LARGA
            worksheet.column_dimensions['B'].width = 15   # label_real
            worksheet.column_dimensions['C'].width = 15   # predicao
            worksheet.column_dimensions['D'].width = 15   # metodo
            worksheet.column_dimensions['E'].width = 15   # confianca
            worksheet.column_dimensions['F'].width = 15   # acertou
        
        self.stdout.write(f'\n✓ Resultados salvos em: {output_file}')
        
        # Análise de erros
        erros = df_resultado[~df_resultado['acertou']]
        if len(erros) > 0:
            self.stdout.write('\n' + '='*70)
            self.stdout.write(f'ANÁLISE DE ERROS ({len(erros)} erros)')
            self.stdout.write('='*70)
            
            # Falsos positivos
            falsos_positivos = erros[erros['predicao'] == 1]
            if len(falsos_positivos) > 0:
                self.stdout.write(f'\n⚠️  Falsos Positivos: {len(falsos_positivos)}')
                for i, row in falsos_positivos.head(3).iterrows():
                    texto_preview = row["texto"][:100] + '...' if len(row["texto"]) > 100 else row["texto"]
                    self.stdout.write(f'  - {texto_preview}')
            
            # Falsos negativos
            falsos_negativos = erros[erros['predicao'] == 0]
            if len(falsos_negativos) > 0:
                self.stdout.write(f'\n⚠️  Falsos Negativos: {len(falsos_negativos)}')
                for i, row in falsos_negativos.head(3).iterrows():
                    texto_preview = row["texto"][:100] + '...' if len(row["texto"]) > 100 else row["texto"]
                    self.stdout.write(f'  - {texto_preview}')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('✓ TESTE CONCLUÍDO')
        self.stdout.write('='*70)