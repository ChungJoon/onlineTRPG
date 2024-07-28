from main import db,app
from sqlalchemy import inspect,Integer,func
from sqlalchemy.orm import class_mapper

def coalesce(value):
    return value if value is not None else 0

# ユーザーモデルの定義
class User(db.Model):
    __tablename__ = 'User'  # 既存のテーブル名に合わせて変更
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

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
    label = db.Column(db.String(45))
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

        mystatus = Status.query.filter_by(related_id=self.id).first()

        # 装備による補正
        EquipmentDEX = db.session.query(func.sum(Equipment.dex)).filter_by(related_id=self.id).scalar()
        EquipmentAGI = db.session.query(func.sum(Equipment.agi)).filter_by(related_id=self.id).scalar()
        EquipmentSTR = db.session.query(func.sum(Equipment.str)).filter_by(related_id=self.id).scalar()
        EquipmentVIT = db.session.query(func.sum(Equipment.vit)).filter_by(related_id=self.id).scalar()
        EquipmentINT = db.session.query(func.sum(Equipment.int)).filter_by(related_id=self.id).scalar()
        EquipmentMND = db.session.query(func.sum(Equipment.mnd)).filter_by(related_id=self.id).scalar()
        EquipmentHP = db.session.query(func.sum(Equipment.HP)).filter_by(related_id=self.id).scalar()
        EquipmentMP = db.session.query(func.sum(Equipment.MP)).filter_by(related_id=self.id).scalar()

        # ステータスを変数として取得
        DEX= self.Technique + self.A + self.d1 + self.e1 + coalesce(EquipmentDEX)
        AGI= self.Technique + self.B + self.d2 + self.e2 + coalesce(EquipmentAGI)
        STR= self.Body + self.C + self.d3 + self.e3 + coalesce(EquipmentSTR)
        VIT= self.Body + self.D + self.d4 + self.e4 + coalesce(EquipmentVIT)
        INT= self.Heart + self.E + self.d5 + self.e5 + coalesce(EquipmentINT)
        MND= self.Heart + self.F + self.d6 + self.e6 + coalesce(EquipmentMND)

        LEVEL = db.session.query(func.max(Job.level)).filter_by(related_id=self.id).scalar()
        if LEVEL is None:
            LEVEL = 0

        MP = db.session.query(func.sum(Job.level)).filter_by(related_id=self.id,type="魔法").scalar() 
        if MP is None:
            MP = 0
        MP = MP * 3 + MND +1
        WizardMP = db.session.query(func.sum(Job.level)).filter_by(related_id=self.id,name="ウィザード").scalar() 
        WizardMP = coalesce(WizardMP)
        MP -= WizardMP * 3
        
        MAG = db.session.query(func.max(Job.level)).filter_by(related_id=self.id,type="魔法").scalar()
        if MAG is None:
            MAG = 0
        else:
            MAG = MAG + INT//6

        sage = Job.query.filter_by(related_id=self.id, name="セージ").first()
        if sage is None:
            Knowledge = 0
        else:
            Knowledge = sage.level + INT//6

        skaut = Job.query.filter_by(related_id=self.id, name="スカウト").first()
        if skaut is None:
            Quickness = 0
        else:
            Quickness = skaut.level + AGI//6

        physical_level = db.session.query(func.max(Job.level)).filter_by(related_id=self.id, type = "物理").scalar()

        if physical_level is None:
            physical_level = 0
        # アプリケーションコンテキストを使用する
        # with app.app_context():  
        # with db.session.begin():
        if mystatus:
            mystatus.DEX= DEX
            mystatus.AGI= AGI
            mystatus.STR= STR
            mystatus.VIT= VIT
            mystatus.INT= INT
            mystatus.MND= MND
            mystatus.HP= LEVEL * 3 + VIT + EquipmentHP
            mystatus.MP= MP + EquipmentMP
            mystatus.LEVEL=LEVEL
            mystatus.VITREG= LEVEL + VIT//6
            mystatus.MNDREG= LEVEL + MND//6
            mystatus.MAG= MAG
            mystatus.魔物知識= Knowledge
            mystatus.先制力= Quickness
            mystatus.移動力= AGI
            mystatus.全力移動= AGI * 3
            mystatus.命中力= physical_level + DEX//6
            mystatus.回避力= physical_level + AGI//6
            mystatus.基本ダメージ= physical_level + STR//6
            mystatus.器用度ボーナス = DEX//6
            mystatus.筋力ボーナス = STR//6
            mystatus.敏捷度ボーナス = AGI//6
            mystatus.知力ボーナス = INT//6
            mystatus.生命力ボーナス = VIT//6
            mystatus.精神力ボーナス = MND//6

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
                )

            # セッションに追加して保存
            db.session.add(my_status)
            db.session.commit()

            return my_status
    
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
    命中力 = db.Column(db.Integer)
    回避力 = db.Column(db.Integer)
    基本ダメージ = db.Column(db.Integer)
    器用度ボーナス = db.Column(db.Integer)
    筋力ボーナス = db.Column(db.Integer)
    敏捷度ボーナス = db.Column(db.Integer)
    知力ボーナス = db.Column(db.Integer)
    生命力ボーナス = db.Column(db.Integer)
    精神力ボーナス = db.Column(db.Integer)

    def __repr__(self):
        return f'<Status {self.name}>'

    
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
    カテゴリー = db.Column(db.String(45), nullable=True)
    actual = db.Column(db.String(10), nullable=True)
    ランク = db.Column(db.String(5), nullable=True)
    用法 = db.Column(db.String(10), nullable=True)
    必筋 = db.Column(db.Integer, default=0)
    命中 = db.Column(db.Integer, default=0)
    威力 = db.Column(db.Integer, default=0)
    クリティカル = db.Column(db.Integer, default=10)
    追加ダメージ = db.Column(db.Integer, default=0)
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
    防護点 = db.Column(db.Integer, default=0, nullable=True)
    必筋 = db.Column(db.Integer, nullable=True)
    回避 = db.Column(db.Integer, default=0, nullable=True)
    命中 = db.Column(db.Integer, default=0, nullable=True)
    type = db.Column(db.String(45), nullable=True)
    ランク = db.Column(db.String(45), nullable=True)
    explain = db.Column(db.String(90), nullable=True)
    command = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f'<Protector {self.name}>'
    
