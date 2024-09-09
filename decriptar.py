import os
import json
from cryptography.fernet import Fernet

def decrypt_file(file_name, key):
    # Converte a chave de string para bytes
    f = Fernet(key.encode())
    # Lê os dados criptografados do arquivo
    with open(file_name, "rb") as file:
        encrypted_data = file.read()
    # Decripta os dados
    decrypted_data = f.decrypt(encrypted_data)
    # Sobrescreve o arquivo com os dados decriptografados
    with open(file_name, "wb") as file:
        file.write(decrypted_data)

def load_original_names(directory_path):
    json_file = os.path.join(directory_path, "file_names.json")
    if not os.path.exists(json_file):
        print("Arquivo JSON com os nomes originais não encontrado.")
        return None
    with open(json_file, "r") as file:
        return json.load(file)

def decrypt_directory(directory_path, key):
    original_names = load_original_names(directory_path)
    if original_names is None:
        return
    
    
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                # Decriptografa o arquivo
                decrypt_file(file_path, key)
                print(f"{file_path} foi decriptado com sucesso.")

                # Renomeia o arquivo de volta ao nome original
                if file_name in original_names:
                    original_name = original_names[file_name]
                    original_file_path = os.path.join(root, original_name)
                    os.rename(file_path, original_file_path)
                    print(f"{file_name} foi renomeado para {original_name}")
            except Exception as e:
                print(f"Erro ao decriptar o arquivo {file_path}: {e}")

def main():
    # Solicita o diretório e a chave de criptografia ao usuário
    directory_path = input("Digite o caminho do diretório a ser decriptografado: ")
    key = input("Digite a chave de criptografia (base64): ")

    # Decripta todos os arquivos no diretório especificado
    decrypt_directory(directory_path, key)

if __name__ == "__main__":
    main()
