import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report 
import joblib
import re

datasetpath = 'frases_dia_a_dia.csv'
df = pd.read_csv(datasetpath)

def limpar_texto(texto):
    texto = re.sub(r"http\S+", "", texto)        # remove URLs
    texto = re.sub(r"@\w+", "", texto)           # remove menções
    texto = texto.lower()                        # converte para minúsculas
    return texto.strip()

df['fraselimpa'] = df['Frase'].apply(limpar_texto)
df[['Frase', 'fraselimpa']].head(3)

X = df['fraselimpa']
y = df['Emocao']  

ymapeado = y.map({'Negativo': 0, 'Neutro': 1, 'Positivo': 2})

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)


vectorizer = TfidfVectorizer(max_features=500)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


model = LogisticRegression(max_iter=200)
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)

print("Acurácia:", round(accuracy_score(y_test, y_pred), 4))
print("\nRelatório de Classificação:\n")
print(classification_report(y_test, y_pred, target_names=['Negativo', 'Neutro', 'Positivo']))


joblib.dump(vectorizer, 'modelo_emocao/tfidf_vectorizer.pkl')
print("\nVectorizer salvo em 'tfidf_vectorizer.pkl'")

joblib.dump(model, 'modelo_emocao/sentiment_model.pkl')
print("Modelo de Regressão Logística salvo em 'sentiment_model.pkl'")