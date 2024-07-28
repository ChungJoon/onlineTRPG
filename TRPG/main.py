from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect,func
from flask_cors import CORS
from jinja2 import Template
from flask_socketio import SocketIO


db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = 'ds'  # セッションの暗号化キーを設定

# データベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Zxcv0987@dbtrpg.crk2e8m6wj6j.ap-northeast-1.rds.amazonaws.com:3306/TRPG'
# 例: 'mysql+pymysql://root:password@localhost:3306/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースオブジェクトの作成
db = SQLAlchemy(app)

socketio = SocketIO(app)

# Custom filter to use getattr in Jinja2 templates
@app.template_filter('getattr')
def getattr_filter(obj, attr):
    return getattr(obj, attr)

# Register the filter with Jinja2
app.jinja_env.filters['getattr'] = getattr_filter

# コマンドのログを保存するリスト
command_logs = []

# 武器種のリストを定義
WEAPON_CATEGORIES = [
    "ソード", "アックス", "スピア", "メイス", "クラブ",
    "スタッフ", "ガン", "フレイル", "ウォーハンマー",
    "ボウ", "クロスボウ", "スリング", "グラップラー",
]

FriendFrontUnits = ["アデル", "ヒイロ"]
FriendMidleUnits = []
FriendBackUnits = ["ルキナ", "ティー", "フラン"]
EnemyFrontUnits = []
EnemyMidleUnits = []
EnemyBackUnits = []

@app.route('/', methods=['GET', 'POST'])
def login():
    from dataclass import User,GameLog
    if request.method == 'POST':
        user_name = request.form['id']
        password = request.form['pwd']
        action = request.form.get('action')  # クリックされたボタンのvalueを取得

        if action == 'login':
            # データベースからユーザーを検索
            user = User.query.filter_by(name=user_name).first()
            if user and user.check_password(password):
                flash('ログイン成功')
                session['username'] = user.name
                # return profile(user.id)
                return redirect(url_for('profile', character_id=user.id))
            else:
                flash('ユーザーIDまたはパスワードが間違っています')
                return render_template('login.html')
        elif action == 'register':

            user = User.query.filter_by(name=user_name).first()
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('ユーザー登録が完了しました')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/login/<int:character_id>', methods=['GET', 'POST'])
def login2(character_id):
    from dataclass import User,Character
    character = Character.query.get_or_404(character_id)
    if request.method == 'POST':
        user_name = request.form['id']
        password = request.form['pwd']
        action = request.form.get('action')  # クリックされたボタンのvalueを取得

        if action == 'login':
            # データベースからユーザーを検索
            user = User.query.filter_by(name=user_name).first()

            if user and user.check_password(password):
                session['username'] = user.name
                # return profile(user.id)
                return redirect(url_for('profile', character_id=user.id))
            else:
                return render_template('login2.html')
        
        elif action == 'register':

            user = User.query.filter_by(name=user_name).first()
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

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
    from dataclass import Character
    character = Character.query.get_or_404(character_id)
    return render_template('home.html', character=character)


@app.route('/profile/<int:character_id>', methods=['GET', 'POST'])
def profile(character_id):
    from dataclass import Character,Job,MagicTable,Skill
    character = Character.query.get_or_404(character_id)
    # status = Status.query.filter_by(related_id=character.id).first()
    status = character.GetStatus()
    BattleSkills = Skill.query.filter_by(related_id=character.id,type="戦闘").all()
    OtherSkills = Skill.query.filter_by(related_id=character.id,type="汎用").all()

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

    UsableMagics = []
    for magicjob in Job.query.filter_by(related_id=character.id,type="魔法").all():
        fitmagic = MagicTable.query.filter_by(master=magicjob.name).first()
        magic = fitmagic.getUserMagic(character.id,magicjob.level)
        UsableMagics.append(magic)

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
                           skills_other=skills_other,UsableMagics=UsableMagics,
                           BattleSkills=BattleSkills,OtherSkills=OtherSkills)

def log_update(message):
    socketio.emit('log_update', {'message': message})

@app.route('/battlefield/<int:character_id>', methods=['GET', 'POST'])
def battlefield(character_id):
    from dataclass import Character,UserCommand,Unit,GameLog

    character = Character.query.get_or_404(character_id)
    user_commands=UserCommand.query.filter_by(related_id=character.id).all()
    public_commands=UserCommand.query.filter_by(related_id=0).all()
    units = Unit.query.filter_by(active=True).all()
    logitem = GameLog.query.filter_by(name="BattleLog").first()
    battle_log = logitem.log.split('\n') if logitem and logitem.log else []
    
    return render_template('battlefield.html', character=character,
                            user_commands=user_commands, public_commands=public_commands,
                            units=units, battle_log=battle_log,
                            FriendFrontUnits=FriendFrontUnits,
                            FriendMidleUnits=FriendMidleUnits,
                            FriendBackUnits=FriendBackUnits,
                            EnemyFrontUnits=EnemyFrontUnits,
                            EnemyMidleUnits=EnemyMidleUnits,
                            EnemyBackUnits=EnemyBackUnits)
    
@app.route('/unitformation', methods=['POST'])
def unitformation():
    global FriendFrontUnits, FriendMidleUnits, FriendBackUnits
    global EnemyFrontUnits, EnemyMidleUnits, EnemyBackUnits

    data = request.get_json()
    FriendFrontUnits = data.get('friendFront', [])
    FriendMidleUnits = data.get('friendMiddle', [])
    FriendBackUnits = data.get('friendBack', [])
    EnemyFrontUnits = data.get('enemyFront', [])
    EnemyMidleUnits = data.get('enemyMiddle', [])
    EnemyBackUnits = data.get('enemyBack', [])
    print(FriendFrontUnits,FriendMidleUnits)

    return jsonify({
        'friendFront': FriendFrontUnits,
        'friendMiddle': FriendMidleUnits,
        'friendBack': FriendBackUnits,
        'enemyFront': EnemyFrontUnits,
        'enemyMiddle': EnemyMidleUnits,
        'enemyBack': EnemyBackUnits
    })


