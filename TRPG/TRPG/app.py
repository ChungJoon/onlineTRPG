from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
import re

app = Flask(__name__)
app.secret_key = 'ds'  # セッションの暗号化キーを設定

# データベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Zxcv0987@dbtrpg.crk2e8m6wj6j.ap-northeast-1.rds.amazonaws.com:3306/TRPG'
# 例: 'mysql+pymysql://root:password@localhost:3306/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースオブジェクトの作成
db = SQLAlchemy(app)

# コマンドのログを保存するリスト
command_logs = []
# コマンドの変数を保存するリスト
variables = {}

# ユーザーモデルの定義
class User(db.Model):
    __tablename__ = 'User'  # 既存のテーブル名に合わせて変更
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        if self.password == password:
            return True
        return False

    def __repr__(self):
        return f'<User {self.name}>'
    
class PowerDamage(db.Model):
    __tablename__ = 'PowerDamage'  # 既存のテーブル名に合わせて変更
    Power = db.Column(db.Integer, primary_key=True, nullable=False)
    col2 = db.Column(db.Integer, nullable=False)
    col3 = db.Column(db.Integer, nullable=False)
    col4 = db.Column(db.Integer, nullable=False)
    # 以下のようにカラム名をcol<数字>形式に変更
    col5 = db.Column(db.Integer, nullable=False)
    col6 = db.Column(db.Integer, nullable=False)
    col7 = db.Column(db.Integer, nullable=False)
    col8 = db.Column(db.Integer, nullable=False)
    col9 = db.Column(db.Integer, nullable=False)
    col10 = db.Column(db.Integer, nullable=False)
    col11 = db.Column(db.Integer, nullable=False)
    col12 = db.Column(db.Integer, nullable=False)

# Dice コマンドの実行関数
def dice(x,y):
    num_dice = int(x)
    num_sides = int(y)
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    sum_value = sum(rolls)
    log_message = f"{num_sides}面ダイスを{num_dice}個振った結果: {', '.join(map(str, rolls))} (合計: {sum_value})"
    return log_message, sum_value

# Power コマンドの実行関数
def power(x, y):
    power_value = int(x)
    column_number = int(y)
    
    # データベースから値を取得
    power_damage = PowerDamage.query.filter_by(Power=power_value).first()
    
    if not power_damage:
        return f"Power {power_value} のレコードが見つかりません。", None
    
    # カラム名を動的に構築
    column_name = f"col{column_number}"
    
    if not hasattr(power_damage, column_name):
        return f"カラム {column_number} が存在しません。", None
    
    column_value = getattr(power_damage, column_name)
    log_message = f"Power {power_value} のダイス {column_number} の値は {column_value} です。"
    return log_message, column_value

# Attack コマンドの実行関数
def attack(critical, powerclass,additionaldamage):
    log_message_dice, dice_value = dice(2,6)
    log_message, power_value = power(powerclass,dice_value)
    log_message_dice = log_message_dice + log_message
    sum = power_value + int(additionaldamage)
    cvalue = int(critical)

    if dice_value >= cvalue:
        x = cvalue
        while x >= cvalue:
            log_message, x = dice(2,6)
            log_message_dice = log_message_dice + log_message
            log_message, y = power(powerclass,x)
            log_message_dice = log_message_dice + log_message
            sum = sum + y

    log_message = log_message_dice + f"攻撃結果は {sum} です。"
    return log_message, sum


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        user_name = str(request.form['id'])
        password = str(request.form['pwd'])
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        
        print("POSTされたIDは？" + user_name)
        print("POSTされたPASSWORDは？" + password)
        print("クリックされたボタンのアクションは？" + action)

        if action == 'login':
            # データベースからユーザーを検索
            user = User.query.filter_by(name=user_name).first()

            if user and user.check_password(password):
                session['username'] = user.name
                return redirect(url_for('show_user_profile'))
            else:
                return render_template('form.html', message="IDまたはパスワードが正しくありません。")

    return render_template('form.html')

@app.route("/user")
def show_user_profile():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', message=f"{username}さん、ようこそ！")
    else:
        return redirect(url_for('form'))

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # セッションからユーザー名を削除
    return redirect(url_for('form'))

# 新しいルートの追加
@app.route("/command", methods=['GET', 'POST'])
def command():
    if request.method == 'POST':
        code_input = request.form.get('code_input', '').strip()  # None の場合は空文字列を使用
        if code_input:  # 空でない場合のみ処理を実行
            result = execute_code(code_input)
            command_logs.append(result)
            return render_template('command.html', command_logs=command_logs, result=result)
        else:
            return render_template('command.html', command_logs=command_logs, result='コマンドが入力されていません。')

    return render_template('command.html', command_logs=command_logs, result='')

def execute_code(code):
    results = []
    commands = code.split(';')

    for command in commands:
        command = command.strip()
        command = replace_variables(command)
        log_message, output_value = process_command(command)
        results.append(log_message)
        if output_value is not None:
            variables['last_result'] = output_value  # 変数 'last_result' に結果を保存

    return "\n".join(results)

def replace_variables(command):
    variable_pattern = r'\$(\w+)'  # $variable の形式で変数を検出
    matches = re.findall(variable_pattern, command)
    
    for match in matches:
        if match in variables:
            command = command.replace(f"${{{match}}}", str(variables[match]))
    
    return command

def process_command(command_input):
    # 変数代入とコマンドの分割処理
    assignment_pattern = r'^(\w+)\s*=\s*(.*)$'
    match = re.match(assignment_pattern, command_input)
    
    if match:
        variable_name = match.group(1)
        command = match.group(2).strip()
        log_message, output_value = execute_single_command(command)
        variables[variable_name] = output_value  # 変数に値を格納
        return f"{log_message} {variable_name} に {output_value} を代入しました。", output_value
    
    else:
        return execute_single_command(command_input)

def execute_single_command(command):
    # Power(x, y) コマンドを処理する
    power_command_pattern = r'^power\((\d+),\s*(\d+)\)$'
    # dice(x,y) コマンドを処理する
    dice_command_pattern = r'^dice\((\d+),(\d+)\)$'
    # attack(x,y,z) コマンドを処理する
    attack_command_pattern = r'^attack\((\d+),(\d+),(\d+)\)$'

    match = re.match(power_command_pattern, command)
    if match:
        return power(match.group(1), match.group(2))
    
    match = re.match(dice_command_pattern, command)
    if match:
        return dice(match.group(1),match.group(2))

    match = re.match(attack_command_pattern, command)
    if match:
        return attack(match.group(1),match.group(2),match.group(3))   
    
    else:
        log_message = "サポートされていないコマンドです。"
        return log_message, None

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0", debug=True)
