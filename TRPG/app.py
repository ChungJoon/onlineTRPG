from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'ds'  # セッションの暗号化キーを設定

# コマンドのログを保存するリスト
command_logs = []

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        user_id = str(request.form['id'])
        password = str(request.form['pwd'])
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        
        print("POSTされたIDは？" + user_id)
        print("POSTされたPASSWORDは？" + password)
        print("クリックされたボタンのアクションは？" + action)

        if action == 'login':
            if user_id == "021512" and password == "password":  # パスワードチェックを追加
                session['username'] = "鄭"
                return redirect(url_for('show_user_profile'))
            elif user_id == "021513" and password == "password":
                session['username'] = "不明"
                return redirect(url_for('show_user_profile'))
            else:
                return render_template('form.html', message="IDまたはパスワードが正しくありません。")

        elif action == 'register':
            return render_template('index.html', message="登録ページにリダイレクトされました")

        elif action == 'forgot_password':
            return render_template('index.html', message="パスワードリセットページにリダイレクトされました")

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
@app.route("/command", methods=['POST'])
def command():
    command_input = request.form.get('command_input')
    # コマンドの実行
    result = f"入力されたコマンド: {command_input}"
    print(result)
    # ログに追加
    command_logs.append(result)
    # ログを返す
    return result

@app.route("/command", methods=['GET'])
def show_command_page():
    return render_template('command.html', command_logs=command_logs)

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0", debug=True)
