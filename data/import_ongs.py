import pymysql
import geojson
import os

# Configurações do banco de dados MySQL
db_config = {
    "host": "localhost",
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "database": os.getenv("database")
}

# Conexão com o banco de dados
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# Função para processar e inserir dados no banco
def importar_ongs(arquivo_geojson):
    with open(arquivo_geojson, 'r', encoding='utf-8') as file:
        dados = geojson.load(file)
    
    for feature in dados['features']:
        # Extrair informações
        nome = feature['properties'].get('name', 'Sem nome')
        descricao = feature['properties'].get('description', 'Sem descrição')
        
        # Coordenadas (POINT)
        if 'geometry' in feature and feature['geometry']['type'] == 'Point':
            coordenadas = feature['geometry']['coordinates']
            latitude, longitude = coordenadas[1], coordenadas[0]  # GeoJSON usa [lon, lat]
            
            # SQL para inserir no banco
            sql = """
                INSERT INTO ongs (nome, descricao, localizacao)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            """
            ponto = f"POINT({longitude} {latitude})"
            cursor.execute(sql, (nome, descricao, ponto))
    
    connection.commit()
    print("Dados importados com sucesso!")

# Caminho para o arquivo GeoJSON
arquivo_geojson = "ongs_brasil.geojson"

# Importar dados
importar_ongs(arquivo_geojson)

# Fechar conexão
cursor.close()
connection.close()
