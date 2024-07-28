import random
from dataclass import PowerDamage
import re
import copy
from main import db

# コマンドの変数を保存するリスト
variables = {}
challengebool = {}
Actor = ""
Targets = []

def execute_code(code,actor,targets):
    global Actor,Targets,variables
    results = [f'<<< {actor}:{code} >>>']
    commands = code.split(';')
    variables = {}
    Actor = actor
    Targets = targets
    variables["self"] = Actor  # 変数に値を格納

    for command in commands:
        command = command.strip()
        # command = replace_variables(command)
        log_message, output_value = process_command(command)
        results.append(log_message)
        if output_value is not None:
            variables['last_result'] = output_value  # 変数 'last_result' に結果を保存

    return "\n".join(results)

def process_command(command_input):
    # 変数代入とコマンドの分割処理
    assignment_pattern = r'^(\w+)\s*=\s*(.*)$'
    match = re.match(assignment_pattern, command_input)
    
    if match:
        variable_name = match.group(1)
        command = match.group(2).strip()
        command = replace_variables(command)
        log_message, output_value = execute_single_command(command)
        variables[variable_name] = output_value  # 変数に値を格納
        return f"{log_message} > {variable_name} に値を代入しました。", output_value
    else:
        if "loop" in command_input:
            command = command_input
        else:
            command = replace_variables(command_input)
        return execute_single_command(command)

def replace_variables(command):
    variable_pattern = r'\$(\w+)'  # $variable の形式で変数を検出
    matches = re.findall(variable_pattern, command)
    
    for match in matches:
        if match == "target":
            command = command.replace(f"${match}", match)
        elif match in variables:
            command = command.replace(f"${match}", str(variables[match]))

    return command

