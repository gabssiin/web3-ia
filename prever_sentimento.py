import joblib
import os
import sys

vectorizer_path = 'modelo_emocao/tfidf_vectorizer.pkl'
model_path = 'modelo_emocao/sentiment_model.pkl'

try:
    # verifica se os arquivos existem
    if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Arquivos .pkl nao encontrados.")
        
    # carrega o vectorizer
    vectorizer_loaded = joblib.load(vectorizer_path)
    
    # carrega o modelo
    model_loaded = joblib.load(model_path)

except Exception as e:
    # mostra erro e encerra
    print(f"Erro ao carregar modelo/vectorizer: {e}")
    sys.exit(1)



# minhas funções auxiliares


def limpar_texto(texto):
    # remove links
    texto = re.sub(r"http\S+", "", texto)
    # remove menções
    texto = re.sub(r"@\w+", "", texto)
    # coloca tudo em minúsculas
    texto = texto.lower()
    return texto.strip()

def prever_sentimento_carregado(frase):
    #utilizando a função criada anteriormente
    texto_limpo = limpar_texto(frase)
    # cria vetor da frase
    vetor = vectorizer_loaded.transform([texto_limpo])
    # faz a previsão
    pred = model_loaded.predict(vetor)[0]
    return pred