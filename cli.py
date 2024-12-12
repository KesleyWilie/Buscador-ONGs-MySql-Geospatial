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

def main():
    while True:
        print("\n1. Buscar ONGs por Raio")
        print("2. Buscar ONGs por Polígono")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            buscar_raio()
        elif opcao == "2":
            buscar_poligono()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