def execute_single_command(command):
    # Power(x, y) コマンドを処理する
    power_command_pattern = r'^power\((\d+),\s*(\d+)\)$'
    # dice(x,y) コマンドを処理する
    dice_command_pattern = r'^dice\((\d+),(\d+)\)$'
    # attack(x,y,z) コマンドを処理する
    attack_command_pattern = r'^attack\((\d+),(\d+)\)$'
    # ifmore(x,y,z) コマンドを処理する
    ifmore_command_pattern = r'^ifmore\((\d+),(\d+)\)$'
    # ifless(x,y,z) コマンドを処理する
    ifless_command_pattern = r'^ifless\((\d+),(\d+)\)$'
    # ifequal(x,y,z) コマンドを処理する
    ifequal_command_pattern = r'^ifequal\((\d+),(\d+)\)$'
    # ifeqmore(x,y,z) コマンドを処理する
    ifeqmore_command_pattern = r'^ifeqmore\((\d+),(\d+)\)$'
    # ifeqless(x,y,z) コマンドを処理する
    ifeqless_command_pattern = r'^ifeqless\((\d+),(\d+)\)$'
    # loop(x,y,z) コマンドを処理する
    loop_command_pattern = r'loop\s*\(\s*([\w]+\([^()]*\))\s*,\s*((?:[\w]+=)?[\w]+\([^()]*\)(?:\s*\+\s*(?:[\w]+=)?[\w]+\([^()]*\))*)\s*,\s*([\w]+\([^()]*\))\s*\)'
    # getStatus(キャラクター名, ステータス名) コマンドの正規表現パターン
    getstatus_command_pattern = r'^getstatus\(([^,]+),\s*([^,]+)\)$'
    # setStatus(キャラクター名, ステータス名) コマンドの正規表現パターン
    setstatus_command_pattern = r'^setstatus\(([^,]+),\s*([^,]+),\s*([^,]+)\)$'
    # actionif(boolean, コマンド) コマンドの正規表現パターン
    actionif_command_pattern = r'^actionif\((True|False|[a-zA-Z_]+\([^,]+,\s*[^,]+\)),\s*([a-zA-Z_]+\([^,]+,\s*[^,]+\))\)$'
    # plus(x,y) コマンドを処理する
    plus_command_pattern = r'^plus\((\d+),(\d+)\)$'
    # minus(x,y) コマンドを処理する
    minus_command_pattern = r'^minus\((\d+),(\d+)\)$'
    # multiply(x,y) コマンドを処理する
    multiply_command_pattern = r'^multiply\((\d+),(\d+)\)$'
    # divide(x,y) コマンドを処理する
    divide_command_pattern = r'^divide\((\d+),(\d+)\)$'
    # challenge(x,y) コマンドを処理する
    challenge_command_pattern = r'^challenge\((\w+),\s*(\w+)\)$'
    # challenge(x,y) コマンドを処理する
    challenge_status_command_pattern = r'^challenge_status\((\w+),\s*(\w+)\)$'
    # getmax(x,y) コマンドを処理する
    getmax_command_pattern = r'^getmax\((\d+(?:,\s*\d+)*)\)$'
    # getmin(x,y) コマンドを処理する
    getmin_command_pattern = r'^getmin\((\d+(?:,\s*\d+)*)\)$'
    # getsum(x,y) コマンドを処理する
    getsum_command_pattern = r'^getsum\((\d+(?:,\s*\d+)*)\)$'
    # physical_attack(x) コマンドを処理する
    physical_attack_command_pattern = r'^physical_attack\((\d+)\)$'
    # magical_attack(x,y) コマンドを処理する
    magical_attack_command_pattern = r'^magical_attack\(([^,]+),\s*([^,]+),\s*([^,]+)\)$'
    # monstercriticalloop(x) コマンドを処理する
    monstercriticalloop_command_pattern = r'^monstercriticalloop\((\d+)\)$'
    # getweapon(x,y) コマンドを処理する
    getweapon_command_pattern = r'^getweapon\(([^,]+),\s*([^,]+)\)$'
    # getprotector(x,y) コマンドを処理する
    getprotector_command_pattern = r'^getprotector\(([^,]+),\s*([^,]+)\)$'
    # shoot_attack(x,y) コマンドを処理する
    shoot_attack_command_pattern = r'^shoot_attack\((\d+),(\d+)\)$'
    # magishoot_attack(x,y) コマンドを処理する
    magishoot_attack_command_pattern = r'^magishoot_attack\((\d+),(\d+),(\d+)\)$'
    # useitem(x,y) コマンドを処理する
    useitem_command_pattern = r'^useitem\((\d+),(\d+)\)$'
    # heal(キャラクター名, ステータス名) コマンドの正規表現パターン
    heal_command_pattern = r'^heal\(([^,]+),\s*([^,]+)\)$'
    # getjoblevel(キャラクター名, ステータス名) コマンドの正規表現パターン
    getjoblevel_command_pattern = r'^getjoblevel\(([^,]+),\s*([^,]+)\)$'
    # fixattack(攻撃タイプ, ダメージ量) コマンドの正規表現パターン
    fixattack_command_pattern = r'^fixattack\(([^,]+),\s*([^,]+)\)$'

    match = re.match(power_command_pattern, command)
    if match:
        return power(match.group(1), match.group(2))
    
    match = re.match(dice_command_pattern, command)
    if match:
        return dice(match.group(1), match.group(2))

    match = re.match(attack_command_pattern, command)
    if match:
        return monsterattack(match.group(1), match.group(2))   
    
    match = re.match(fixattack_command_pattern, command)
    if match:
        return fixattack(match.group(1), match.group(2))  
    
    match = re.match(ifmore_command_pattern, command)
    if match:
        return ifmore(match.group(1), match.group(2))
    
    match = re.match(ifless_command_pattern, command)
    if match:
        return ifless(match.group(1), match.group(2))
    
    match = re.match(ifequal_command_pattern, command)
    if match:
        return ifequal(match.group(1), match.group(2))
    
    match = re.match(ifeqmore_command_pattern, command)
    if match:
        return ifeqmore(match.group(1), match.group(2))
    
    match = re.match(ifeqless_command_pattern, command)
    if match:
        return ifeqless(match.group(1), match.group(2))
    
    match = re.match(loop_command_pattern, command)
    if match:
        return loop(match.group(1), match.group(2) , match.group(3))
    
    match = re.match(getstatus_command_pattern, command)
    if match:
        return getstatus(match.group(1), match.group(2))
    
    match = re.match(setstatus_command_pattern, command)
    if match:
        return setstatus(match.group(1), match.group(2), match.group(3))
    
    match = re.match(actionif_command_pattern, command)
    if match:
        return actionif(match.group(1), match.group(2))
    
    match = re.match(plus_command_pattern, command)
    if match:
        return plus(match.group(1), match.group(2))
    
    match = re.match(minus_command_pattern, command)
    if match:
        return minus(match.group(1), match.group(2))
    
    match = re.match(multiply_command_pattern, command)
    if match:
        return multiply(match.group(1), match.group(2))
    
    match = re.match(divide_command_pattern, command)
    if match:
        return divide(match.group(1), match.group(2))
    
    match = re.match(challenge_command_pattern, command)
    if match:
        log_message, value, _ = challenge(match.group(1), match.group(2))
        return log_message, value
    
    match = re.match(challenge_status_command_pattern, command)
    if match:
        log_message, value, _ = challenge_status(match.group(1), match.group(2))
        return log_message, value
    
    match = re.match(getmax_command_pattern, command)
    if match:
        return getmax(match.group(1))
    
    match = re.match(getmin_command_pattern, command)
    if match:
        return getmin(match.group(1))
    
    match = re.match(getsum_command_pattern, command)
    if match:
        return getsum(match.group(1))
    
    match = re.match(physical_attack_command_pattern, command)
    if match:
        return physical_attack(match.group(1))
    
    match = re.match(magical_attack_command_pattern, command)
    if match:
        return magical_attack(match.group(1),match.group(2),match.group(3))
    
    match = re.match(monstercriticalloop_command_pattern, command)
    if match:
        return monstercriticalloop(match.group(1))
    
    match = re.match(getweapon_command_pattern, command)
    if match:
        return getweapon(match.group(1),match.group(2))
    
    match = re.match(getprotector_command_pattern, command)
    if match:
        return getprotector(match.group(1),match.group(2))
    
    match = re.match(magishoot_attack_command_pattern, command)
    if match:
        return magishoot_attack(match.group(1),match.group(2),match.group(3))
    
    match = re.match(shoot_attack_command_pattern, command)
    if match:
        return shoot_attack(match.group(1),match.group(2))
    
    match = re.match(useitem_command_pattern, command)
    if match:
        return useitem(match.group(1),match.group(2))
    
    match = re.match(heal_command_pattern, command)
    if match:
        return heal(match.group(1),match.group(2))
    
    match = re.match(getjoblevel_command_pattern, command)
    if match:
        return getjoblevel(match.group(1),match.group(2))
    
    else:
        log_message = "サポートされていないコマンドです。"
        return log_message, None


