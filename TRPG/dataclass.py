from main import db,app
from sqlalchemy import inspect,Integer
from sqlalchemy.orm import class_mapper

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
    
# Characterモデルの定義
class Character(db.Model):
    __tablename__ = 'Character'  # テーブル名を指定

    # カラムの定義
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(45), unique=True, nullable=False)
    type = db.Column(db.String(45), nullable=False)
    age = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    lavel = db.Column(db.String(45))
    backborn = db.Column(db.String(45))
    Technique = db.Column(db.Integer, nullable=False, default=0)
    Body = db.Column(db.Integer, nullable=False, default=0)
    Heart = db.Column(db.Integer, nullable=False, default=0)
    A = db.Column(db.Integer, nullable=False, default=0)
    B = db.Column(db.Integer, nullable=False, default=0)
    C = db.Column(db.Integer, nullable=False, default=0)
    D = db.Column(db.Integer, nullable=False, default=0)
    E = db.Column(db.Integer, nullable=False, default=0)
    F = db.Column(db.Integer, nullable=False, default=0)
    d1 = db.Column(db.Integer)
    d2 = db.Column(db.Integer)
    d3 = db.Column(db.Integer)
    d4 = db.Column(db.Integer)
    d5 = db.Column(db.Integer)
    d6 = db.Column(db.Integer)
    e1 = db.Column(db.Integer)
    e2 = db.Column(db.Integer)
    e3 = db.Column(db.Integer)
    e4 = db.Column(db.Integer)
    e5 = db.Column(db.Integer)
    e6 = db.Column(db.Integer)
    experience = db.Column(db.Integer)
    money = db.Column(db.Integer)
    debt = db.Column(db.Integer)
    honor = db.Column(db.Integer)


    def __repr__(self):
        return f'<Character {self.name}>'
    
    def GetStatus(self):

        # Statusの名前
        status_name = self.name + '_Status'
        # 同名のStatusが存在するかをチェック
        mystatus = Status.query.filter_by(related_id=self.id).first()
        myskills = Skills.query.filter_by(related_id=self.id).first()


        # ステータスを変数として取得
        DEX= self.Technique + self.A + self.d1 + self.e1
        AGI= self.Technique + self.B + self.d2 + self.e2
        STR= self.Body + self.C + self.d3 + self.e3
        VIT= self.Body + self.D + self.d4 + self.e4
        INT= self.Heart + self.E + self.d5 + self.e5
        MND= self.Heart + self.F + self.d6 + self.e6
        LEVEL= myskills.get_max_skill_value('All')[1]
        MP= myskills.get_total_magic_value() * 3 + MND + 1
        MAG= myskills.get_max_skill_value('Magics')[1] + INT//6

        # アプリケーションコンテキストを使用する
        # with app.app_context():  
        # with db.session.begin():
        if mystatus:
            mystatus.DEX= DEX,
            mystatus.AGI= AGI,
            mystatus.STR= STR,
            mystatus.VIT= VIT,
            mystatus.INT= INT,
            mystatus.MND= MND,
            mystatus.HP= LEVEL * 3 + VIT ,
            mystatus.MP= MP,
            mystatus.LEVEL=LEVEL,
            mystatus.VITREG= LEVEL + VIT//6,
            mystatus.MNDREG= LEVEL + MND//6,
            mystatus.MAG= MAG,
            mystatus.魔物知識= INT//6,
            mystatus.先制力= AGI//6,
            mystatus.移動力= AGI,
            mystatus.全力移動= AGI * 3,
            mystatus.器用度ボーナス= DEX//6,
            mystatus.筋力ボーナス= STR//6,
            mystatus.敏捷度ボーナス= AGI//6

            # セッションに追加して保存
            db.session.add(mystatus)
            db.session.commit()
            return mystatus
        else:
            # 新しいステータスの作成
            my_status = Status(
                id=self.id,  # CharacterのIDを参照
                related_id= self.id,
                name= self.name+'_Status',
                DEX= DEX,
                AGI= AGI,
                STR= STR,
                VIT= VIT,
                INT= INT,
                MND= MND,
                HP= VIT * 3 + LEVEL,
                MP= MP,
                LEVEL=LEVEL,
                VITREG= LEVEL + VIT//6,
                MNDREG= LEVEL + MND//6,
                MAG=MAG,
                魔物知識= INT//6,
                先制力= AGI//6,
                移動力= AGI,
                全力移動= AGI * 3,
                器用度ボーナス= DEX//6,
                筋力ボーナス= STR//6,
                敏捷度ボーナス= AGI//6
                )

            # セッションに追加して保存
            db.session.add(my_status)
            db.session.commit()

            return my_status
            
    def GetSkills(self):
        # 同名のStatusが存在するかをチェック
        myskill = Status.query.filter_by(related_id=self.id).first()
        myskill.深智魔法 = min(myskill.ソーサラー魔法,myskill.コンジュラー魔法)

        return myskill
    
