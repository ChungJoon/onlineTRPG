from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)

# データベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Zxcv0987@dbtrpg.crk2e8m6wj6j.ap-northeast-1.rds.amazonaws.com:3306/TRPG'
# 例: 'mysql+pymysql://root:password@localhost:3306/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# データベースオブジェクトの作成
db = SQLAlchemy(app)

# Characterモデルの定義
class Character(db.Model):
    __tablename__ = 'Character'  # テーブル名を指定

    # カラムの定義
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(45), unique=True, nullable=False)
    type = db.Column(db.String(45), nullable=False)
    age = db.Column(db.Integer)
    background = db.Column(db.String(45))
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
    experience = db.Column(db.Integer)

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

# アプリケーションコンテキストを使用する
with app.app_context():   

    # データベースからすべてのCharacterのIDを取得
    # character_ids = db.session.query(Character.id).all()
    # print("All Character IDs:", [id_tuple[0] for id_tuple in character_ids])

    # ステータスを変数として取得
    DEX= 6
    AGI= 6
    STR= 6
    VIT= 6
    INT= 6
    MND= 6
    LEVEL= 13
    MP= 40
    MAG= 15

    # 新しいステータスの作成
    my_status = Status(
        id= 2,  # CharacterのIDを参照
        related_id = 2,
        name= 'b_Status',
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