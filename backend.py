from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import traceback

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

# 3. Buscar ONGs dentro de um raio(com topografia)
@app.route('/ongs-raio', methods=['GET'])
def ongs_raio():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    raio = float(request.args.get('raio'))  # Raio em metros

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    ponto = f"POINT({longitude} {latitude})"
    query = """
    SELECT ongs.id, ongs.nome, ongs.descricao, 
           ST_X(ongs.localizacao) AS longitude, 
           ST_Y(ongs.localizacao) AS latitude,
           ST_Distance_Sphere(ongs.localizacao, ST_GeomFromText(%s, 4326)) AS distancia,
           topografia.tipo_topografia, 
           topografia.altitude
    FROM ongs
    LEFT JOIN topografia ON ongs.id = topografia.local_id
    WHERE ST_Distance_Sphere(ongs.localizacao, ST_GeomFromText(%s, 4326)) <= %s
    """
    cursor.execute(query, (ponto, ponto, raio))
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

# 4. Buscar ONGs dentro de um polígono(com topografia)
@app.route('/ongs-poligono', methods=['POST'])
def ongs_poligono():
    dados = request.json
    poligono = dados['polygon']  # Coordenadas no formato WKT
    
    # Extrair os pontos do WKT e inverter lat/lon para lon/lat
    try:
        pontos = poligono.replace("POLYGON((", "").replace("))", "").split(", ")
        coordenadas = []
        for ponto in pontos:
            ponto = ponto.strip('()')  # Remover parênteses ao redor de cada ponto
            lat, lon = map(float, ponto.split())  # Separar e converter corretamente
            coordenadas.append(f"{lon} {lat}")  # Inverter para lon, lat

        # Fechar o polígono (opcional, mas importante para evitar erros)
        if coordenadas[0] != coordenadas[-1]:
            coordenadas.append(coordenadas[0])

        # Recriar o WKT com os valores invertidos
        wkt = f"POLYGON(({', '.join(coordenadas)}))"
    except Exception as e:
        return jsonify({"error": f"Erro ao processar as coordenadas: {str(e)}"}), 400

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT ongs.id, ongs.nome, ongs.descricao, 
           ST_X(ongs.localizacao) AS longitude, 
           ST_Y(ongs.localizacao) AS latitude,
           topografia.tipo_topografia, 
           topografia.altitude
    FROM ongs
    LEFT JOIN topografia ON ongs.id = topografia.local_id
    WHERE ST_Within(ongs.localizacao, ST_GeomFromText(%s, 4326))
    """
    cursor.execute(query, (wkt,))  # Usando wkt ao invés de poligono
    resultados = cursor.fetchall()
    conn.close()

    return jsonify(resultados)


#5 Buscar ONGs dentro de um raio (por linha)
@app.route('/ongs-linha-raio', methods=['GET'])
def ongs_linha_raio():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    raio = float(request.args.get('raio'))  # Raio em metros
    
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    # Ponto central da busca
    ponto = f"POINT({longitude} {latitude})"
    
    query = """
    SELECT id, nome, descricao,
           ST_AsText(trajeto) AS linha,
           ST_Distance(ST_Transform(trajeto, 3857), 
                       ST_Transform(ST_GeomFromText(%s, 4326), 3857)) AS distancia
    FROM linhas
    WHERE ST_Distance(ST_Transform(trajeto, 3857), 
                      ST_Transform(ST_GeomFromText(%s, 4326), 3857)) <= %s;
    """
    cursor.execute(query, (ponto, ponto, raio))
    resultados = cursor.fetchall()
    conn.close()
    
    return jsonify(resultados)

# 6. Buscar ONGs dentro de um polígono (por linha)
@app.route('/ongs-linha-poligono', methods=['POST'])
def ongs_linha_poligono():
    try:
        dados = request.json
        poligono = dados.get('polygon')

        # Verificar se o polígono foi fornecido
        if not poligono:
            return jsonify({"error": "Nenhum polígono foi fornecido"}), 400

        # Extrair os pontos do WKT e inverter lat/lon para lon/lat
        # Formato recebido: "POLYGON((lat1 lon1, lat2 lon2, ...))"
        try:
            pontos = poligono.replace("POLYGON((", "").replace("))", "").split(", ")
            coordenadas = []
            for ponto in pontos:
                lat, lon = map(float, ponto.split())
                coordenadas.append(f"{lon} {lat}")  # Inverta aqui

            # Fechar o polígono (opcional, mas importante para evitar erros)
            if coordenadas[0] != coordenadas[-1]:
                coordenadas.append(coordenadas[0])

            # Recriar o WKT com os valores invertidos
            wkt = f"POLYGON(({', '.join(coordenadas)}))"
        except Exception as e:
            return jsonify({"error": f"Erro ao processar as coordenadas: {str(e)}"}), 400

        # Query para buscar os dados no banco
        print("COORDENADAS",wkt)
        query = """
            SELECT id, nome, descricao, ST_AsText(localizacao) as localizacao
            FROM ongs
            WHERE ST_Intersects(localizacao, ST_GeomFromText(%s, 4326))
        """
        
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (wkt,))
        resultados = cursor.fetchall()

        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": f"Erro ao processar o polígono: {str(e)}"}), 500

# Rota Flask para buscar os locais visitados:
@app.route('/locais-visitados', methods=['GET'])
def listar_locais_visitados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT lv.nome, lv.descricao, 
           ST_X(lv.localizacao) AS longitude, 
           ST_Y(lv.localizacao) AS latitude,
           t.tipo_topografia, 
           t.altitude
    FROM locais_visitados lv
    LEFT JOIN topografia t ON lv.id = t.local_id
    """)
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