class UserCommand(db.Model):
    __tablename__ = 'UserCommand'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(Integer, nullable=True)
    creator = db.Column(db.String(45), nullable=True)
    name = db.Column(db.String(45), unique=True, nullable=False)
    command = db.Column(db.String(9945), nullable=True)
    explain = db.Column(db.String(245), nullable=True)


    def __repr__(self):
        return f"UserCommand(id={self.id}, related_id={self.related_id}, creator='{self.creator}', name='{self.name}', command='{self.command}', explain='{self.explain}')"


class Unit(db.Model):
    __tablename__ = 'Unit'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, default=None)
    name = db.Column(db.String(45), nullable=True)
    label = db.Column(db.String(45), nullable=True)
    HP = db.Column(db.Integer, default=0)
    MP = db.Column(db.Integer, default=0)
    命中= db.Column(db.Integer, default=0)
    回避 = db.Column(db.Integer, default=0)
    防護点 = db.Column(db.Integer, default=0)
    先制力 = db.Column(db.Integer, default=0)
    魔物知識 = db.Column(db.Integer, default=0)
    魔物知識要求値 = db.Column(db.Integer, default=0)
    生命抵抗 = db.Column(db.Integer, default=0)
    精神抵抗 = db.Column(db.Integer, default=0)
    詳細 = db.Column(db.String(455), nullable=True)
    弱点 = db.Column(db.String(45), nullable=True)
    基本ダメージ = db.Column(db.Integer, default=0)
    MP軽減 = db.Column(db.Integer, default=0)
    MP消費カット = db.Column(db.Integer, default=0)
    魔力 = db.Column(db.Integer, default=0)
    type = db.Column(db.String(45), nullable=True)
    active = db.Column(db.Boolean, nullable=True)
    MaxHP = db.Column(db.Integer, default=0)
    MaxMP = db.Column(db.Integer, default=0)
    DEX = db.Column(db.Integer, default=0, nullable=True)
    STR = db.Column(db.Integer, default=0, nullable=True)
    AGI = db.Column(db.Integer, default=0, nullable=True)
    VIT = db.Column(db.Integer, default=0, nullable=True)
    INT = db.Column(db.Integer, default=0, nullable=True)
    MND = db.Column(db.Integer, default=0, nullable=True)
    魔力ボーナス = db.Column(db.Integer, default=0, nullable=True)
    クリティカルボーナス = db.Column(db.Integer, default=0, nullable=True)
    魔法クリティカル = db.Column(db.Integer, default=0, nullable=True)
    先制ボーナス = db.Column(db.Integer, default=0, nullable=True)
    知識ボーナス = db.Column(db.Integer, default=0, nullable=True)
    回復ボーナス = db.Column(db.Integer, default=0, nullable=True)
    魔法行使判定 = db.Column(db.Integer, default=0, nullable=True)
    魔法耐性 = db.Column(db.Integer, default=0, nullable=True)
    カウンター = db.Column(db.Integer, default=0, nullable=True)

    def __repr__(self):
        return f"Unit(id={self.id}, name='{self.name}')"
    
    def GetCharacterUnit(self):
        myStatus = Status.query.filter_by(related_id=self.related_id).first()
        physiclevel = db.session.query(func.max(Job.level)).filter_by(related_id=self.related_id, type = "物理").scalar()
        magiclevel = db.session.query(func.max(Job.level)).filter_by(related_id=self.related_id, type = "魔法").scalar()
        
        # ボーナス補正
        self.DEX = myStatus.器用度ボーナス
        self.AGI = myStatus.敏捷度ボーナス 
        self.STR = myStatus.筋力ボーナス 
        self.VIT = myStatus.生命力ボーナス 
        self.INT = myStatus.知力ボーナス 
        self.MND = myStatus.精神力ボーナス 

        if physiclevel is None:
            self.命中 = 0
            self.回避 = 0
            self.基本ダメージ = 0
        else:
            # 命中力補正
            ProtectorAccuracy = db.session.query(func.sum(Protector.命中)).filter_by(related_id=self.related_id).scalar()
            ProtectorAccuracy = coalesce(ProtectorAccuracy)
            self.命中 = physiclevel + self.DEX + ProtectorAccuracy
        
            # 回避力補正
            ProtectorEvasion = db.session.query(func.sum(Protector.回避)).filter_by(related_id=self.related_id).scalar()
            ProtectorEvasion = coalesce(ProtectorEvasion)
            self.回避 = physiclevel + self.AGI + ProtectorEvasion

             # ダメージ補正
            self.基本ダメージ = physiclevel + self.STR
        

        # 防護点補正
        ProtectorDefense = db.session.query(func.sum(Protector.防護点)).filter_by(related_id=self.related_id).scalar()
        ProtectorDefense = coalesce(ProtectorDefense)
        self.防護点 = ProtectorDefense

        # 魔力補正
        if magiclevel is None:
            self.魔力 =0
        else:
            self.魔力ボーナス = self.INT
            self.魔力 = self.魔力ボーナス + int(magiclevel)
        

         # 先制力補正
        self.先制力 = myStatus.先制力 

         # 魔物知識補正
        self.魔物知識 = myStatus.魔物知識 
         # 精神抵抗補正
        self.精神抵抗 = myStatus.MNDREG

         # 生命抵抗補正
        self.生命抵抗 = myStatus.VITREG

        self.MaxHP = myStatus.HP
        self.MaxMP = myStatus.MP

        # その他ステータス初期化
        self.クリティカルボーナス = 0
        self.魔法クリティカル = 0
        self.MP軽減 = 0
        self.先制ボーナス = 0
        self.知識ボーナス = 0
        self.回復ボーナス = 0
        self.魔法行使判定 = 0
        self.MP消費カット = 0
        self.魔法耐性 = 0

        db.session.add(self)
        db.session.commit()

        # 武器、防具、特技によるコマンド実行
        from commands import execute_code
        myweapons = Weapon.query.filter_by(related_id=self.related_id).all()
        for weapon in myweapons:
            if not weapon.command is None:
                result = execute_code(weapon.command,self.name,[])
        myprotectors = Protector.query.filter_by(related_id=self.related_id).all()
        for protector in myprotectors:
            if not protector.command is None:
                result = execute_code(protector.command,self.name,[])
        myskills = Skill.query.filter_by(related_id=self.related_id).all()
        for skill in myskills:
            if not skill.command is None:
                result = execute_code(skill.command,self.name,[])
        myequipments = Equipment.query.filter_by(related_id=self.related_id).all()
        for equipment in myequipments:
            if not equipment.command is None:
                result = execute_code(equipment.command,self.name,[])

        self.MP消費カット = self.MP軽減
        db.session.add(self)
        db.session.commit()

        return self

    
