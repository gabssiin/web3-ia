import joblib
import os
import sys

vectorizer_path = 'modelo_emocao/tfidf_vectorizer.pkl'
model_path = 'modelo_emocao/sentiment_model.pkl'

try:
    if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Arquivos .pkl nao encontrados.")
        
    vectorizer_loaded = joblib.load(vectorizer_path)
    model_loaded = joblib.load(model_path)

except Exception as e:
    print(f"Erro ao carregar modelo/vectorizer: {e}")
    sys.exit(1)