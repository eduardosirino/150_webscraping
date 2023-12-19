from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

app = Flask(__name__)

# Exemplo de dados de treinamento (normalmente, isso seria feito offline)
dados = [
    {"texto": "Imóvel com área útil de 120 m² e área total de 200 m².", "area_util": 120, "area_total": 200},
    # Mais dados...
]

# Função de pré-processamento
def preprocessar_textos(textos):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(textos)
    return pad_sequences(tokenizer.texts_to_sequences(textos))

# Preparação dos dados
textos = [d["texto"] for d in dados]
X = preprocessar_textos(textos)
Y = np.array([[d['area_util'], d['area_total']] for d in dados])

# Construção do Modelo
model = tf.keras.models.Sequential([
    tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=64),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(2, activation='linear')
])

# Treinamento do Modelo (normalmente, isso seria feito offline)
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X, Y, epochs=10)

# Função para fazer previsões
def prever(texto):
    processed_text = preprocessar_textos([texto])
    predicao = model.predict(processed_text)[0]
    return [None if np.isnan(x) else x for x in predicao]

@app.route('/analise', methods=['POST'])
def analise():
    data = request.json
    texto = data.get('texto', '')
    resultado = prever(texto)
    return jsonify({'resultado': resultado})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500000)