@app.route('/subcharacter/<int:character_id>', methods=['GET', 'POST'])
def subcharacter(character_id):
    from dataclass import Character,SubCharacter
    character = Character.query.get_or_404(character_id)
    subcharacters=SubCharacter.query.filter_by(type="CPU").all()
    monsters=SubCharacter.query.filter_by(related_id=character_id,type="魔物").all()

    if request.method == 'POST':
        return render_template('subcharacter.html', character=character, subcharacters=subcharacters, monsters=monsters)

    return render_template('subcharacter.html', character=character, subcharacters=subcharacters, monsters=monsters)


@app.route('/create_subcharacter/<int:character_id>', methods=['GET', 'POST'])
def create_subcharacter(character_id):
    from dataclass import Character,SubCharacter,SubCharacterPart
    character = Character.query.get_or_404(character_id)

    if request.method == 'POST':
        sub_name = request.form.get('name').strip()
        subcharacter=SubCharacter.query.filter_by(name=sub_name).first()

        if sub_name and subcharacter is None and request.form.get('part_1_name'):
            items = request.form

            new_sub = SubCharacter(
                        name = sub_name,
                        related_id = character_id,
                        Level = request.form.get('Level'),
                        type = request.form.get('type'),
                        detail = request.form.get('detail')
                    )
            
            db.session.add(new_sub)
            db.session.commit()

            for key, value in items.items():
                
                if key.startswith("part_") and key.endswith("_number"):
                    value
                    partkey = f"part_{value}_"

                    if request.form.get(f'{partkey}name') != "":
                        new_subPart = SubCharacterPart(
                            name = request.form.get(f'{partkey}name'),
                            related_id = new_sub.id,
                            HP = request.form.get(f'{partkey}HP'),
                            MP = request.form.get(f'{partkey}MP'),
                            Accuracy = request.form.get(f'{partkey}Accuracy'),
                            Evasion = request.form.get(f'{partkey}Evasion'),
                            Defence = request.form.get(f'{partkey}Defence'),
                            MagicDefence = request.form.get(f'{partkey}MagicDefence'),
                            Quickness = request.form.get(f'{partkey}Require_Quickness'),
                            Knowledge = request.form.get(f'{partkey}Knowledge'),
                            Require_knowledge = request.form.get(f'{partkey}Require_knowledge'),
                            VID = request.form.get(f'{partkey}VID'),
                            MND = request.form.get(f'{partkey}MND'),
                            detail = request.form.get(f'{partkey}detail'),
                            weakpoint = request.form.get(f'{partkey}weakpoint'),
                            damage = request.form.get(f'{partkey}damage'),
                            magic_power = request.form.get(f'{partkey}magic_power'),
                            partnumber = request.form.get(f'{partkey}number')
                        )

                        new_sub.partnum = value

                        db.session.add(new_subPart)
                        db.session.add(new_sub)
                        db.session.commit()

    return render_template('create_subcharacter.html', character=character)

@app.route('/open_edit_subcharacter/<int:character_id>/<int:subcharacter_id>', methods=['GET', 'POST'])
def open_edit_subcharacter(character_id,subcharacter_id):
    from dataclass import Character,SubCharacter,SubCharacterPart
    
    subcharacter = SubCharacter.query.get_or_404(subcharacter_id)
    character = Character.query.get_or_404(character_id)
    subparts = SubCharacterPart.query.filter_by(related_id=subcharacter_id).all()

    return render_template('edit_subcharacter.html', character=character, subcharacter=subcharacter, subparts=subparts)


@app.route('/edit_subcharacter/<int:character_id>/<int:subcharacter_id>', methods=['GET', 'POST'])
def edit_subcharacter(character_id,subcharacter_id):
    from dataclass import Character,SubCharacter,SubCharacterPart

    subcharacter = SubCharacter.query.get_or_404(subcharacter_id)
    character = Character.query.get_or_404(character_id)
    
    if request.method == 'POST':
        sub_name = request.form.get('name').strip()

        if sub_name:
            items = request.form

            action = request.form.get('action')  # クリックされたボタンのvalueを取得
            
            for key, value in items.items():
  
                if key.startswith("part_") and key.endswith("_number"):
                    value
                    partkey = f"part_{value}_"
                    partname = request.form.get(f'{partkey}name') 

                    if action == 'save':

                        if partname != "" and SubCharacterPart.query.filter_by(related_id=subcharacter_id, name=partname).first() is None:      
                            
                            new_subPart = SubCharacterPart(
                                name = request.form.get(f'{partkey}name'),
                                related_id = subcharacter.id,
                                HP = request.form.get(f'{partkey}HP'),
                                MP = request.form.get(f'{partkey}MP'),
                                Accuracy = request.form.get(f'{partkey}Accuracy'),
                                Evasion = request.form.get(f'{partkey}Evasion'),
                                Defence = request.form.get(f'{partkey}Defence'),
                                MagicDefence = request.form.get(f'{partkey}MagicDefence'),
                                Quickness = request.form.get(f'{partkey}Require_Quickness'),
                                Knowledge = request.form.get(f'{partkey}Knowledge'),
                                Require_knowledge = request.form.get(f'{partkey}Require_knowledge'),
                                VID = request.form.get(f'{partkey}VID'),
                                MND = request.form.get(f'{partkey}MND'),
                                detail = request.form.get(f'{partkey}detail'),
                                weakpoint = request.form.get(f'{partkey}weakpoint'),
                                damage = request.form.get(f'{partkey}damage'),
                                magic_power = request.form.get(f'{partkey}magic_power'),
                                partnumber = request.form.get(f'{partkey}number')
                            )

                            db.session.add(new_subPart)
                            db.session.commit()

                        elif partname != "" :
                            subpart = SubCharacterPart.query.filter_by(related_id=subcharacter_id, name=partname).first() 
       
                            subpart.name = request.form.get(f'{partkey}name'),
                            subpart.related_id = subcharacter.id,
                            subpart.HP = request.form.get(f'{partkey}HP'),
                            subpart.MP = request.form.get(f'{partkey}MP'),
                            subpart.Accuracy = request.form.get(f'{partkey}Accuracy'),
                            subpart.Evasion = request.form.get(f'{partkey}Evasion'),
                            subpart.Defence = request.form.get(f'{partkey}Defence'),
                            subpart.MagicDefence = request.form.get(f'{partkey}MagicDefence'),
                            subpart.Quickness = request.form.get(f'{partkey}Require_Quickness'),
                            subpart.Knowledge = request.form.get(f'{partkey}Knowledge'),
                            subpart.Require_knowledge = request.form.get(f'{partkey}Require_knowledge'),
                            subpart.VID = request.form.get(f'{partkey}VID'),
                            subpart.MND = request.form.get(f'{partkey}MND'),
                            subpart.detail = request.form.get(f'{partkey}detail'),
                            subpart.weakpoint = request.form.get(f'{partkey}weakpoint'),
                            subpart.damage = request.form.get(f'{partkey}damage'),
                            subpart.magic_power = request.form.get(f'{partkey}magic_power'),
                            subpart.partnumber = request.form.get(f'{partkey}number')

                            db.session.add(subpart)
                            db.session.commit()

                    elif action == 'delete':
                        subpart = SubCharacterPart.query.filter_by(related_id=subcharacter_id, name=partname).first() 
                        db.session.delete(subpart)
                        db.session.commit()

            if action == 'save':
                subcharacter.name = request.form.get('name')
                subcharacter.Level = request.form.get('Level')
                subcharacter.type = request.form.get('type')
                subcharacter.detail = request.form.get('detail')

                db.session.add(subcharacter)
                db.session.commit()

            elif action == 'delete':
                db.session.delete(subcharacter)
                db.session.commit()
                return redirect(url_for('subcharacter', character_id=character.id))

    subparts = SubCharacterPart.query.filter_by(related_id=subcharacter_id).all()

    return redirect(url_for('subcharacter', character_id=character.id))

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


