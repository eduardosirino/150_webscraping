import numpy as np
import flask
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression

app = flask.Flask(__name__)

# Exemplo de dados de treinamento (normalmente, isso seria feito offline)
data = [
    {"text": "Imóvel com área útil de 120 m² e área total de 200 m².", "area_util": 120, "area_total": 200},
    # Mais dados...
]

# Função de pré-processamento
def preprocess_text(text):
    vectorizer = TfidfVectorizer()
    return vectorizer.fit_transform([text])

# Preparação dos dados
texts = [d["text"] for d in data]
X = preprocess_text(texts)
Y = np.array([[d['area_util'], d['area_total']] for d in data])

# Construção do Modelo
model = LinearRegression()

# Treinamento do Modelo (normalmente, isso seria feito offline)
model.fit(X, Y)

# Função para fazer previsões
def predict(text):
    processed_text = preprocess_text(text)
    prediction = model.predict(processed_text)
    return [None if np.isnan(x) else x for x in prediction]

@app.route('/analyse', methods=['POST'])
def analyse():
    data = flask.request.json
    text = data.get('text', '')
    result = predict(text)
    return flask.jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500000)