def loop(init, code, trigger):
    count = 0
    log_messages = ''
    result = '1'
    bool = sub_code(init)[1]
    while bool == True and count < 20:
        count +=  1
        command = copy.copy(trigger)
        log_message,result = sub_code(code)
        nextbool = sub_code(command)[1]
        bool = nextbool
        log_messages = log_messages+","+str(log_message)+","+f"ループ繰り返し: {bool}"

    return log_messages, result

def actionif(bool, command):
    if bool == "True":
        log_message,result = sub_code(command)
        return log_message,result 
    else:
        bool = sub_code(bool)[1]
        if bool == True:
            log_message,result = sub_code(command)
            return log_message,result 
        else:
            log_message = "実行なし"
            return log_message,None
    
def sub_code(code):
    log_message = ""
    commands = code.split('+')
    for command in commands:
        command = command.strip()
        command = replace_variables(command)
        message, output_value = process_command(command)
        log_message = log_message + message
    if output_value is not None:
        variables['result'] = output_value
    return log_message,output_value


def dice(x, y):
    num_dice = int(x)
    num_sides = int(y)
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    sum_value = sum(rolls)
    log_message = f"ダイス結果: {', '.join(map(str, rolls))} (合計: {sum_value})"
    return log_message, sum_value

def getstatus(unit_name,status_name):
    if unit_name == "target":
        log_message = ""
        for target in Targets:
            message,status_value=getstatus(target,status_name)
            log_message = log_message + message

        return log_message,status_value

    from dataclass import Unit
    unit = Unit.query.filter_by(name=unit_name).first()

    if unit is None:
        log_message = "ユニットが存在しません"
        return log_message,None
    else:
        try:
            status_value = getattr(unit,status_name)
            log_message = f"{unit_name}の{status_name}: {status_value}"
        except:
            status_value = 0
            log_message = f"{unit_name}に'{status_name}'というステータスは存在しません"
        if unit.type == "魔物":
            log_message = f"魔物のステータスは閲覧できません。"
        
    return log_message,status_value

def setstatus(unit_name,status_name,value):
    from dataclass import Unit

    if unit_name == "target":
        log_message = ""
        for target in Targets:
            message,status_value=setstatus(target,status_name,value)
            log_message = log_message + message

        return log_message,status_value

    unit = Unit.query.filter_by(name=unit_name).first()
    value = int(value)

    if unit is None:
        log_message = "ユニットが存在しません"
        return log_message,None
    
    else:
        try:
            # MP軽減ありの時計算
            if status_name == "MP":
                if value < 0:
                    mpcover = unit.MP軽減
                    value = int(value) + int(mpcover)
                    unit.MP軽減 = unit.MP消費カット
                    if value > 0:
                        value = 0

            status_value = getattr(unit,status_name)
            new_value = status_value + int(value)
            setattr(unit,status_name,new_value)
            db.session.add(unit)
            db.session.commit()
            if unit.type == "魔物":
                log_message = f" {unit_name}の{status_name}を {value} 変化させました。"
            else:
                log_message = f" {unit_name}の{status_name}を {value} 変化させました。 現在{status_name}: {new_value}"
        except:
            log_message = f" {unit_name}に'{status_name}'というステータスは存在しません。"
            new_value = 0
        
    return log_message,new_value

