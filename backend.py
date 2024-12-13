from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
def conectar():
    return mysql.connector.connect(
        host="localhost",  # Pode ser parametrizado se necessário
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

# 1. Cadastrar um local visitado
@app.route('/cadastrar-local', methods=['POST'])
def cadastrar_local():
    dados = request.json
    nome = dados.get('nome', 'Sem Nome')
    descricao = dados.get('descricao', 'Sem descrição')
    latitude = dados['latitude']
    longitude = dados['longitude']

    conn = conectar()
    cursor = conn.cursor()
    query = """
    INSERT INTO locais_visitados (nome, descricao, localizacao)
    VALUES (%s, %s, ST_GeomFromText(%s, 4326))
    """
    ponto = f"POINT({longitude} {latitude})"
    cursor.execute(query, (nome, descricao, ponto))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Local visitado cadastrado com sucesso!'})

# 2. Listar ONGs no mapa
@app.route('/ongs', methods=['GET'])
def listar_ongs():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, descricao, ST_X(localizacao) AS longitude, ST_Y(localizacao) AS latitude FROM ongs")
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

# 3. Buscar ONGs dentro de um raio
@app.route('/ongs-raio', methods=['GET'])
def ongs_raio():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    raio = float(request.args.get('raio'))  # Raio em metros

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    ponto = f"POINT({longitude} {latitude})"
    query = """
    SELECT id, nome, descricao, ST_X(localizacao) AS longitude, ST_Y(localizacao) AS latitude,
           ST_Distance_Sphere(localizacao, ST_GeomFromText(%s, 4326)) AS distancia
    FROM ongs
    WHERE ST_Distance_Sphere(localizacao, ST_GeomFromText(%s, 4326)) <= %s
    """
    cursor.execute(query, (ponto, ponto, raio))
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

# 4. Buscar ONGs dentro de um polígono
@app.route('/ongs-poligono', methods=['POST'])
def ongs_poligono():
    dados = request.json
    poligono = dados['polygon']  # Coordenadas no formato WKT

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT id, nome, descricao, ST_X(localizacao) AS longitude, ST_Y(localizacao) AS latitude
    FROM ongs
    WHERE ST_Within(localizacao, ST_GeomFromText(%s, 4326))
    """
    cursor.execute(query, (poligono,))
    resultados = cursor.fetchall()
    conn.close()

    return jsonify(resultados)

# Rota Flask para buscar os locais visitados:
@app.route('/locais-visitados', methods=['GET'])
def listar_locais_visitados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nome, descricao, ST_X(localizacao) AS longitude, ST_Y(localizacao) AS latitude FROM locais_visitados")
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

# Inicializar o servidor
if __name__ == '__main__':
    app.run(debug=True)