class SubCharacter(db.Model):
    __tablename__ = 'SubCharacter'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, default=None)
    name = db.Column(db.String(45), default=None)
    Level = db.Column(db.Integer, default=0)
    HP = db.Column(db.Integer, default=0)
    MP = db.Column(db.Integer, default=0)
    Accuracy = db.Column(db.Integer, default=0)
    Evasion = db.Column(db.Integer, default=0)
    Defence = db.Column(db.Integer, default=0)
    Quickness = db.Column(db.Integer, default=0)
    Knowledge = db.Column(db.Integer, default=0)
    Require_knowledge = db.Column(db.Integer, default=0)
    VID = db.Column(db.Integer, default=0)
    MND = db.Column(db.Integer, default=0)
    detail = db.Column(db.String(455), default=None)
    weakpoint = db.Column(db.String(45), default=None)
    damage = db.Column(db.Integer, default=0)
    magic_power = db.Column(db.Integer, default=0)
    type = db.Column(db.String(45), default=None)
    partnum = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"SubCharacter(id={self.id}, name='{self.name}')"

class SubCharacterPart(db.Model):
    __tablename__ = 'SubCharacterPart'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.Integer, default=None)
    name = db.Column(db.String(45), default=None)
    HP = db.Column(db.Integer, default=0)
    MP = db.Column(db.Integer, default=0)
    Accuracy = db.Column(db.Integer, default=0)
    Evasion = db.Column(db.Integer, default=0)
    Defence = db.Column(db.Integer, default=0)
    Quickness = db.Column(db.Integer, default=0)
    Knowledge = db.Column(db.Integer, default=0)
    Require_knowledge = db.Column(db.Integer, default=0)
    VID = db.Column(db.Integer, default=0)
    MND = db.Column(db.Integer, default=0)
    detail = db.Column(db.String(455), default=None)
    weakpoint = db.Column(db.String(45), default=None)
    damage = db.Column(db.Integer, default=0)
    magic_power = db.Column(db.Integer, default=0)
    partnumber = db.Column(db.Integer, default=0)
    MagicDefence = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"SubCharacterPart(id={self.id}, name='{self.name}')"
    

