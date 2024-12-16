import requests

BASE_URL = "http://localhost:5000"

def buscar_raio():
    lat = float(input("Latitude: "))
    lon = float(input("Longitude: "))
    raio = float(input("Raio em metros: "))
    response = requests.get(f"{BASE_URL}/ongs-raio", params={"latitude": lat, "longitude": lon, "raio": raio})
    print(response.json())

def buscar_poligono():
    print("Digite as coordenadas do polígono (ex: lat1 lon1, lat2 lon2, ...):")
    coords = input("Coordenadas: ").split(",")
    wkt = f"POLYGON(({', '.join(coords)}))"
    response = requests.post(f"{BASE_URL}/ongs-poligono", json={"polygon": wkt})
    print(response.json())

def buscar_raio_linha():
    lat = float(input("Latitude: "))
    lon = float(input("Longitude: "))
    raio = float(input("Raio em metros: "))
    response = requests.get(f"{BASE_URL}/ongs-raio", params={"latitude": lat, "longitude": lon, "raio": raio})
    print(response.json())

def buscar_poligono_linha():
    print("Digite as coordenadas do polígono (ex: lat1 lon1, lat2 lon2, ...):")
    coords = input("Coordenadas: ").split(",")
    wkt = f"POLYGON(({', '.join(coords)}))"
    response = requests.post(f"{BASE_URL}/ongs-poligono", json={"polygon": wkt})
    print(response.json())

def atualizar_ponto():
    lat = float(input("Latitude do ponto a atualizar: "))
    lon = float(input("Longitude do ponto a atualizar: "))
    nome = input("Novo nome: ")
    descricao = input("Nova descrição: ")
    response = requests.put(f"{BASE_URL}/atualizar-ong", json={
        "latitude": lat,
        "longitude": lon,
        "nome": nome,
        "descricao": descricao
    })
    print(response.json())

def deletar_ponto():
    lat = float(input("Latitude do ponto a deletar: "))
    lon = float(input("Longitude do ponto a deletar: "))
    response = requests.delete(f"{BASE_URL}/deletar-ong", params={
        "latitude": lat,
        "longitude": lon
    })
    print(response.json())

def main():
    while True:
        print("\n1. Buscar ONGs por Raio")
        print("2. Buscar ONGs por Polígono")
        print("3. Buscar ONGs por Raio (linha)")
        print("4. Buscar ONGs por Polígono (linha)")
        print("5. Atualizar Ponto")
        print("6. Deletar Ponto")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            buscar_raio()
        elif opcao == "2":
            buscar_poligono()
        elif opcao == "3":
            buscar_raio_linha()
        elif opcao == "4":
            buscar_poligono_linha()
        elif opcao == "5":
            atualizar_ponto()
        elif opcao == "6":
            deletar_ponto()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