# Statusモデルの定義
class Status(db.Model):
    __tablename__ = 'Status'  # テーブル名を指定

    # カラムの定義
    id = db.Column(db.Integer, primary_key=True)
    related_id = db.Column(db.Integer, db.ForeignKey('Character.id'))
    name = db.Column(db.String(45), unique=True, nullable=False)
    DEX = db.Column(db.Integer, nullable=False, default=0)
    AGI = db.Column(db.Integer, nullable=False, default=0)
    STR = db.Column(db.Integer, nullable=False, default=0)
    VIT = db.Column(db.Integer, nullable=False, default=0)
    INT = db.Column(db.Integer, nullable=False, default=0)
    MND = db.Column(db.Integer, nullable=False, default=0)
    HP = db.Column(db.Integer, nullable=False, default=0)
    MP = db.Column(db.Integer, nullable=False, default=0)
    LEVEL = db.Column(db.Integer, nullable=False, default=0)
    VITREG = db.Column(db.Integer, nullable=False, default=0)
    MNDREG = db.Column(db.Integer, nullable=False, default=0)
    MAG = db.Column(db.Integer, nullable=False, default=0)
    魔物知識 = db.Column(db.Integer)
    先制力 = db.Column(db.Integer)
    移動力 = db.Column(db.Integer)
    全力移動 = db.Column(db.Integer)
    器用度ボーナス = db.Column(db.Integer)
    筋力ボーナス = db.Column(db.Integer)
    敏捷度ボーナス = db.Column(db.Integer)

    def __repr__(self):
        return f'<Status {self.name}>'

class Skills(db.Model):
    __tablename__ = 'Skills'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, db.ForeignKey('Character.id'), nullable=True)  # 外部キー
    name = db.Column(db.String(45), unique=True, nullable=False)
    ソーサラー魔法 = db.Column(db.Integer, default=0, nullable=False)
    コンジュラー魔法 = db.Column(db.Integer, default=0, nullable=False)
    フェアリーテイマー魔法 = db.Column(db.Integer, default=0, nullable=False)
    プリースト魔法 = db.Column(db.Integer, default=0, nullable=False)
    マギテック魔法 = db.Column(db.Integer, default=0, nullable=False)
    深智魔法 = db.Column(db.Integer, default=0, nullable=False)
    ファイター物理 = db.Column(db.Integer, default=0, nullable=False)
    グラップラー物理 = db.Column(db.Integer, default=0, nullable=False)
    フェンサー物理 = db.Column(db.Integer, default=0, nullable=False)
    シューター物理 = db.Column(db.Integer, default=0, nullable=False)
    スカウト = db.Column(db.Integer, default=0, nullable=False)
    レンジャー = db.Column(db.Integer, default=0, nullable=False)
    セージ = db.Column(db.Integer, default=0, nullable=False)
    ウォーリーダー = db.Column(db.Integer, default=0, nullable=False)
    ミスティック = db.Column(db.Integer, default=0, nullable=False)
    ライダー = db.Column(db.Integer, default=0, nullable=False)
    アルケミスト = db.Column(db.Integer, default=0, nullable=False)
    バード = db.Column(db.Integer, default=0, nullable=False)
    エンハンサー = db.Column(db.Integer, default=0, nullable=False)
    ウィザード = db.Column(db.Integer, default=0, nullable=False)

    def get_max_skill_value(self,keyword):
        # 自身の属性を取得
        attributes = inspect(self.__class__).columns

        if keyword == "All":
            # name, id, related_id 以外で、Integer型のカラムのみをフィルタリング
            skill_values = {
                attr_name: getattr(self, attr_name) 
                for attr_name, column in attributes.items()
                if column.type.__class__ == Integer and attr_name not in ['id', 'related_id', 'name']
            }

        elif keyword == "Physics":
            # '物理' が名前に含まれ、Integer型のカラムのみをフィルタリング
            skill_values = {
                attr_name: getattr(self, attr_name) 
                for attr_name, column in attributes.items()
                if column.type.__class__ == Integer 
                    and '物理' in attr_name
            }

        elif keyword == "Magics":
            # '魔法' が名前に含まれ、Integer型のカラムのみをフィルタリング
            skill_values = {
                attr_name: getattr(self, attr_name) 
                for attr_name, column in attributes.items()
                if column.type.__class__ == Integer 
                    and '魔法' in attr_name and attr_name not in ['深智魔法', 'related_id', 'id']
            }

        if not skill_values:
            return None, 0
        
        # 最大値を取得
        max_skill_name, max_skill_value = max(skill_values.items(), key=lambda item: item[1])
        return max_skill_name, max_skill_value
    
    def get_total_magic_value(self):
        # 自身の属性を取得
        attributes = inspect(self.__class__).columns
        # '魔法' が名前に含まれ、Integer型のカラムのみをフィルタリング
        skill_values = {
        attr_name: getattr(self, attr_name) 
        for attr_name, column in attributes.items()
        if isinstance(column.type, Integer) 
        and '魔法' in attr_name 
        and attr_name not in ['深智魔法', 'related_id', 'id']
    }
        
        # 合計を取得
        sum_skill_value = sum(skill_values.values())
        return sum_skill_value
    
    def __repr__(self):
        return f'<Skills {self.name}>'
    
    