@app.route('/edit_job/<int:character_id>/<int:skill_id>', methods=['POST'])
def edit_job(character_id, skill_id):
    from dataclass import Character,Job

    if request.method == 'POST':
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        skill = Job.query.get(skill_id)

        if action == 'change':
             # スキルの編集ロジックをここに追加します
            inputname = skill.name
            skill.level = request.form.get(inputname)

            db.session.add(skill)
            db.session.commit()
        
        elif action == 'delete':
            db.session.delete(skill)
            db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('profile', character_id=character_id,skill_id=skill_id))


@app.route('/items/<int:character_id>', methods=['GET', 'POST'])
def items(character_id):
    from dataclass import Character,Item,Weapon,Protector,Equipment,Memo,Bullet,BulletBox
    character = Character.query.get_or_404(character_id)
    # Item情報を取得
    weapons = Weapon.query.filter_by(related_id=character.id).all()
    # Item情報を取得
    protectors = Protector.query.filter_by(related_id=character.id).all()
    # Item情報を取得
    items = Item.query.filter_by(related_id=character.id).all()
    # メモ情報を取得    
    myMemo = Memo.query.filter_by(related_id=character_id).first()
    # 弾を取得  
    mybullets = {bullet.id: bullet for bullet in Bullet.query.filter_by(related_id=character_id).all()}
    bullets = Bullet.query.filter_by(related_id=character_id).all()
    # 弾倉を取得  
    bulletboxes = []
    for weapon in weapons:
        if not weapon is None:
            bulletbox = BulletBox.query.filter_by(related_id=weapon.id).first()
            if not bulletbox is None:
                box_dict = {
                    'id': bulletbox.id,
                    'weapon_name': bulletbox.weapon_name,
                    'maxbullet': bulletbox.maxbullet,
                    'bullets': []
                }
                for i in range(1, bulletbox.maxbullet + 1):
                    col_name = f'col{i}'
                    bullet_id = getattr(bulletbox, col_name)
                    box_dict['bullets'].append(bullet_id)
                bulletboxes.append(box_dict)

    Head = Equipment.query.filter_by(related_id=character_id, type="head").first()
    Face = Equipment.query.filter_by(related_id=character_id, type="face").first()
    Ear = Equipment.query.filter_by(related_id=character_id, type="ear").first()
    Neck = Equipment.query.filter_by(related_id=character_id, type="neck").first()
    Back = Equipment.query.filter_by(related_id=character_id, type="back").first()
    RightHand = Equipment.query.filter_by(related_id=character_id, type="right_hand").first()
    LeftHand = Equipment.query.filter_by(related_id=character_id, type="left_hand").first()
    Waist = Equipment.query.filter_by(related_id=character_id, type="waist").first()
    Feet = Equipment.query.filter_by(related_id=character_id, type="feet").first()
    Other = Equipment.query.filter_by(related_id=character_id, type="other").first()

    return render_template('items.html', character=character,items=items, weapons=weapons,
                           protectors=protectors, weapon_categories=WEAPON_CATEGORIES,
                           Head=Head,Face=Face,Ear=Ear,Neck=Neck,Back=Back,RightHand=RightHand,
                           LeftHand=LeftHand,Waist=Waist,Feet=Feet,Other=Other,Memo=myMemo,
                           bullets=bullets,bulletboxes=bulletboxes,mybullets=mybullets)


@app.route('/add_item/<int:character_id>', methods=['POST'])
def add_item(character_id):
    from dataclass import Character,Item
    if request.method == 'POST':

        item_name = request.form.get('item_name-new')
        item_type = request.form.get('item_type-new')
        item_num = request.form.get('item_num-new')
        item_explain = request.form.get('item_explain-new')
        item_command = request.form.get('item_command-new')

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
    return redirect(url_for('items', character_id=character_id))

@app.route('/edit_item/<int:character_id>/<int:item_id>', methods=['POST'])
def edit_item(character_id, item_id):
    from dataclass import Character,Item

    if request.method == 'POST':
        item = Item.query.get(item_id)
        action = request.form.get('action')  # クリックされたボタンのvalueを取得

        if action == 'change':

            item.name = request.form.get(f'item_name-{item_id}')
            item.type = request.form.get(f'item_type-{item_id}')
            item.num = request.form.get(f'item_num-{item_id}')
            item.explain = request.form.get(f'item_explain-{item_id}')
            item.command = request.form.get(f'item_command-{item_id}')

            db.session.add(item)
            db.session.commit()
        
        elif action == 'delete':
            db.session.delete(item)
            db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('items', character_id=character_id,item_id=item_id))