def getweapon(weapon_id,status_name):
    from dataclass import Weapon
    weapon = Weapon.query.filter_by(id=weapon_id).first()

    if weapon is None:
        log_message = f" ID{weapon_id}の武器が存在しません。"
        return log_message,None
    else:
        try:
            status_value = getattr(weapon,status_name)
            log_message = f" {weapon.name}の{status_name}: {status_value}"
        except:
            log_message = f" {weapon.name}に'{status_name}'というステータスは存在しません。"
        
    return log_message,status_value

def getprotector(protetor_id,status_name):
    from dataclass import Protector
    weapon = Protector.query.filter_by(id=protetor_id).first()

    if weapon is None:
        log_message = f" ID{protetor_id}の防具が存在しません。"
        return log_message,None
    else:
        try:
            status_value = getattr(weapon,status_name)
            log_message = f" {weapon.name}の{status_name}: {status_value}"
        except:
            log_message = f" {weapon.name}に'{status_name}'というステータスは存在しません。"
        
    return log_message,status_value

def power(x, y):
    power_value = int(x)
    column_number = int(y)
    
    # データベースから値を取得
    power_damage = PowerDamage.query.filter_by(Power=power_value).first()
    
    if not power_damage:
        return f" Power {power_value} のレコードが見つかりません。", None
    
    # カラム名を動的に構築
    column_name = f"col{column_number}"
    
    if not hasattr(power_damage, column_name):
        return f" カラム {column_number} が存在しません。", None
    
    column_value = getattr(power_damage, column_name)
    log_message = f" 威力 {power_value} のダメージは {column_value} です。"
    return log_message, int(column_value)

def monsterattack(critical, additionaldamage):
    log_message, dice_value = dice(2, 6)
    maindamage = dice_value + int(additionaldamage)
    damage_value = maindamage
    critical_value = int(critical)

    # 命中判定
    message, bool, dicevalue = challenge_status("命中","回避")
    log_message += message

    # クリティカル計算
    critical_line = int(critical_value)
    if dicevalue >= int(critical_line):
        message, cvalue = monstercriticalloop(critical_line)
        damage_value = maindamage + cvalue
        log_message = log_message + "クリティカル計算:" + message
    
    # ターゲットに対するダメージ計算
    for target in Targets:
        if challengebool[target] == True:
            message = f" {target}に{damage_value}のダメージを与えます。"
            log_message += message

            defence = getstatus(target,"防護点")[1]
            actualdamage = (damage_value - defence) * (-1)
            if actualdamage > 0:
                actualdamage = 0
            message, newHP = setstatus(target,"HP",actualdamage)
        else:
            message = f" {target}は回避しました。"
            log_message += message

    return log_message, damage_value

def fixattack(type,value):
    log_message  = f" ダメージ固定攻撃。"
    # 命中判定
    if type == "物理":
        Accuracy = int(getstatus(Actor,"命中")[1])
        message, bool, dicevalue = challenge(Accuracy,"回避")
    elif type == "魔法":
        magicchallenge = int(getstatus(Actor,"魔力")[1])
        message, bool, dicevalue = challenge(magicchallenge,"精神抵抗")
    else:
        log_message = "タイプは物理か魔法です。"
        damage_value = 0
        return log_message, damage_value
    
    log_message += message

    damage_value = int(value)
    maindamage = damage_value
    # ターゲットに対するダメージ計算
    for target in Targets:
        if type == "物理":
            defence = getstatus(target,"防護点")[1]
        elif type == "魔法":
            defence = getstatus(target,"魔法耐性")[1]

        if challengebool[target] == True:
            damage_value = maindamage
            defence = int(defence)
            message = f" {target}に{damage_value}のダメージを与えます。"
            log_message += message
            actualdamage = (damage_value - defence) * (-1)
            if actualdamage > 0:
                actualdamage = 0
            message, newHP = setstatus(target,"HP",actualdamage)
            
        else:
            if dicevalue == 2:
                damage_value = 0
                message = f"  {target}への攻撃は自動失敗しました。"
                log_message = log_message + message
            else:
                if type == "物理":
                    damage_value = maindamage // 2
                    message = f" {target}は回避しました。"
                    log_message = log_message + message
                elif type == "魔法":
                    damage_value = maindamage // 2
                    message = f" {target}は抵抗しました。{target}に{damage_value}のダメージを与えます。"
                    log_message = log_message + message
                    actualdamage = (damage_value - defence) * (-1)
                    if actualdamage > 0:
                        actualdamage = 0
                    message, newHP = setstatus(target,"HP",actualdamage)

    return log_message, damage_value