class Equipment(db.Model):
    __tablename__ = 'Equipment'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(Integer, nullable=True)
    name = db.Column(db.String(45), nullable=True)
    type = db.Column(db.String(45), nullable=True)
    explain = db.Column(db.String(45), nullable=True)
    dex = db.Column(Integer, default=0)
    agi = db.Column(Integer, default=0)
    str = db.Column(Integer, default=0)
    vit = db.Column(Integer, default=0)
    int = db.Column(Integer, default=0)
    mnd = db.Column(Integer, default=0)
    dfn = db.Column(Integer, default=0) 
    evs = db.Column(Integer, default=0)
    dmg = db.Column(Integer, default=0)
    acr = db.Column(Integer, default=0)
    command = db.Column(db.String(45), nullable=True)
    knowledge = db.Column(Integer, default=0)
    quickness = db.Column(Integer, default=0)
    magic = db.Column(Integer, default=0)
    HP = db.Column(Integer, default=0)
    MP = db.Column(Integer, default=0)
    VITREG = db.Column(Integer, default=0)
    MNDREG = db.Column(Integer, default=0)

    def __repr__(self):
        return f"<Equipment(id={self.id}, name={self.name}, type={self.type})>"

class Memo(db.Model):
    __tablename__ = 'Memo'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    related_id = db.Column(db.String(45), nullable=True)
    content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Memo {self.id}>'
    