@app.route('/delete_item/<int:character_id>/<int:item_id>', methods=['POST'])
def delete_item(character_id, item_id):
    from dataclass import Character,Item

    if request.method == 'POST':
        item = Item.query.get(item_id)
 
        db.session.delete(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('items', character_id=character_id,item_id=item_id))


@app.route('/add_weapon/<int:character_id>', methods=['POST'])
def add_weapon(character_id):
    from dataclass import Character,Weapon
    if request.method == 'POST':
        item_name = request.form.get('weapon_name-new')
        item_category = request.form.get('weapon_category-new')
        item_rank = request.form.get('weapon_rank-new')
        item_type = request.form.get('weapon_type-new')
        item_weight = request.form.get('weapon_weight-new')
        item_aim = request.form.get('weapon_aim-new')
        item_power = request.form.get('weapon_power-new')
        item_damage = request.form.get('weapon_damage-new')
        item_critical = request.form.get('weapon_critical-new')
        item_explain = request.form.get('weapon_explain-new')
        item_command = request.form.get('weapon_command-new')

        new_weapon = Weapon(
            name=item_name,
            カテゴリー=item_category,
            ランク=item_rank,
            type=item_type,
            必筋=item_weight,
            命中=item_aim,
            威力=item_power,
            追加ダメージ=item_damage,
            クリティカル=item_critical,
            explain=item_explain,
            command=item_command,
            related_id=character_id
        )
        
        db.session.add(new_weapon)
        db.session.commit()

    return redirect(url_for('items', character_id=character_id))

@app.route('/edit_weapon/<int:character_id>/<int:weapon_id>', methods=['POST'])
def edit_weapon(character_id, weapon_id):
    from dataclass import Character,Weapon

    if request.method == 'POST':
        item = Weapon.query.get(weapon_id)
        action = request.form.get('action')  # クリックされたボタンのvalueを取得

        if action == 'change':

            item.name = request.form[f'weapon_name-{weapon_id}']
            item.カテゴリー = request.form[f'weapon_category-{weapon_id}']
            item.ランク = request.form[f'weapon_rank-{weapon_id}']
            item.type = request.form[f'weapon_type-{weapon_id}']
            item.必筋 = request.form[f'weapon_weight-{weapon_id}']
            item.命中 = request.form[f'weapon_aim-{weapon_id}']
            item.威力 = request.form[f'weapon_power-{weapon_id}']
            item.クリティカル = request.form[f'weapon_critical-{weapon_id}']
            item.追加ダメージ = request.form[f'weapon_damage-{weapon_id}']
            item.command = request.form[f'weapon_command-{weapon_id}']
            item.explain = request.form[f'weapon_explain-{weapon_id}']

            db.session.add(item)
            db.session.commit()

        elif action == 'delete':
            db.session.delete(item)
            db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('items', character_id=character_id,weapon_id=weapon_id))


@app.route('/add_protector/<int:character_id>', methods=['POST'])
def add_protector(character_id):
    from dataclass import Character,Protector
    if request.method == 'POST':

        new_protector = Protector(
            name=request.form.get('protector_name-new'),
            type=request.form.get('protector_type-new'),
            ランク=request.form.get('protector_rank-new'),
            必筋=request.form.get('protector_weight-new'),
            回避=request.form.get('protector_evasion-new'),
            命中=request.form.get('protector_accuracy-new'),
            command=request.form.get('protector_command-new'),
            explain=request.form.get('protector_explain-new'),
            防護点=request.form.get('protector_defense-new'),
            related_id=character_id
        )
        
        db.session.add(new_protector)
        db.session.commit()
        

    return redirect(url_for('items', character_id=character_id))

@app.route('/edit_protector/<int:character_id>/<int:protector_id>', methods=['POST'])
def edit_protector(character_id, protector_id):
    from dataclass import Character,Protector

    if request.method == 'POST':
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        item = Protector.query.get(protector_id)

        if action == 'change':
            item.name = request.form[f'protector_name-{protector_id}']
            item.ランク = request.form[f'protector_rank-{protector_id}']
            item.type = request.form[f'protector_type-{protector_id}']
            item.必筋 = request.form[f'protector_weight-{protector_id}']
            item.防護点 = request.form[f'protector_defense-{protector_id}']
            item.回避 = request.form[f'protector_evasion-{protector_id}']
            item.命中 = request.form[f'protector_accuracy-{protector_id}']
            item.command = request.form[f'protector_command-{protector_id}']
            item.explain = request.form[f'protector_explain-{protector_id}']

            db.session.add(item)
            db.session.commit()
        
        elif action == 'delete':
            db.session.delete(item)
            db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('items', character_id=character_id,protector_id=protector_id))

@app.route('/delete_protector/<int:character_id>/<int:protector_id>', methods=['POST'])
def delete_protector(character_id, protector_id):
    from dataclass import Character,Protector

    if request.method == 'POST':
        item = Protector.query.get(protector_id)
 
        db.session.delete(item)
        db.session.commit()

    # 編集後にリダイレクトする
    return redirect(url_for('items', character_id=character_id,protector_id=protector_id))


@app.route("/settings/<int:character_id>")
def settings(character_id):
    from dataclass import Character,Status
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
@app.route("/battle_command/<int:character_id>", methods=['GET', 'POST'])
def battle_command(character_id):
    from dataclass import Character,GameLog
    character = Character.query.get_or_404(character_id)
    logitem = GameLog.query.filter_by(name="BattleLog").first()
    from commands import execute_code # commands.pyから関数をインポート
    if request.method == 'POST':
        code_input = request.form.get('command-input', '').strip()  # None の場合は空文字列を使用
        actor =  request.form['actor-selection']
        if actor == "自分":
            actor = character.label
        targets = request.form.getlist('target-selection')

        if code_input:  # 空でない場合のみ処理を実行
            result = execute_code(code_input,actor,targets)
            battle_log = logitem.log.split('\n') if logitem and logitem.log else []
            battle_log.append(result)
            log_text = '\n'.join(battle_log)
            logitem.log = log_text
            db.session.add(logitem)
            db.session.commit()
            log_update(result) 
            return jsonify({'result': [result]})

    return redirect(url_for('battlefield', character_id=character_id))


