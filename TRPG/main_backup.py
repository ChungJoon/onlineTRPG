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

# 武器種のリストを定義
WEAPON_CATEGORIES = [
    "ソード", "アックス", "スピア", "メイス", "クラブ",
    "スタッフ", "ガン", "フレイル", "ウォーハンマー",
    "ボウ", "クロスボウ", "スリング"
]


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
    from dataclass import Character,Status,Skills,Item,Job,Weapon,Protector
    character = Character.query.get_or_404(character_id)
    # status = Status.query.filter_by(related_id=character.id).first()
    status = character.GetStatus()

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
    weapons = Weapon.query.filter_by(related_id=character.id).all()
    # Item情報を取得
    protectors = Protector.query.filter_by(related_id=character.id).all()
    # Item情報を取得
    items = Item.query.filter_by(related_id=character.id).all()
    
    if request.method == 'POST':
        # POSTリクエスト処理、フォームのデータを取得し、必要な操作を実行する
        character.sex = request.form['sex']
        character.type = request.form['type']
        character.age = request.form['age']
        character.backborn = request.form['backborn']
        character.Technique = request.form['Technique']
        character.Body = request.form['Body']
        character.Heart = request.form['Heart']
        character.A = request.form['A']
        character.B = request.form['B']
        character.C = request.form['C']
        character.D = request.form['D']
        character.E = request.form['E']
        character.F = request.form['F']
        character.d1 = request.form['d1']
        character.d2 = request.form['d2']
        character.d3 = request.form['d3']
        character.d4 = request.form['d4']
        character.d5 = request.form['d5']
        character.d6 = request.form['d6']
        character.e1 = request.form['e1']
        character.e2 = request.form['e2']
        character.e3 = request.form['e3']
        character.e4 = request.form['e4']
        character.e5 = request.form['e5']
        character.e6 = request.form['e6']
        character.experience = request.form['experience']
        character.money = request.form['money']
        character.debt = request.form['debt']
        character.honor = request.form['honor']

        db.session.add(character)
        db.session.commit()

    return render_template('profile.html', character=character, status=status,
                           skills_physical=skills_physical, skills_magic=skills_magic,
                           skills_other=skills_other, items=items, weapons=weapons,
                           protectors=protectors, weapon_categories=WEAPON_CATEGORIES)


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

@app.route('/add_item/<int:character_id>', methods=['POST'])
def add_item(character_id):
    from dataclass import Character,Item
    if request.method == 'POST':
        print('add')
        item_name = request.form.get('new_item_name[]')
        item_type = request.form.get('new_item_type[]')
        item_num = request.form.get('new_item_num[]')
        item_explain = request.form.get('new_item_explain[]')
        item_command = request.form.get('new_item_command[]')
        print(item_name)
        new_item = Item(
            related_id=character_id,
            name=item_name,
            type=item_type,
            num=item_num,
            explain=item_explain,
            command=item_command
        )
        
        db.session.add(new_item)
        db.session.commit()

    # 追加後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id))

@app.route('/edit_item/<int:character_id>/<int:item_id>', methods=['POST'])
def edit_item(character_id, item_id):
    from dataclass import Character,Item

    if request.method == 'POST':
        item = Item.query.get(item_id)
        print('item_id:'+str(item_id))

        items = request.form
        for key, value in items.items():
            if key.startswith("item_") and key.endswith("_name"):
                select_item_id = int(key.split("_")[1])
                item_name = str(value)
            elif key.startswith("item_") and key.endswith("_type"):
                item_type = str(value)
            elif key.startswith("item_") and key.endswith("_num"):
                item_num = int(value)
            elif key.startswith("item_") and key.endswith("_explain"):
                item_explain = str(value)
            elif key.startswith("item_") and key.endswith("_command"):
                item_command = str(value)

        item.name = item_name
        item.type=item_type,
        item.num=item_num,
        item.explain=item_explain,
        item.command=item_command

        db.session.add(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,item_id=item_id))

@app.route('/delete_item/<int:character_id>/<int:item_id>', methods=['POST'])
def delete_item(character_id, item_id):
    from dataclass import Character,Item

    if request.method == 'POST':
        item = Item.query.get(item_id)
 
        db.session.delete(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,item_id=item_id))


@app.route('/add_weapon/<int:character_id>', methods=['POST'])
def add_weapon(character_id):
    from dataclass import Character,Weapon
    if request.method == 'POST':
        item_name = request.form.get('new_weapon_name[]')
        item_type = request.form.get('new_weapon_category[]')
        item_type = request.form.get('new_weapon_type[]')
        item_weight = request.form.get('new_weapon_weight[]')
        item_aim = request.form.get('new_weapon_aim[]')
        item_power = request.form.get('new_weapon_power[]')
        item_explain = request.form.get('new_weapon_explain[]')
        item_command = request.form.get('new_weapon_command[]')

        new_weapon = Weapon(
            name=item_name,
            type=item_type,
            weight=item_weight,
            aim=item_aim,
            power=item_power,
            explain=item_explain,
            command=item_command,
            related_id=character_id
        )
        
        db.session.add(new_weapon)
        db.session.commit()

    return redirect(url_for('profile', character_id=character_id))