class MagicTable(db.Model):
    __tablename__ = 'MagicTable'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=True)
    master = db.Column(db.String(45), nullable=True)
    exptable = db.Column(db.String(45), nullable=True)

    def getUserMagic(self,character_id,magiclevel):
        magic = UserMagic.query.filter_by(related_id=character_id,name=self.name).first()
        if magic is None:
            magic = UserMagic(
                        name = self.name,
                        related_id = character_id,
                        level = magiclevel
                    )
        else:
            magic.level=magiclevel
        
        db.session.add(magic)
        db.session.commit()

        return magic

    def __repr__(self):
        return f'<MagicTable {self.id}>'
    

class UserMagic(db.Model):
    __tablename__ = 'UserMagic'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    level = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<UserMagic {self.id}>'
    

class Skill(db.Model):
    __tablename__ = 'Skill'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    getlevel = db.Column(db.Integer, nullable=True)
    getway = db.Column(db.String(45), nullable=True)
    effect = db.Column(db.String(45), nullable=True)
    explain = db.Column(db.String(45), nullable=True)
    command = db.Column(db.String(445), nullable=True)
    type = db.Column(db.String(445), nullable=True)

    def __repr__(self):
        return f'<Skill {self.id}>'
    
class Bullet(db.Model):
    __tablename__ = 'Bullet'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    個数 = db.Column(db.Integer, nullable=True)
    補正ダメージ = db.Column(db.Integer, nullable=True)
    補正命中 = db.Column(db.Integer, nullable=True)
    explain = db.Column(db.String(445), nullable=True)
    command = db.Column(db.String(445), nullable=True)
    消費MP = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Bullet {self.id}>'
    
class BulletBox(db.Model):
    __tablename__ = 'BulletBox'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    weapon_name = db.Column(db.String(45), nullable=True)
    related_id = db.Column(db.Integer, nullable=True)
    maxbullet = db.Column(db.Integer, nullable=True)
    col1 = db.Column(db.Integer, nullable=True)
    col2 = db.Column(db.Integer, nullable=True)
    col3 = db.Column(db.Integer, nullable=True)
    col4 = db.Column(db.Integer, nullable=True)
    col5 = db.Column(db.Integer, nullable=True)
    col6 = db.Column(db.Integer, nullable=True)
    col7 = db.Column(db.Integer, nullable=True)
    col8 = db.Column(db.Integer, nullable=True)
    col9 = db.Column(db.Integer, nullable=True)
    col10 = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<BulletBox {self.id}>'
    
class GameLog(db.Model):
    __tablename__ = 'GameLog'
    
    name = db.Column(db.String(45), primary_key=True)
    date = db.Column(db.Date)
    log = db.Column(db.Text)

    def __repr__(self):
        return f'<GameLog {self.name}>'