# 新しいルートの追加
@app.route("/command/<int:character_id>", methods=['GET', 'POST'])
def command(character_id):
    from dataclass import Character
    character = Character.query.get_or_404(character_id)
    from commands import execute_code # commands.pyから関数をインポート
    if request.method == 'POST':
        code_input = request.form.get('code_input', '').strip()  # None の場合は空文字列を使用
        actor =  character.label
        target = ["コマンドテスト用"]

        if code_input:  # 空でない場合のみ処理を実行
            result = execute_code(code_input,actor,target)
            command_logs.append(result)

            return render_template('command.html', command_logs=command_logs, result=result, character=character, command_input=code_input)
        else:
            return render_template('command.html', command_logs=command_logs, result='コマンドが入力されていません。', character=character)

    return render_template('command.html', command_logs=command_logs, result='', character=character)


# 保存された文字列を格納するリスト
saved_strings = []

@app.route('/save_string/<int:character_id>', methods=['POST'])
def save_string(character_id):
    from dataclass import Character,UserCommand

    character = Character.query.get_or_404(character_id)
    string_name = request.form.get('string_name')
    string_content = request.form.get('string_content')
    string_explain = request.form.get('string_explain')
    
    # 保存された文字列を追加
    saved_strings.append({'name': string_name, 'content': string_content})
    
    command = UserCommand.query.filter_by(name=string_name)

    if command != None:
        if string_name and string_content:
            new_commands = UserCommand(
                name=string_name,
                related_id=character_id,
                creator=character.label,
                command=string_content,
                explain=string_explain
            )
            db.session.add(new_commands)
            db.session.commit()
            
    # 保存された文字列を表示するページにリダイレクト
    return redirect(url_for('saved_strings_page',character_id=character_id))


@app.route('/saved_strings/<int:character_id>')
def saved_strings_page(character_id):
    from dataclass import Character
    character = Character.query.get_or_404(character_id)
    return render_template('saved_strings.html', strings=saved_strings, character=character)


@app.route('/user_command_list/<int:character_id>')
def user_command_list(character_id):
    from dataclass import Character,UserCommand
    character = Character.query.get_or_404(character_id)

    # UserCommandからrelated_idがuser_idに一致するコマンドを取得
    user_commands = UserCommand.query.filter_by(related_id=character.id).all()

    # PublicCommandからすべてのコマンドを取得
    public_commands = UserCommand.query.filter_by(related_id=0).all()

    return render_template('user_command_list.html', character=character, user_commands=user_commands, public_commands=public_commands)

@app.route('/edit_command/<int:character_id>/<int:command_id>', methods=['POST'])
def edit_command(character_id,command_id):
    from dataclass import Character,UserCommand
    character = Character.query.get_or_404(character_id)
    command = UserCommand.query.get(command_id)
    if command:
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        if action == 'save':
            command.name = request.form['name']
            command.command = request.form['command']
            command.explain = request.form['explain']
            db.session.add(command)
            db.session.commit()
        elif action == 'delete':
            db.session.delete(command)
            db.session.commit()
        elif action == 'public':
            command.related_id = 0
            db.session.add(command)
            db.session.commit()

    return redirect(url_for('user_command_list', character_id=character_id))


@app.route('/unit/<int:character_id>', methods=['GET', 'POST'])
def unit(character_id):
    from dataclass import Character, Unit, SubCharacter
    character = Character.query.get_or_404(character_id)
    palyer_units = Unit.query.filter_by(type="player").all()
    monsters = SubCharacter.query.filter_by(related_id=character_id).all()
    cpucharacters = SubCharacter.query.filter_by(type="CPU").all()

    monster_units=[]
    cpu_units=[]

    for subcharacter in monsters:    
        from dataclass import SubCharacterPart
        parts = SubCharacterPart.query.filter_by(related_id=subcharacter.id).all()

        for part in parts:
            monster_unit = Unit.query.filter_by(related_id=part.id, type="魔物").all()
            for unit in monster_unit:
                if unit.active == True:
                    monster_units.append(unit)

    for subcharacter in cpucharacters:   
        from dataclass import SubCharacterPart
        parts = SubCharacterPart.query.filter_by(related_id=subcharacter.id).all()
        for part in parts:
            cpu_unit = Unit.query.filter_by(related_id=part.id, type="CPU").all()
            for unit in cpu_unit:
                if unit.active == True:
                    cpu_units.append(unit)

    return render_template('unit.html',character=character, palyer_units=palyer_units,cpu_units=cpu_units,monster_units=monster_units)

@app.route('/creare_unit/<int:character_id>/<int:subcharacter_id>', methods=['POST'])
def creare_unit(character_id, subcharacter_id):
    
    from dataclass import Character,SubCharacter,Unit,SubCharacterPart
    character = Character.query.get_or_404(character_id)
    subcharacter = SubCharacter.query.get_or_404(subcharacter_id)
    parts = SubCharacterPart.query.filter_by(related_id=subcharacter_id).all()

    subcharacters = SubCharacter.query.filter_by(related_id=character_id, type="CPU").all()
    monsters = SubCharacter.query.filter_by(related_id=character_id, type="魔物").all()

    for part in SubCharacterPart.query.filter_by(related_id=subcharacter_id).all():
        
        new_unit = Unit(
            name=request.form.get('name').strip() + "_" + part.name,
            label=request.form.get('name').strip() + "_" + part.name,
            related_id=part.id,
            HP=part.HP,
            MP=part.MP,
            MaxHP=part.HP,
            MaxMP=part.MP,
            命中 = part.Accuracy,
            回避 = part.Evasion,
            防護点 = part.Defence,
            魔法耐性 = part.MagicDefence,
            先制力 = part.Quickness,
            魔物知識 = part.Knowledge,
            魔物知識要求値 = part.Require_knowledge,
            生命抵抗 = part.VID,
            精神抵抗 = part.MND,
            詳細 = part.detail,
            弱点 = part.weakpoint,
            基本ダメージ = part.damage,
            魔力 = part.magic_power,
            type = subcharacter.type,
            active = True
        )

        db.session.add(new_unit)
        db.session.commit()

    return render_template('subcharacter.html', character=character, subcharacters=subcharacters, monsters=monsters)