def ifmore(x, y):
    x = int(x)
    y = int(y)
    result = x > y
    log_message = f"大きい: {result}"
    return log_message, result

def ifeqmore(x, y):
    x = int(x)
    y = int(y)
    result = x >= y
    log_message = f" 以上: {result}"
    return log_message, result

def ifless(x, y):
    x = int(x)
    y = int(y)
    result = x < y
    log_message = f" 小さい: {result}"
    return log_message, result

def ifeqless(x, y):
    x = int(x)
    y = int(y)
    result = x <= y
    log_message = f" 以下: {result}"
    return log_message, result

def ifequal(x, y):
    x = int(x)
    y = int(y)
    result = x == y
    log_message = f" 等しい: {result}"
    return log_message, result

def plus(x, y):
    x = int(x)
    y = int(y)
    result = x + y
    log_message = f" 和: {result}"
    return log_message, result

def minus(x, y):
    x = int(x)
    y = int(y)
    result = x - y
    log_message = f" 差: {result}"
    return log_message, result

def multiply(x, y):
    x = int(x)
    y = int(y)
    result = x * y
    log_message = f" 積: {result}"
    return log_message, result

def divide(x, y):
    x = int(x)
    y = int(y)
    if y == 0:
        result = 0
        log_message = f" 0で割っています。"
    else:
        x = int(x)
        y = int(y)
        result = x // y
        log_message = f" 商: {result}"
    return log_message, result

def getmax(numlist):
    # カンマで分割し、リストに変換
    numbers = [int(num.strip()) for num in numlist.split(',')]
    # 最大値を計算
    max_value = max(numbers)
    log_message = f' {numbers}の最大値は{max_value}です。'
    return log_message, max_value

def getmin(numlist):
    # カンマで分割し、リストに変換
    numbers = [int(num.strip()) for num in numlist.split(',')]
    # 最大値を計算
    min_value = min(numbers)
    log_message = f' {numbers}の最小値は{min_value}です。'
    return log_message, min_value

def getsum(numlist):
    # カンマで分割し、リストに変換
    numbers = [int(num.strip()) for num in numlist.split(',')]
    # 最大値を計算
    sum_value = sum(numbers)
    log_message = f' {numbers}の合計値は{sum_value}です。'
    return log_message, sum_value


def challenge_status(mystatus,targetstatus):
    mybonus = getstatus(Actor,mystatus)[1]
    message,mydice = dice(2,6)
    myvalue = int(mybonus) + int(mydice)
    myresult = message

    if getstatus(Actor,"type")[1] == "魔物":
        log_message = f" << {Actor}の{myresult} >> "
    else:
        log_message = f" << {Actor}の{myresult} 補正値:{mybonus} 判定値:{myvalue} >> "
    

    for target in Targets:
        targetbonus = getstatus(target,targetstatus)[1]
        message,tdice = dice(2,6)
        tvalue = int(targetbonus) + int(tdice)
        tresult = message

        if int(mydice) == 2:
            bool = False
        elif int(tdice) == 12:
            bool = False
        elif int(mydice) == 12 and int(tdice) != 12 :
            bool = True
        elif int(mydice) != 2 and int(tdice) == 2:
            bool = True
        else:
            bool = myvalue > tvalue

        challengebool[target] = bool

        if getstatus(target,"type")[1] == "魔物":
            log_message = log_message + f" << {target}の{tresult},判定:{bool} >> "
        else:
            log_message = log_message + f" << {target}の{tresult} 補正値:{targetbonus} 判定値:{tvalue} 判定:{bool} >> "
            print(log_message)
    return log_message, bool, mydice

