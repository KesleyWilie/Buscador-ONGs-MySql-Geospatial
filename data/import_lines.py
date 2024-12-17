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
def importar_linhas(arquivo_geojson):
    with open(arquivo_geojson, 'r', encoding='utf-8') as file:
        dados = geojson.load(file)
    
    for feature in dados['features']:
        # Extrair informações
        nome = feature['properties'].get('name', 'Sem nome')
        descricao = feature['properties'].get('description', 'Sem descrição')
        
        # Verificar se a geometria é um polígono
        if 'geometry' in feature and feature['geometry']['type'] == 'Polygon':
            # Extrair as coordenadas do polígono
            coordenadas = feature['geometry']['coordinates'][0]  # Pegando a coordenada do primeiro polígono
            
            # Criar a string WKT para o LINESTRING (conectar os pontos)
            linha_wkt = "LINESTRING(" + ", ".join([f"{lon} {lat}" for lon, lat in coordenadas]) + ")"
            
            # SQL para inserir no banco
            sql = """
                INSERT INTO linhas (nome, descricao, trajeto)
                VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            """
            cursor.execute(sql, (nome, descricao, linha_wkt))
    
    connection.commit()
    print("Dados de linhas importados com sucesso!")

# Caminho para o arquivo GeoJSON
arquivo_geojson = "data\ongs_brasil.geojson"

# Importar dados para a tabela linhas
importar_linhas(arquivo_geojson)

# Fechar conexão
cursor.close()
connection.close()