@app.route('/edit_unit/<int:character_id>/<int:unit_id>', methods=['POST'])
def edit_unit(character_id,unit_id):
    from dataclass import Character,Unit,Status,Job,Equipment
    character = Character.query.get_or_404(character_id)
    unit = Unit.query.get(unit_id)
    myStatus = Status.query.filter_by(related_id=unit.related_id).first()

    if unit:
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        if action == 'save':
            unit.name = request.form[f'name-{unit_id}']
            unit.HP = request.form[f'HP-{unit_id}']
            unit.MP = request.form[f'MP-{unit_id}']
            unit.MaxHP = request.form[f'MaxHP-{unit_id}']
            unit.MaxMP = request.form[f'MaxMP-{unit_id}']
            unit.命中 = request.form[f'accuracy-{unit_id}']
            unit.回避 = request.form[f'evasion-{unit_id}']
            unit.基本ダメージ = request.form[f'damage-{unit_id}']
            unit.防護点 = request.form[f'defence-{unit_id}']
            unit.魔力 = request.form[f'magic-{unit_id}']
            unit.生命抵抗 = request.form[f'VID-{unit_id}']
            unit.精神抵抗 = request.form[f'MND-{unit_id}']
            unit.魔物知識 = request.form[f'knowledge-{unit_id}']
            unit.先制力 = request.form[f'quickness-{unit_id}']
            unit.MP軽減 = request.form[f'mpcut-{unit_id}']
            unit.DEX = request.form[f'DEX-{unit_id}']
            unit.STR = request.form[f'STR-{unit_id}']
            unit.AGI = request.form[f'AGI-{unit_id}']
            unit.VIT = request.form[f'VIT-{unit_id}']
            unit.INT = request.form[f'INT-{unit_id}']
            unit.MND = request.form[f'MND-{unit_id}']
            unit.魔力ボーナス = request.form[f'magicbonus-{unit_id}']
            unit.クリティカルボーナス = request.form[f'criticalbonus-{unit_id}']
            unit.魔法クリティカル = request.form[f'magiccritical-{unit_id}']
            unit.先制ボーナス = request.form[f'quickbonus-{unit_id}']
            unit.知識ボーナス = request.form[f'knowbonus-{unit_id}']
            unit.回復ボーナス = request.form[f'healbonus-{unit_id}']
            unit.魔法行使判定 = request.form[f'magicchallengebonus-{unit_id}']

            unit.detail = request.form[f'detail-{unit_id}']
            db.session.add(unit)
            db.session.commit()
        elif action == 'set':
            unit.name = request.form[f'name-{unit_id}']
            unit.HP = request.form[f'HP-{unit_id}']
            unit.MP = request.form[f'MP-{unit_id}']
            unit.基本ダメージ = request.form[f'damage-{unit_id}']
            unit.魔力 = request.form[f'magic-{unit_id}']
            unit.命中 = request.form[f'accuracy-{unit_id}']
            unit.回避 = request.form[f'evasion-{unit_id}']
            unit.防護点 = request.form[f'defence-{unit_id}']
            unit.魔法耐性 = request.form[f'magicdefence-{unit_id}']
            unit.精神抵抗 = request.form[f'MND-{unit_id}']
            unit.生命抵抗 = request.form[f'VID-{unit_id}']
            unit.魔物知識 = request.form[f'knowledge-{unit_id}']
            unit.先制力 = request.form[f'quickness-{unit_id}']
            unit.魔物知識要求値 = request.form[f'Require_knowledge-{unit_id}']
            unit.弱点 = request.form[f'weakpoint-{unit_id}']
            unit.詳細 = request.form[f'detail-{unit_id}']
            db.session.add(unit)
            db.session.commit()
        elif action == 'delete':
            db.session.delete(unit)
            db.session.commit()
        elif action == 'reset':
            unitstatus = unit.GetCharacterUnit()

            db.session.add(unitstatus)
            db.session.commit()

    return redirect(url_for('unit', character_id=character_id))


@app.route('/add_equipment/<int:character_id>', methods=['POST'])
def add_equipment(character_id):
    from dataclass import Character,Equipment
    if request.method == 'POST':

        PartList = ["head","face","ear","neck","back","right_hand","left_hand","waist","feet","other"]
        
        for part in PartList:
            myEquipment = Equipment.query.filter_by(related_id=character_id, type=part).first()
            if myEquipment is None:
                new_eq = Equipment(
                related_id=character_id,
                name = request.form.get(f'{part}_name'),
                type=part,
                explain = request.form.get(f'{part}_explain'),
                )
                
                db.session.add(new_eq)
                db.session.commit()

            else:
                myEquipment.name = request.form.get(f'{part}_name')
                myEquipment.explain = request.form.get(f'{part}_explain')
                myEquipment.dex = request.form.get(f'{part}_dex')
                myEquipment.agi = request.form.get(f'{part}_agi')
                myEquipment.str = request.form.get(f'{part}_str')
                myEquipment.vit = request.form.get(f'{part}_vit')
                myEquipment.int = request.form.get(f'{part}_int')
                myEquipment.mnd = request.form.get(f'{part}_mnd')
                myEquipment.HP = request.form.get(f'{part}_HP')
                myEquipment.MP = request.form.get(f'{part}_MP')
                myEquipment.command = request.form.get(f'{part}_command')
        
                db.session.add(myEquipment)
                db.session.commit()

    return redirect(url_for('items', character_id=character_id))

@app.route('/add_memo/<int:character_id>', methods=['POST'])
def add_memo(character_id):
    from dataclass import Character,Equipment,Memo
    if request.method == 'POST':
        myMemo = Memo.query.filter_by(related_id=character_id).first()
        if myMemo is None:
            new_memo = Memo(
            related_id=character_id,
            content = request.form.get('memo_content'),
            )
            
            db.session.add(new_memo)
            db.session.commit()
        else:
            myMemo.content = request.form.get('memo_content')

            db.session.add(myMemo)
            db.session.commit()

        return redirect(url_for('items', character_id=character_id))