# Rota PUT para atualizar uma ONG com base na latitude e longitude
@app.route('/atualizar-local-visitado', methods=['PUT'])
def atualizar_ong():
    dados = request.json
    latitude = dados.get('latitude')
    longitude = dados.get('longitude')
    nome = dados.get('nome')
    descricao = dados.get('descricao')

    # Verificar se latitude e longitude foram fornecidas
    if not latitude or not longitude:
        return jsonify({"error": "Latitude e Longitude devem ser fornecidas"}), 400

    # Buscar o id usando a latitude e longitude
    id = buscar_id_por_localizacao(latitude, longitude)
    if not id:
        return jsonify({"message": "Nenhum ponto encontrado com essas coordenadas."}), 404

    try:
        # Conectar ao banco
        conn = conectar()
        cursor = conn.cursor()

        # Atualizar os dados com o id encontrado
        query = "UPDATE locais_visitados SET nome=%s, descricao=%s WHERE id=%s"
        cursor.execute(query, (nome, descricao, id))
        conn.commit()
        conn.close()

        return jsonify({'message': f'Local visitado com id {id} atualizado com sucesso!'}), 200

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print("DEBUG: Traceback do erro:\n", error_message)
        return jsonify({"error": str(e), "details": error_message}), 500

# Rota DELETE para deletar uma ONG com base na latitude e longitude
@app.route('/deletar-local-visitado', methods=['DELETE'])
def deletar_ong():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude or not longitude:
        return jsonify({"error": "Latitude e Longitude devem ser fornecidas"}), 400
    
    # Buscar o id usando a latitude e longitude
    id = buscar_id_por_localizacao(latitude, longitude)
    if not id:
        return jsonify({"message": "Nenhum ponto encontrado com essas coordenadas."}), 404

    try:
        # Conectar ao banco
        conn = conectar()
        cursor = conn.cursor()

        # Usar ST_Distance com uma tolerância muito pequena
        query = "DELETE FROM locais_visitados WHERE id=%s"

        # Executar a query
        cursor.execute(query, (id,))

        conn.commit()
        return jsonify({'message': f'Local visitado nas coordenadas ({latitude}, {longitude}) deletado com sucesso!'}), 200

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print("DEBUG: Traceback do erro:\n", error_message)
        return jsonify({"error": str(e), "details": error_message}), 500

    finally:
        cursor.close()
        conn.close()
        
def buscar_id_por_localizacao(latitude, longitude):
    conn = conectar()
    cursor = conn.cursor()

    # Usando ST_Distance para procurar o ponto com a localização mais próxima
    query = """
        SELECT id FROM locais_visitados
        WHERE ST_Distance(localizacao, ST_SRID(ST_GeomFromText(%s), 4326)) < 0.0001
    """
    ponto = f"POINT({latitude} {longitude})"
    cursor.execute(query, (ponto,))

    # Verificando se algum resultado foi encontrado
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return resultado[0]  # Retorna o id encontrado
    return None  # Retorna None caso não encontre nenhum ponto

# Inicializar o servidor
if __name__ == '__main__':
    app.run(debug=True)