def challenge(bonus,targetstatus):
    mybonus = int(bonus)
    message,mydice = dice(2,6)
    myvalue = int(mybonus) + int(mydice)
    myresult = message

    if getstatus(Actor,"type")[1] == "魔物":
        log_message = f" << {Actor}の{myresult} >> "
    else:
        log_message = f" << {Actor}の{myresult} 補正値:{mybonus} 判定値:{myvalue} >> "
    

    for target in Targets:
        targetbonus = getstatus(target,targetstatus)[1]
        message,tdice = dice(2,6)
        tvalue = int(targetbonus) + int(tdice)
        tresult = message

        if int(mydice) == 2:
            bool = False
        elif int(tdice) == 12:
            bool = False
        elif int(mydice) == 12 and int(tdice) != 12 :
            bool = True
        elif int(mydice) != 2 and int(tdice) == 2:
            bool = True
        else:
            bool = myvalue > tvalue

        challengebool[target] = bool

        if getstatus(target,"type")[1] == "魔物":
            log_message = log_message + f" << {target}の{tresult},判定:{bool} >> "
        else:
            log_message = log_message + f" << {target}の{tresult} 補正値:{targetbonus} 判定値:{tvalue} 判定:{bool} >>"
            print(log_message)
    return log_message, bool, mydice


def physical_attack(weapon_id):
    from dataclass import Weapon,Unit
    
    try:
        # 基本ダメージ計算
        basicdamage = getstatus(Actor,"基本ダメージ")[1]
        weapondamage = getweapon(weapon_id,"追加ダメージ")[1]
        if weapondamage is None:
            weapondamage = 0
        weaponpower = getweapon(weapon_id,"威力")[1]
        weaponcritical = getweapon(weapon_id,"クリティカル")[1]
        criticalbonus = getstatus(Actor,"クリティカルボーナス")[1]

        damage = int(basicdamage) + int(weapondamage)
        log_message = f"武器威力:{weaponpower} 基本追加ダメージ:{damage}"

        # 命中判定
        Accuracy = int(getstatus(Actor,"命中")[1]) + int(getweapon(weapon_id,"命中")[1])
        message, bool, dicevalue = challenge(Accuracy,"回避")
        log_message += message

        # ダメージ結果
        powerdamage = power(int(weaponpower),int(dicevalue))[1]
        maindamage = int(basicdamage) + int(weapondamage) + powerdamage
        damage_value = maindamage

        message = f"  基礎ダメージ:{powerdamage}"
        log_message += message

        # クリティカル計算
        critical_line = int(weaponcritical) - int(criticalbonus)
        if dicevalue >= int(critical_line):
            message, cvalue = criticalloop(critical_line,weaponpower)
            damage_value = maindamage + cvalue
            log_message += "クリティカル計算:" + message

        # ターゲットに対するダメージ計算
        for target in Targets:
            if challengebool[target] == True:
                message = f" {target}に{damage_value}のダメージを与えます。"
                log_message += message

                defence = getstatus(target,"防護点")[1]
                actualdamage = (damage_value - defence) * (-1)
                if actualdamage > 0:
                    actualdamage = 0
                message, newHP = setstatus(target,"HP",actualdamage)
            else:
                message = f" {target}は回避しました。"
                log_message += message

    except Exception as e:
        log_message += f"\nエラーが発生しました: {str(e)}"

    return log_message, damage_value

def magical_attack(mpower,mp,magictype):
    from dataclass import Unit,UserMagic

    log_message = f" MPを{mp}消費します。"
    # MP消費
    mp = int(mp)
    mp = -mp

    message, newHP = setstatus(Actor,"MP",mp)
    log_message += message

    # 使用する魔法の基本ダメージ計算
    unit = Unit.query.filter_by(name=Actor).first()
    magic = UserMagic.query.filter_by(related_id=unit.id,name=magictype).first()
    magiclevel = magic.level
    magicbonus = getstatus(Actor,"魔力ボーナス")[1]
    magicpower = int(magiclevel) + int(magicbonus)

    criticalbonus = 0

    log_message += f" 魔法レベル:{magiclevel} 魔法威力:{mpower} 魔力:{magicpower}"

    # 抵抗判定
    magicchallenge = magicpower + int(unit.魔法行使判定)
    message, bool, dicevalue = challenge(magicchallenge,"精神抵抗")
    log_message += message

    # ダメージ結果
    powerdamage = power(int(mpower),int(dicevalue))[1]
    # 魔力＋威力のダイスダメージ
    maindamage = magicpower + powerdamage
    damage_value = maindamage

    cvalue=0
    # クリティカル計算
    critical_line = 10 - int(criticalbonus)
    if dicevalue >= int(critical_line):
        message, cvalue = criticalloop(critical_line,mpower)
        log_message += " クリティカル計算:" + message

    # ターゲットに対するダメージ計算
    for target in Targets:
        defence = getstatus(target,"魔法耐性")[1]
        if challengebool[target] == True:
            damage_value = maindamage + cvalue
            message = f"  {target}に{damage_value}のダメージを与えます。"
            log_message += message
            actualdamage = (damage_value - defence) * (-1)
            if actualdamage > 0:
                actualdamage = 0
            message, newHP = setstatus(target,"HP",actualdamage)
            
        else:
            if dicevalue == 2:
                damage_value = 0
                message = f"  {target}への魔法は自動失敗しました。"
                log_message = log_message + message
            else:
                damage_value = maindamage // 2
                message = f"  {target}に{damage_value}の半減ダメージを与えます。"
                log_message = log_message + message

                actualdamage = (damage_value - defence) * (-1)
                if actualdamage > 0:
                    actualdamage = 0
                message, newHP = setstatus(target,"HP",actualdamage)

    return log_message, damage_value