@app.route('/add_skill/<int:character_id>', methods=['POST'])
def add_skill(character_id):
    from dataclass import Skill
    if request.method == 'POST':

        newSkill = Skill(
            related_id = character_id,
            getlevel = request.form.get('battle_skill_level'),
            name = request.form.get('battle_skill_name'),
            getway = request.form.get('battle_skill_way'),
            explain = request.form.get('battle_skill_explain'),
            command = request.form.get('battle_skill_command'),
            type = request.form.get('battle_skill_type')
        )

        db.session.add(newSkill)
        db.session.commit()

    return redirect(url_for('profile', character_id=character_id))

@app.route('/edit_skill/<int:character_id>/<int:skill_id>', methods=['POST'])
def edit_skill(character_id,skill_id):
    from dataclass import Skill
    if request.method == 'POST':
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        mySkill = Skill.query.filter_by(id=skill_id).first()

        if action == 'change':
            mySkill.getlevel = request.form.get(f'battlelevel_{skill_id}')
            mySkill.name = request.form.get(f'{mySkill.name}')
            mySkill.getway = request.form.get(f'battleway_{skill_id}')
            mySkill.explain = request.form.get(f'battleexplain_{skill_id}')
            mySkill.command = request.form.get(f'battlecomand_{skill_id}')
            mySkill.type = request.form.get(f'battletype_{skill_id}')

            db.session.add(mySkill)
            db.session.commit()

        elif action == 'delete':
            db.session.delete(mySkill)
            db.session.commit()

    return redirect(url_for('profile', character_id=character_id))

@app.route('/add_bullet/<int:character_id>', methods=['POST'])
def add_bullet(character_id):
    from dataclass import Bullet
    if request.method == 'POST':

        newbullet = Bullet(
            related_id = character_id,
            個数 = request.form.get('個数-new'),
            name = request.form.get('bullet_name-new'),
            補正ダメージ = request.form.get('補正ダメージ-new'),
            explain = request.form.get('battle_bullet_explain'),
            command = request.form.get('battle_bullet_command'),
            補正命中 = request.form.get('補正命中-new'),
            消費MP = request.form.get('消費MP-new')
        )

        db.session.add(newbullet)
        db.session.commit()

    return redirect(url_for('items', character_id=character_id))

@app.route('/edit_bullet/<int:character_id>/<int:bullet_id>', methods=['POST'])
def edit_bullet(character_id,bullet_id):
    from dataclass import Bullet
    if request.method == 'POST':
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        mybullet = Bullet.query.filter_by(id=bullet_id).first()

        if action == 'change':
            mybullet.個数 = request.form.get(f'個数-{bullet_id}')
            mybullet.name = request.form.get(f'bullet_name-{bullet_id}')
            mybullet.補正ダメージ = request.form.get(f'補正ダメージ-{bullet_id}')
            mybullet.explain = request.form.get(f'bullet_explain-{bullet_id}')
            mybullet.command = request.form.get(f'bullet_command-{bullet_id}')
            mybullet.補正命中 = request.form.get(f'補正命中-{bullet_id}')
            mybullet.消費MP = request.form.get(f'消費MP-{bullet_id}')

            db.session.add(mybullet)
            db.session.commit()

        elif action == 'delete':
            db.session.delete(mybullet)
            db.session.commit()

    return redirect(url_for('items', character_id=character_id))

@app.route('/create_bulletbox/<int:character_id>', methods=['POST'])
def create_bulletbox(character_id):
    from dataclass import BulletBox,Weapon
    weapon_id = request.form.get('bulletbox_weapon_id')
    maxbullet = request.form.get('maxbullet')

    weapon = Weapon.query.get_or_404(weapon_id)

    new_bulletbox = BulletBox(
        weapon_name=weapon.name,
        related_id=weapon_id,
        maxbullet=maxbullet
    )

    db.session.add(new_bulletbox)
    db.session.commit()
    return redirect(url_for('items', character_id=character_id))

@app.route('/edit_bulletbox/<int:character_id>/<int:bulletbox_id>', methods=['POST'])
def edit_bulletbox(character_id,bulletbox_id):
    from dataclass import BulletBox
    if request.method == 'POST':
        action = request.form.get('action')  # クリックされたボタンのvalueを取得
        mybullet = BulletBox.query.filter_by(id=bulletbox_id).first()

        if action == 'change':
            for i in range(1, mybullet.maxbullet + 1):
                col_name = f'col{i}'
                bullet_id = request.form.get(f'bullet_box-{mybullet.id}-{i}')
                setattr(mybullet, col_name, bullet_id)

            db.session.commit()

        elif action == 'delete':
            db.session.delete(mybullet)
            db.session.commit()

    return redirect(url_for('items', character_id=character_id))


