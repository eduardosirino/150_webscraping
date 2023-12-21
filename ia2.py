import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer

# Exemplo de dados de treinamento
data = [
    {"text": "Imóvel com área útil de 120 m² e área total de 200 m².", "area_util": 120, "area_total": 200},
    # Mais dados...
]

# Função de pré-processamento e vetorização de texto
vectorizer = TfidfVectorizer()

def preprocess_text(text):
    return vectorizer.transform([text]).toarray()

# Preparação dos dados
texts = [d["text"] for d in data]
X = vectorizer.fit_transform(texts).toarray()
Y = np.array([[d['area_util'], d['area_total']] for d in data])

# Construção do Modelo
model = tf.keras.Sequential([
    tf.keras.layers.Dense(units=2, input_shape=[X.shape[1]])
])

# Compilação do Modelo
model.compile(optimizer='adam', loss='mean_squared_error')

# Treinamento do Modelo
model.fit(X, Y, epochs=10)  # Ajuste o número de épocas conforme necessário

# Função para fazer previsões
def get_areas(text):
    processed_text = preprocess_text(text)
    prediction = model.predict(processed_text)
    return [None if np.isnan(x) else x for x in prediction[0]]