class PowerDamage(db.Model):
    __tablename__ = 'PowerDamage'  # 既存のテーブル名に合わせて変更
    Power = db.Column(db.Integer, primary_key=True, nullable=False)
    col2 = db.Column(db.Integer, nullable=False)
    col3 = db.Column(db.Integer, nullable=False)
    col4 = db.Column(db.Integer, nullable=False)
    col5 = db.Column(db.Integer, nullable=False)
    col6 = db.Column(db.Integer, nullable=False)
    col7 = db.Column(db.Integer, nullable=False)
    col8 = db.Column(db.Integer, nullable=False)
    col9 = db.Column(db.Integer, nullable=False)
    col10 = db.Column(db.Integer, nullable=False)
    col11 = db.Column(db.Integer, nullable=False)
    col12 = db.Column(db.Integer, nullable=False)

class Job(db.Model):
    __tablename__ = 'Job'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=False)
    related_id = db.Column(db.Integer, db.ForeignKey('Character.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    type = db.Column(db.String(45), nullable=True)
    exptype = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f"<Job(name={self.name}, level={self.level}, type={self.type}, related_id={self.related_id})>"

class Item(db.Model):
    __tablename__ = 'Item'  # 既存のテーブル名に合わせて変更
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, nullable=True)  # 外部キー
    name = db.Column(db.String(45), nullable=False)
    num = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(45), nullable=True)
    explain = db.Column(db.String(45), nullable=True)
    command = db.Column(db.String(45), nullable=True)

class Weapon(db.Model):
    __tablename__ = 'Weapon'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, db.ForeignKey('Character.id'), nullable=True)
    name = db.Column(db.String(45), nullable=False)
    type = db.Column(db.String(45), nullable=True)
    category = db.Column(db.String(45), nullable=True)
    actual = db.Column(db.String(10), nullable=True)
    rank = db.Column(db.String(5), nullable=True)
    using = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.Integer, default=0)
    aim = db.Column(db.Integer, default=0)
    power = db.Column(db.Integer, default=0)
    critical = db.Column(db.Integer, default=10)
    damage = db.Column(db.Integer, default=0)
    explain = db.Column(db.String(950), nullable=True)
    command = db.Column(db.String(45), nullable=True)
    effect = db.Column(db.String(90), nullable=True)

    def __repr__(self):
        return f'<Weapon {self.name}>'
    
class Protector(db.Model):
    __tablename__ = 'Protector'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, db.ForeignKey('Character.id'), nullable=True)
    name = db.Column(db.String(45), nullable=False)
    defense = db.Column(db.Integer, default=0)
    weight = db.Column(db.Integer, nullable=True)
    evasion = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Integer, default=0)
    type = db.Column(db.String(45), nullable=True)
    explain = db.Column(db.String(90), nullable=True)
    command = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f'<Protector {self.name}>'
