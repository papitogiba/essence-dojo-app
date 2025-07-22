from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Caminho do arquivo CSV
ALUNOS_FILE = 'alunos.csv'
INSCRICOES_FILE = 'inscricoes.csv'

# Certifique-se que os arquivos existem
if not os.path.exists(ALUNOS_FILE):
    with open(ALUNOS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nome', 'Email', 'Faixa'])

if not os.path.exists(INSCRICOES_FILE):
    with open(INSCRICOES_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nome', 'Data', 'Horário'])

HORARIOS = [
    ("09:00 - 10:30", "Todos os níveis"),
    ("18:00 - 19:00", "Fundamentos"),
    ("19:00 - 20:30", "Avançados")
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/registo', methods=['GET', 'POST'])
def registo():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        faixa = request.form['faixa']
        with open(ALUNOS_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([nome, email, faixa])
        return redirect(url_for('home'))
    return render_template('registo.html')

@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        horario = request.form['horario']
        with open(INSCRICOES_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([nome, data, horario])
        return render_template('confirmacao.html', nome=nome, data=data, horario=horario)
    return render_template('inscricao.html', horarios=HORARIOS)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        senha = request.form['senha']
        if senha == 'admin2025':
            with open(ALUNOS_FILE, encoding='utf-8') as f:
                alunos = list(csv.reader(f))[1:]
            with open(INSCRICOES_FILE, encoding='utf-8') as f:
                inscricoes = list(csv.reader(f))[1:]
            return render_template('painel.html', alunos=alunos, inscricoes=inscricoes)
    return render_template('admin.html')

@app.route('/excluir', methods=['POST'])
def excluir():
    email = request.form['email']
    # Atualiza lista de alunos
    with open(ALUNOS_FILE, encoding='utf-8') as f:
        alunos = list(csv.reader(f))
    with open(ALUNOS_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for linha in alunos:
            if linha and linha[1] != email:
                writer.writerow(linha)
    return redirect(url_for('admin'))

# Teste de integridade de inscrições – 2ª prova

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
