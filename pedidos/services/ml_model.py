import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
import numpy as np


# Lista de stopwords em português (palavras comuns que podem ser removidas)
STOPWORDS_PT = [
    'a', 'o', 'e', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as', 'dos', 'das',
    'para', 'com', 'por', 'no', 'na', 'ao', 'aos', 'à', 'às', 'é', 'que', 'se',
    'como', 'mais', 'foi', 'tem', 'são', 'essa', 'esse', 'isso', 'esta', 'este',
    'muito', 'já', 'também', 'só', 'pelo', 'pela', 'ou', 'quando', 'mesmo', 'sem'
]


def train_model(texts, labels):
    """
    Treina um modelo ensemble para detecção de dados pessoais.
    
    Args:
        texts (list): Lista de textos
        labels (list): Lista de labels (0 ou 1)
    """
    print("\n" + "="*60)
    print("TREINANDO MODELO ML")
    print("="*60)
    
    # Vetorização TF-IDF
    print("\n1. Vetorizando textos (TF-IDF)...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),
        min_df=2,
        stop_words=STOPWORDS_PT  # ← CORREÇÃO AQUI
    )
    X = vectorizer.fit_transform(texts)
    y = np.array(labels)
    
    print(f"   Dimensão do vetor: {X.shape}")
    print(f"   Total de features: {len(vectorizer.get_feature_names_out())}")
    
    # Criar ensemble de classificadores
    print("\n2. Criando ensemble de classificadores...")
    clf1 = LogisticRegression(max_iter=1000, random_state=42)
    clf2 = RandomForestClassifier(n_estimators=100, random_state=42)
    clf3 = MultinomialNB()
    
    modelo = VotingClassifier(
        estimators=[
            ('lr', clf1),
            ('rf', clf2),
            ('nb', clf3)
        ],
        voting='soft'
    )
    
    # Validação cruzada
    print("\n3. Validação cruzada (5 folds)...")
    scores = cross_val_score(modelo, X, y, cv=5, scoring='f1')
    print(f"   F1-Score por fold: {scores}")
    print(f"   F1-Score médio: {scores.mean():.4f} (+/- {scores.std():.4f})")
    
    # Treinar modelo final
    print("\n4. Treinando modelo final...")
    modelo.fit(X, y)
    
    # Salvar modelo e vectorizer
    os.makedirs('ml', exist_ok=True)
    joblib.dump(modelo, 'ml/modelo.pkl')
    joblib.dump(vectorizer, 'ml/vectorizer.pkl')
    
    print("\n✓ Modelo salvo em: ml/modelo.pkl")
    print("✓ Vectorizer salvo em: ml/vectorizer.pkl")
    print("\n" + "="*60)


def predict(text):
    """Prediz se texto contém dados pessoais (retorna 0 ou 1)."""
    modelo = joblib.load('ml/modelo.pkl')
    vectorizer = joblib.load('ml/vectorizer.pkl')
    
    X = vectorizer.transform([text])
    return modelo.predict(X)[0]


def predict_proba(text):
    """Retorna probabilidade de conter dados pessoais (0.0 a 1.0)."""
    modelo = joblib.load('ml/modelo.pkl')
    vectorizer = joblib.load('ml/vectorizer.pkl')
    
    X = vectorizer.transform([text])
    return modelo.predict_proba(X)[0][1]  # Probabilidade da classe 1