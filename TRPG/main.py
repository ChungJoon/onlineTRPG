from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

db = SQLAlchemy()

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


@app.route('/', methods=['GET', 'POST'])
def login():
    from dataclass import User
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
                # return profile(user.id)
                return redirect(url_for('profile', character_id=user.id))
            else:
                return render_template('login.html', message="IDまたはパスワードが正しくありません。")

    return render_template('login.html')

@app.route('/login/<int:character_id>', methods=['GET', 'POST'])
def login2(character_id):
    from dataclass import User,Character
    character = Character.query.get_or_404(character_id)
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
                # return profile(user.id)
                return redirect(url_for('profile', character_id=user.id))
            else:
                return render_template('login2.html', message="IDまたはパスワードが正しくありません。")

    return render_template('login2.html',character=character)

@app.route("/user")
def show_user_profile():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', message=f"{username}さん、ようこそ！")
    else:
        return redirect(url_for('form'))

@app.route("/home/<int:character_id>")
def home(character_id):
    from dataclass import Character,Status,Skills
    character = Character.query.get_or_404(character_id)
    return render_template('home.html', character=character)


@app.route('/profile/<int:character_id>', methods=['GET', 'POST'])
def profile(character_id):
    from dataclass import Character,Status,Skills,Item,Job
    character = Character.query.get_or_404(character_id)
    # status = Status.query.filter_by(related_id=character.id).first()
    status = character.GetStatus()
    skills = Skills.query.filter_by(related_id=character.id).first()
    jobs = Job.query.filter_by(related_id=character.id).first()

    # Skill情報の分類
    skills_physical = []
    skills_magic = []
    skills_other = []

    for skill in Job.query.filter_by(related_id=character.id).all():
        if '物理' in skill.type:
            skills_physical.append(skill)
        elif '魔法' in skill.type:
            skills_magic.append(skill)
        else:
            skills_other.append(skill)

    # Item情報を取得
    items = Item.query.filter_by(related_id=character.id).all()
    
    if request.method == 'POST':
        # POSTリクエスト処理、フォームのデータを取得し、必要な操作を実行する
        character.sex = str(request.form['sex'])
        character.type = str(request.form['type'])
        character.age = str(request.form['age'])
        character.backborn = str(request.form['backborn'])
        character.Technique = str(request.form['Technique'])
        character.Body = str(request.form['Body'])
        character.Heart = str(request.form['Heart'])
        character.A = str(request.form['A'])
        character.B = str(request.form['B'])
        character.C = str(request.form['C'])
        character.D = str(request.form['D'])
        character.E = str(request.form['E'])
        character.F = str(request.form['F'])
        character.d1 = str(request.form['d1'])
        character.d2 = str(request.form['d2'])
        character.d3 = str(request.form['d3'])
        character.d4 = str(request.form['d4'])
        character.d5 = str(request.form['d5'])
        character.d6 = str(request.form['d6'])
        character.e1 = str(request.form['e1'])
        character.e2 = str(request.form['e2'])
        character.e3 = str(request.form['e3'])
        character.e4 = str(request.form['e4'])
        character.e5 = str(request.form['e5'])
        character.e6 = str(request.form['e6'])
        character.experience = str(request.form['experience'])
        character.money = str(request.form['money'])
        character.debt = str(request.form['debt'])
        character.honor = str(request.form['honor'])

        db.session.add(character)
        db.session.commit()

    return render_template('profile.html', character=character, status=status,
                           skills_physical=skills_physical, skills_magic=skills_magic,
                           skills_other=skills_other, items=items)


@app.route('/add_job/<int:character_id>', methods=['POST'])
def add_job(character_id):
    
    from dataclass import Character,Job
    character = Character.query.get_or_404(character_id)

    skill_name = request.form.get('skill_name').strip()
    skill_level = int(request.form.get('skill_level'))
    skill_type = request.form.get('skill_type')

    if skill_name and skill_type:
        new_skill = Job(
            name=skill_name,
            related_id=character_id,
            level=skill_level,
            type=skill_type
        )
        db.session.add(new_skill)
        db.session.commit()

    return redirect(url_for('profile', character_id=character_id))

@app.route('/edit_skill/<int:character_id>/<int:skill_id>', methods=['POST'])
def edit_skill(character_id, skill_id):
    from dataclass import Character,Job
    # スキルの削除ロジックをここに追加します
    skill = Job.query.get(skill_id)
    inputname = skill.name
    skill.level = request.form.get(inputname)

    if skill:
        db.session.add(skill)
        db.session.commit()
        flash(f"スキル {skill.name} を変更しました", "success")
    else:
        flash("スキルが見つかりません", "error")
    
    # 削除後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,skill_id=skill_id))

@app.route('/delete_skill/<int:character_id>/<int:skill_id>', methods=['POST'])
def delete_skill(character_id, skill_id):
    from dataclass import Character,Job
    # スキルの削除ロジックをここに追加します
    skill = Job.query.get(skill_id)
    if skill:
        db.session.delete(skill)
        db.session.commit()
        flash(f"スキル {skill.name} が削除されました", "success")
    else:
        flash("スキルが見つかりません", "error")
    
    # 削除後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,skill_id=skill_id))

@app.route("/settings/<int:character_id>")
def settings(character_id):
    from dataclass import Character,Status,Skills
    character = Character.query.get_or_404(character_id)
    return render_template('settings.html', character=character)

@app.route('/logout')
def logout():
    session.pop('username', None)  # セッションからユーザー名を削除
    return redirect(url_for('form'))

@app.route('/apply')
def apply(character_id):
    db.session.commit()             # データベース更新
    return redirect(url_for('profile', character_id=character_id))

# 新しいルートの追加
@app.route("/command/<int:character_id>", methods=['GET', 'POST'])
def command(character_id):
    from dataclass import Character,Status,Skills
    character = Character.query.get_or_404(character_id)
    from commands import execute_code # commands.pyから関数をインポート
    if request.method == 'POST':
        code_input = request.form.get('code_input', '').strip()  # None の場合は空文字列を使用
        if code_input:  # 空でない場合のみ処理を実行
            result = execute_code(code_input)
            command_logs.append(result)
            return render_template('command.html', command_logs=command_logs, result=result, character=character)
        else:
            return render_template('command.html', command_logs=command_logs, result='コマンドが入力されていません。', character=character)

    return render_template('command.html', command_logs=command_logs, result='', character=character)

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0", debug=True)