@app.route('/edit_weapon/<int:character_id>/<int:weapon_id>', methods=['POST'])
def edit_weapon(character_id, weapon_id):
    from dataclass import Character,Weapon

    if request.method == 'POST':
        item = Weapon.query.get(weapon_id)

        items = request.form
        for key, value in items.items():
            if key.startswith("weapon_") and key.endswith("_name"):
                select_item_id = int(key.split("_")[1])
                item_name = str(value)
            elif key.startswith("weapon_") and key.endswith("_category"):
                item_category = str(value)
            elif key.startswith("weapon_") and key.endswith("_type"):
                item_type = str(value)
            elif key.startswith("weapon_") and key.endswith("_rank"):
                item_rank = str(value)
            elif key.startswith("weapon_") and key.endswith("_weight"):
                item_weight = int(value)
            elif key.startswith("weapon_") and key.endswith("_power"):
                item_power = int(value)
            elif key.startswith("weapon_") and key.endswith("_aim"):
                item_aim = int(value)
            elif key.startswith("weapon_") and key.endswith("_damage"):
                item_damage = int(value)
            elif key.startswith("weapon_") and key.endswith("_explain"):
                item_explain = str(value)

        item.name = item_name
        item.category=item_category
        item.type=item_type
        item.rank=item_rank
        item.weight=item_weight
        item.power=item_power
        item.aim=item_aim
        item.damage=item_damage
        item.explain=item_explain

        db.session.add(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,weapon_id=weapon_id))

@app.route('/delete_weapon/<int:character_id>/<int:weapon_id>', methods=['POST'])
def delete_weapon(character_id, weapon_id):
    from dataclass import Character,Weapon

    if request.method == 'POST':
        item = Weapon.query.get(weapon_id)
 
        db.session.delete(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,weapon_id=weapon_id))

@app.route('/add_protector/<int:character_id>', methods=['POST'])
def add_protector(character_id):
    from dataclass import Character,Protector
    if request.method == 'POST':
        item_name = request.form.get('new_protector_name[]')
        item_defense = request.form.get('new_protector_defense[]')
        item_weight = request.form.get('new_protector_weight[]')
        item_evasion = request.form.get('new_protector_evasion[]')
        item_accuracy = request.form.get('new_protector_accuracy[]')
        item_explain = request.form.get('new_protector_explain[]')
        item_command = request.form.get('new_protector_command[]')

        new_protector = Protector(
            name=item_name,
            defense=item_defense,
            weight=item_weight,
            evasion=item_evasion,
            accuracy=item_accuracy,
            explain=item_explain,
            command=item_command,
            related_id=character_id
        )
        
        db.session.add(new_protector)
        db.session.commit()

    return redirect(url_for('profile', character_id=character_id))

@app.route('/edit_protector/<int:character_id>/<int:protector_id>', methods=['POST'])
def edit_protector(character_id, protector_id):
    from dataclass import Character,Protector

    if request.method == 'POST':
        item = Protector.query.get(protector_id)

        items = request.form
        for key, value in items.items():
            if key.startswith("protector_") and key.endswith("_name"):
                select_item_id = int(key.split("_")[1])
                item_name = str(value)
            elif key.startswith("protector_") and key.endswith("_type"):
                item_type = str(value)
            elif key.startswith("protector_") and key.endswith("_weight"):
                item_weight = int(value)
            elif key.startswith("protector_") and key.endswith("_defense"):
                item_defense = int(value)
            elif key.startswith("protector_") and key.endswith("_evasion"):
                item_evasion = int(value)
            elif key.startswith("protector_") and key.endswith("_accuracy"):
                item_accuracy = int(value)
            elif key.startswith("protector_") and key.endswith("_explain"):
                item_explain = str(value)
            elif key.startswith("protector_") and key.endswith("_command"):
                item_command = str(value)

        item.name = item_name
        item.type=item_type
        item.defense=item_defense
        item.weight=item_weight
        item.evasion=item_evasion
        item.accuracy=item_accuracy
        item.explain=item_explain
        item.command=item_command

        db.session.add(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,protector_id=protector_id))

@app.route('/delete_protector/<int:character_id>/<int:protector_id>', methods=['POST'])
def delete_protector(character_id, protector_id):
    from dataclass import Character,Protector

    if request.method == 'POST':
        item = Protector.query.get(protector_id)
 
        db.session.delete(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,protector_id=protector_id))


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
