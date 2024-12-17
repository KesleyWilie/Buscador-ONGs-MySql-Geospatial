
# Mapa Interativo de ONGs e Locais Visitados

Este projeto consiste em uma aplicação web que exibe ONGs e locais visitados em um mapa interativo, permitindo ao usuário adicionar novos locais e buscar ONGs por proximidade.

## Funcionalidades

* **Visualização de ONGs no mapa:**  Exibe as ONGs cadastradas no banco de dados como marcadores no mapa.
* **Cadastro de locais visitados:** Permite ao usuário adicionar novos locais visitados clicando no mapa e fornecendo nome e descrição.
* **Busca de ONGs por raio:**  (Implementado no backend, disponível via CLI) Permite buscar ONGs dentro de um raio específico de um ponto.
* **Busca de ONGs por polígono:** (Implementado no backend, disponível via CLI) Permite buscar ONGs dentro de um polígono desenhado no mapa (as coordenadas do polígono devem ser copiadas e usadas na CLI).
* **Persistência de dados:** Os locais visitados são salvos em um banco de dados MySQL e carregados no mapa quando a página é aberta.
* **Topografia das ONGs:** Cada ONG pode ter informações sobre o tipo de topografia (por exemplo, plano, montanhoso) e a altitude, que são exibidas no mapa quando o usuário clica em um marcador.

## Tecnologias Utilizadas

* **Front-end:** HTML, JavaScript, Leaflet, Leaflet.draw
* **Back-end:** Python, Flask, Flask-CORS
* **Banco de dados:** MySQL com extensões geoespaciais

## Instalação

1. **Clone o repositório:**

   ```bash
   git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/KesleyWilie/Buscador-ONGs-MySql-Geospatial.git) 
   cd seu-repositorio
   ```

2. **Instale as dependências:**

   ```bash
   pip install flask flask-cors mysql-connector-python requests shapely
   ```

3. **Configure o banco de dados MySQL:**

   * Certifique-se de ter o MySQL instalado e em execução.
   * Crie o banco de dados e as tabelas:

   ```sql
   CREATE DATABASE ongs_db;

   USE ongs_db;

   CREATE TABLE locais_visitados (
       id INT AUTO_INCREMENT PRIMARY KEY,
       nome VARCHAR(100) NOT NULL,
       descricao TEXT,
       localizacao POINT NOT NULL SRID 4326,
       SPATIAL INDEX (localizacao)
   );

   CREATE TABLE ongs (
       id INT AUTO_INCREMENT PRIMARY KEY,
       nome VARCHAR(100) NOT NULL,
       descricao TEXT,
       localizacao POINT NOT NULL SRID 4326,
       SPATIAL INDEX (localizacao)
   );
   
   CREATE TABLE topografia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    local_id INT,
    tipo_topografia VARCHAR(255),
    altitude DECIMAL(10, 2),
    forma_geometrica GEOMETRY,
    CONSTRAINT fk_local
        FOREIGN KEY (local_id) REFERENCES locais_visitados(id)
   );

   CREATE TABLE linhas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    trajeto LINESTRING NOT NULL SRID 4326,
    SPATIAL INDEX (trajeto)
   );

   ```
   * Para alimentar as tabelas de ongs e de linhas basta executar os arquivos impor_ongs.py e import_lines.py localizados na pasta data.

4. **Execute o servidor Flask:**

   ```bash
   python backend.py
   ```

5. **Abra o arquivo `index.html` no seu navegador.**

## Uso da Interface de Linha de Comando (CLI)

1. **Certifique-se de que o servidor Flask esteja em execução.**
2. **Execute o script `cli.py`:**

   ```bash
   python cli.py
   ```

3. **Siga as instruções no menu para buscar ONGs por raio ou polígono.**  Para a busca por polígono, desenhe o polígono no mapa na interface web, copie as coordenadas exibidas e cole-as na CLI.



## Observações

* O projeto utiliza dados geoespaciais para permitir a busca de ONGs por proximidade, dentro de um raio ou polígono.
* As operações geoespaciais são realizadas pelo MySQL, utilizando funções como `ST_Distance_Sphere` e `ST_Within`.
* Este projeto é um exemplo de aplicação que demonstra o uso de dados geoespaciais para resolver um problema prático.