@app.route('/commandlist/<int:character_id>')
def commandlist(character_id):
    from dataclass import Character
    character = Character.query.get_or_404(character_id)
    commands = [
        {
            'name': 'dice(x,y)',
            'description': 'x:ダイスの数,y:面の数',
            'return': '合計値',
            'details': '任意の数・面のダイスを振り合計値を取得する。'
        },
        {
            'name': 'getstatus(unit_name,status_name)',
            'description': 'unit_name:ユニットの名前, status_name:ステータスの名前',
            'return': 'ステータス値',
            'details': '指定されたユニットの特定のステータスを取得する。'
        },
        {
            'name': 'setstatus(unit_name,status_name,status_value)',
            'description': 'unit_name:ユニットの名前, status_name:ステータスの名前, status_value:ステータスの変化量',
            'return': 'ステータス値',
            'details': '指定されたユニットの特定のステータスを変更する。'
        },
        {
            'name': 'getweapon(weapon_id,status_name)',
            'description': 'weapon_id:武器のid, status_name:ステータスの名前',
            'return': 'ステータス値',
            'details': '指定されたユニットの特定のステータスを取得する。'
        },
        {
            'name': 'getprotector(protector_id,status_name)',
            'description': 'protector_id:防具の名id, status_name:ステータスの名前',
            'return': 'ステータス値',
            'details': '指定されたユニットの特定のステータスを取得する。'
        },
        {
            'name': 'power(power,dice)',
            'description': 'power:威力, dice:ダイス値',
            'return': 'ステータス値',
            'details': '威力表の該当する値を取得する。'
        },
        {
            'name': 'physical_attack(weapon_id)',
            'description': 'weapon_id:使用する武器のID',
            'return': 'ダメージ値',
            'details': 'ターゲットに対する物理攻撃を行い、ダメージ値を取得する。'
        },
        {
            'name': 'magical_attack(power,mp,magictype)',
            'description': 'power:魔法の威力, mp:消費MP, magictype:魔法の分類(真語魔法、操霊魔法など)',
            'return': 'ダメージ値',
            'details': 'ターゲットに対する魔法攻撃を行い、ダメージ値を取得する。'
        },
        {
            'name': 'shoot_attack(power,weapon_id)',
            'description': 'power:武器の威力, weapon_id:使用する武器のID',
            'return': 'ダメージ値',
            'details': 'ターゲットに対する射撃攻撃を行い、ダメージ値を取得する。'
        },
        {
            'name': 'magishoot_attack(power,mp,weapon_id)',
            'description': 'power:武器の威力, mp:消費MP, weapon_id:使用する武器のID',
            'return': 'ダメージ値',
            'details': 'ターゲットに対して魔法を乗せた射撃攻撃を行い、ダメージ値を取得する。'
        },
        {
            'name': 'attack(critical,damage)',
            'description': 'critical:クリティカル値, damage:打撃点',
            'return': 'ダメージ値',
            'details': 'モンスター用。ターゲットに対してダイス+打撃点の攻撃を行い、ダメージ値を取得する。'
        },
        {
            'name': 'fixattack(type,value)',
            'description': 'type:攻撃タイプ（魔法か物理）,value:固定ダメージ値',
            'return': 'ダメージ値',
            'details': '魔法か物理の固定ダメージを与える。ダメージ値は基本ダメージの値'
        },
        {
            'name': 'useitem(item_id,num)',
            'description': 'useitem:アイテムID,num:使用する個数',
            'return': 'コマンドのreturn値',
            'details': 'アイテムを使用する。このときアイテムのコマンドが実行される。使用したアイテムが消耗品の場合その個数分消費する。'
        },
        {
            'name': 'heal(unit_name,value)',
            'description': 'unit_name:ユニットの名前,value:回復量',
            'return': '回復後のHP',
            'details': '特定のユニットに対して回復を行う。'
        },
        {
            'name': 'challenge(bonus,targetstatus)',
            'description': 'bonus:判定ボーナス値, targetstatus:ステータス名',
            'return': 'True/False',
            'details': '自分のダイス＋ボーナス値と相手のダイス＋ステータス値で達成値比較'
        },
        {
            'name': 'challenge_status(mystatus,targetstatus)',
            'description': 'mystatus:ステータス名, targetstatus:ステータス名',
            'return': 'True/False',
            'details': '自分と相手のステータス補正込みで達成値比較'
        },
        {
            'name': 'getsum(a,b,c...)',
            'description': '任意の数字の列',
            'return': '合計値',
            'details': '合計値を取得する。'
        },
        {
            'name': 'getmax(a,b,c...)',
            'description': '任意の数字の列',
            'return': '最大値',
            'details': '最大値を取得する。'
        },
        {
            'name': 'getmin(a,b,c...)',
            'description': '任意の数字の列',
            'return': '最小値',
            'details': '最小値を取得する。'
        },
        {
            'name': 'plus(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': '数字の和',
            'details': 'x+yをする。'
        },
        {
            'name': 'minus(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': '数字の差',
            'details': 'x-yをする。'
        },
        {
            'name': 'multiply(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': '数字の積',
            'details': 'x*yをする。'
        },
        {
            'name': 'divide(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': '数字の商',
            'details': 'x/yをする。余りは切り捨て。'
        },
        {
            'name': 'ifmore(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': 'True/False',
            'details': 'x>yを判定する。'
        },
        {
            'name': 'ifless(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': 'True/False',
            'details': 'x<yを判定する。'
        },
        {
            'name': 'ifequal(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': 'True/False',
            'details': 'x=yを判定する。'
        },
        {
            'name': 'ifeqmore(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': 'True/False',
            'details': 'x>=yを判定する。'
        },
        {
            'name': 'ifeqless(x,y)',
            'description': 'x:任意の数,y:任意の数',
            'return': 'True/False',
            'details': 'x<=yを判定する。'
        },
        {
            'name': 'actionif(bool,action)',
            'description': 'bool:TrueまたはFalseまたはreturnがTrue/Falseのコマンド,action:任意のコマンド',
            'return': 'コマンドのreturn値',
            'details': '判定がTureの時のみ実行する。'
        },
        {
            'name': 'loop(trigger,action,bool)',
            'description': 'trigger:ループに突入するか判断するreturnがTrue/Falseのコマンド,action:任意のコマンド,bool:ループ継続するか判断するreturnがTrue/Falseのコマンド',
            'return': 'コマンドのreturn値',
            'details': '判定がTureの限り繰り返し実行する。無限ループ防止のため上下２０回'
        },
        {
            'name': 'challenge(bonus,targetstatus)',
            'description': 'bonus:自分側の補正値,targetstatus:相手が参照するステータス',
            'return': 'True/False',
            'details': '相手への挑戦（命中や魔法など）'
        },
        {
            'name': 'challenge_status(mystatus,targetstatus)',
            'description': 'mystatus:自分が参照するステータス値,targetstatus:相手が参照するステータス',
            'return': 'True/False',
            'details': 'お互いのステータスを参照して挑戦（命中や魔法など）'
        },
        {
            'name': 'getjoblevel(unit_name,jobname)',
            'description': 'unit_name:ユニット名,jobname:技能名',
            'return': '技能レベル',
            'details': '技能レベルを取得する'
        },
        
        # 他のコマンドを追加
    ]
    return render_template('commandlist.html', commands=commands, character=character)

# SocketIOイベントのハンドラを追加
@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == "__main__":
    socketio.run(port=8000, host="0.0.0.0", debug=True)
