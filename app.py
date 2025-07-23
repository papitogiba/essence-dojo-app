from flask import Flask, render_template, request, redirect, url_for
import csv
import os
import tempfile
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime  # ¡Esto también es necesario!

app = Flask(__name__)  # 💥 Esto faltaba

# Caminhos dos arquivos locais (ainda usados no painel admin)
ALUNOS_FILE = 'alunos.csv'
INSCRICOES_FILE = 'inscricoes.csv'

# Conexão com Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".json") as tmp:
    tmp.write(os.environ['GOOGLE_CREDENTIALS_JSON'])
    tmp_path = tmp.name

creds = ServiceAccountCredentials.from_json_keyfile_name(tmp_path, scope)
client = gspread.authorize(creds)

# Abre a planilha e as abas (usa exatamente os nomes no Google Sheets)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1utcHu8XSYnCuAJcBJnwY9OqjRAdGPI5GHIEKPmSP4E0/edit")
sheet_inscricoes = spreadsheet.worksheet("Inscricoes")
sheet_alunos = spreadsheet.worksheet("Alunos")

# Certifique-se que os arquivos locais ainda existam
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
        sheet_alunos.append_row([nome, email, faixa])
        return redirect(url_for('home'))
    return render_template('registo.html')

@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        horario = request.form['horario']

        # Bloquear domingos
        data_obj = datetime.strptime(data, "%Y-%m-%d")
        dia_semana = data_obj.weekday()  # 0=lunes, 6=domingo
        if dia_semana == 6:
            return "Não há treinos aos domingos. Por favor, escolha outro dia."

        # Validar horários disponíveis por dia
        horarios_validos = []
        if dia_semana in range(0, 5):  # Segunda a Sexta
            horarios_validos = [
                "09:00 - 10:30 - Todos os níveis",
                "18:00 - 19:00 - Fundamentos",
                "19:00 - 20:30 - Avançados"
            ]
        elif dia_semana == 5:  # Sábado
            horarios_validos = [
                "09:00 - 10:30 - Todos os níveis"
            ]

        horario_str = f"{horario}"
        if horario_str not in horarios_validos:
            return "Este horário não está disponível para o dia escolhido. Por favor, selecione um horário válido."

        sheet_inscricoes.append_row([nome, data, horario])
        return render_template('confirmacao.html', nome=nome, data=data, horario=horario)

    nomes = [row[0] for row in sheet_alunos.get_all_values()[1:]]  # ignora cabeçalho
    return render_template('inscricao.html', horarios=HORARIOS, nomes=nomes)

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
    # Atualiza lista de alunos local
    with open(ALUNOS_FILE, encoding='utf-8') as f:
        alunos = list(csv.reader(f))
    with open(ALUNOS_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for linha in alunos:
            if linha and linha[1] != email:
                writer.writerow(linha)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