def shoot_attack(wpower,weapon_id):
    from dataclass import BulletBox,Bullet

    log_message = "" 

    mybox = BulletBox.query.filter_by(related_id=weapon_id).first()
    mybullet = Bullet.query.filter_by(id=mybox.col1).first()

    # ユニット情報
    criticalbonus = getstatus(Actor,"クリティカルボーナス")[1]
    unitaccuracy = getstatus(Actor,"命中")[1]
    basicdamage = getstatus(Actor,"基本ダメージ")[1]
    # 武器情報
    weaponcritical = getweapon(weapon_id,"クリティカル")[1]
    weaponaccuracy = getweapon(weapon_id,"命中")[1]
    # 弾情報
    bulletacr = mybullet.補正命中
    bulletdmg = mybullet.補正ダメージ
    bulletmp = mybullet.消費MP

    mp = -int(bulletmp) 
    message, newMP = setstatus(Actor,"MP",mp)
    log_message += message

    criticalbonus = 0

    mybox = usebullet(mybox)

    # 命中判定
    Accuracy = int(unitaccuracy) + int(weaponaccuracy) + int(bulletacr)
    message, bool, dicevalue = challenge(Accuracy,"回避")
    log_message += message

    # ダメージ結果
    powerdamage = power(int(wpower),int(dicevalue))[1]
    # 物理＋威力のダイスダメージ
    maindamage = powerdamage + int(bulletdmg) + int(basicdamage)
    damage_value = maindamage

    cvalue=0
    # クリティカル計算
    critical_line = 10 - int(criticalbonus)
    if dicevalue >= int(critical_line):
        message, cvalue = criticalloop(critical_line,wpower)
        log_message += "クリティカル計算:" + message
        damage_value = maindamage + cvalue

    # ターゲットに対するダメージ計算
    for target in Targets:
        if challengebool[target] == True:
            message = f"  {target}に{damage_value}のダメージを与えます。"
            log_message += message

            actualdamage = (damage_value) * (-1)
            message, newHP = setstatus(target,"HP",actualdamage)
            
        else:
            message = f"  {target}は回避しました。"
            log_message += message

    return log_message, damage_value


def magishoot_attack(mpower,mp,weapon_id):
    from dataclass import Unit,UserMagic,BulletBox,Bullet,Weapon

    mybox = BulletBox.query.filter_by(related_id=weapon_id).first()

    if mybox.col1 is None or mybox.col1 == "":
        log_message = "不発！弾がありません。"
        damage_value = 0
        return log_message, damage_value

    mybullet = Bullet.query.filter_by(id=mybox.col1).first()
    if mybullet is None:
        log_message = "不発！弾がありません。"
        damage_value = 0
        return log_message, damage_value

    # ユニット情報
    criticalbonus = getstatus(Actor,"クリティカルボーナス")[1]
    unitaccuracy = getstatus(Actor,"命中")[1]
    # 武器情報
    weaponcritical = getweapon(weapon_id,"クリティカル")[1]
    weaponaccuracy = getweapon(weapon_id,"命中")[1]
    # 弾情報
    bulletacr = mybullet.補正命中
    bulletdmg = mybullet.補正ダメージ
    bulletmp = mybullet.消費MP

    # MP消費
    mp = int(mp) + int(bulletmp)
    log_message = f" MPを{mp}消費します。"
    mp = -mp

    message, newMP = setstatus(Actor,"MP",mp)
    log_message += message

    # 使用する魔法の基本ダメージ計算
    unit = Unit.query.filter_by(name=Actor).first()
    magic = UserMagic.query.filter_by(related_id=unit.id,name="魔動機術").first()
    magiclevel = magic.level
    magicbonus = getstatus(Actor,"魔力ボーナス")[1]
    magicpower = int(magiclevel) + int(magicbonus)

    criticalbonus = 0

    log_message += f" 魔動機術レベル:{magiclevel} 威力:{mpower} 魔力:{magicpower}"

    mybox = usebullet(mybox)
    mybullet.個数 = int(mybullet.個数) - 1
    db.session.add(mybullet)
    db.session.commit()
    
    # 命中判定
    Accuracy = int(unitaccuracy) + int(weaponaccuracy) + int(bulletacr)
    message, bool, dicevalue = challenge(Accuracy,"回避")
    log_message += message

    # ダメージ結果
    powerdamage = power(int(mpower),int(dicevalue))[1]
    # 魔力＋威力のダイスダメージ
    maindamage = magicpower + powerdamage + int(bulletdmg)
    damage_value = maindamage

    cvalue=0
    # クリティカル計算
    critical_line = 10 - int(criticalbonus)
    if dicevalue >= int(critical_line):
        message, cvalue = criticalloop(critical_line,mpower)
        log_message += "クリティカル計算:" + message
        damage_value = maindamage + cvalue

    # ターゲットに対するダメージ計算
    for target in Targets:
        if challengebool[target] == True:
            message = f"  {target}に{damage_value}のダメージを与えます。"
            log_message += message

            actualdamage = (damage_value) * (-1)
            message, newHP = setstatus(target,"HP",actualdamage)
            
        else:
            message = f"  {target}は回避しました。"
            log_message += message

    return log_message, damage_value

