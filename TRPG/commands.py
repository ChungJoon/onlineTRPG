import random
from dataclass import PowerDamage
import re
import copy

# コマンドの変数を保存するリスト
variables = {}

def execute_code(code):
    results = []
    commands = code.split(';')
    variables = {}

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
        return f"{log_message} {variable_name} に {output_value} を代入しました。", output_value
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
        if match in variables:
            command = command.replace(f"${match}", str(variables[match]))

    return command

def execute_single_command(command):
    # Power(x, y) コマンドを処理する
    power_command_pattern = r'^power\((\d+),\s*(\d+)\)$'
    # dice(x,y) コマンドを処理する
    dice_command_pattern = r'^dice\((\d+),(\d+)\)$'
    # attack(x,y,z) コマンドを処理する
    attack_command_pattern = r'^attack\((\d+),(\d+),(\d+)\)$'
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

    match = re.match(power_command_pattern, command)
    if match:
        return power(match.group(1), match.group(2))
    
    match = re.match(dice_command_pattern, command)
    if match:
        return dice(match.group(1), match.group(2))

    match = re.match(attack_command_pattern, command)
    if match:
        return attack(match.group(1), match.group(2), match.group(3))   
    
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

    else:
        log_message = "サポートされていないコマンドです。"
        return log_message, None


def loop(init, code, trigger):
    count = 0
    log_messages = ''
    result = '1'
    bool = loop_code(init)[1]
    while bool == True and count < 10:
        count +=  1
        command = copy.copy(trigger)
        log_message,result = loop_code(code)
        nextbool = loop_code(command)[1]
        bool = nextbool
        log_messages = log_messages+","+str(log_message)+","+f"ループ繰り返し: {bool}"

    return log_messages, result

def loop_code(code):
    results = []
    commands = code.split('+')
    for command in commands:
        command = command.strip()
        command = replace_variables(command)
        log_message, output_value = process_command(command)
        results.append(log_message)
    if output_value is not None:
        variables['result'] = output_value
    return results,output_value
    
def dice(x, y):
    num_dice = int(x)
    num_sides = int(y)
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    sum_value = sum(rolls)
    log_message = f"{num_sides}面ダイスを{num_dice}個振った結果: {', '.join(map(str, rolls))} (合計: {sum_value})"
    return log_message, sum_value

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

def attack(critical, powerclass, additionaldamage):
    log_message_dice, dice_value = dice(2, 6)
    log_message_power, power_value = power(powerclass, dice_value)
    log_message_dice += log_message_power
    sum_value = power_value + int(additionaldamage)
    critical_value = int(critical)

    while dice_value >= critical_value:
        log_message_dice += f"\nCritical hit! ダイスの値が {critical_value} 以上なので追加の攻撃を行います。\n"
        log_message_dice_attack, dice_value_attack = dice(2, 6)
        log_message_power_attack, power_value_attack = power(powerclass, dice_value_attack)
        log_message_dice += log_message_dice_attack + log_message_power_attack
        sum_value += power_value_attack
    
    log_message = f"{log_message_dice}\n最終的な攻撃結果は {sum_value} です。"
    return log_message, sum_value

def ifmore(x, y):
    x = int(x)
    y = int(y)
    result = x > y
    log_message = f"{x} が {y} より大きいか: {result}"
    return log_message, result

def ifeqmore(x, y):
    x = int(x)
    y = int(y)
    result = x >= y
    log_message = f"{x} は {y} 以上か: {result}"
    return log_message, result

def ifless(x, y):
    x = int(x)
    y = int(y)
    result = x < y
    log_message = f"{x} が {y} より小さいか: {result}"
    return log_message, result

def ifeqless(x, y):
    x = int(x)
    y = int(y)
    result = x <= y
    log_message = f"{x} は {y} 以下か: {result}"
    return log_message, result

def ifequal(x, y):
    x = int(x)
    y = int(y)
    result = x == y
    log_message = f"{x} と {y} は等しいか: {result}"
    return log_message, result