def usebullet(mybox):
    for i in range(mybox.maxbullet-1):
        cola = f'col{i+2}'
        colb = f'col{i+1}'
        bid = getattr(mybox,cola)
        setattr(mybox,colb,bid)

        db.session.add(mybox)
        db.session.commit()
    
    return mybox

def criticalloop(critical,powerscore):
    log_message, dvalue = dice(2,6)
    message, score = power(powerscore,dvalue)
    log_message = log_message + message
    if dvalue > critical:
        message, cvalue = criticalloop(critical,powerscore)
        log_message = log_message + message
        bonus = int(score) + cvalue
        return log_message, int(bonus)
    else:
        return log_message, int(score)
    
def monstercriticalloop(critical):
    log_message, dvalue = dice(2,6)
    if dvalue > critical:
        message, cvalue = monstercriticalloop(critical)
        log_message = log_message + message
        bonus = int(cvalue)
        return log_message, bonus
    else:
        return log_message, bonus


def useitem(item_id,num):
    from dataclass import Item
    item = Item.query.filter_by(id=item_id).first()
    if not item is None:
        log_message = f'{item.name}を{num}個使用しました。'
        result=0
        item_num = int(item.num) 
        for i in range(int(num)):
            command = item.command
            message,result = sub_code(command)
            log_message += message
            if item.type == "消耗品":
                item_num -= 1
            
        item.num = item_num
        db.session.add(item)
        db.session.commit()
    else:
        log_message = "アイテムが見つかりません。"
        result = 0
    
    return log_message,result


def heal(unit_name,value):
    if unit_name == "target":
        log_message = ""
        for target in Targets:
            message,status_value=heal(target,value)
            log_message = log_message + message

        return log_message,status_value

    from dataclass import Unit
    unit = Unit.query.filter_by(name=unit_name).first()
    status_value = 0

    if unit is None:
        log_message = "ユニットが存在しません"
        return log_message,None
    else:
        try:
            status_value = getattr(unit,"HP")
            healbonus = unit.回復ボーナス
            healvalue = int(value) + int(healbonus)
            status_value = status_value + healvalue
            setattr(unit,"HP",status_value)
            db.session.add(unit)
            db.session.commit()
            log_message = f"{healvalue}の回復を行います。{unit_name}のHP: {status_value}"
        except:
            status_value = 0
            log_message = f"{unit_name}にHPというステータスは存在しません"
        if unit.type == "魔物":
            log_message = f"魔物のステータスは閲覧できません。"
        
    return log_message,status_value

def getjoblevel(unit_name,jobname):
    log_message = ""
    if unit_name == "target":
        for target in Targets:
            message,joblevel=getjoblevel(target,jobname)
            log_message += message

        return log_message,joblevel

    from dataclass import Unit,Job
    unit = Unit.query.filter_by(name=unit_name).first()

    if unit is None:
        log_message = "ユニットが存在しません"
        return log_message,None
    else:
        job = Job.query.filter_by(related_id=unit.related_id,name=jobname).first()
        if job is None:
            log_message = f'{jobname}は習得していません。'
            return log_message, None
        
        joblevel = job.level
        log_message = f'{unit_name}の{jobname}レベルは{joblevel}です。'
        
    return log_message,joblevel



