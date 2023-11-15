import pandas as pd
import sqlite3

from functools import wraps
from flask import redirect, session


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_framework(path, sheet, columns):
    try:
        df = pd.read_excel(path, sheet_name=sheet, usecols=columns)
        df = df.dropna()
        for c in df.columns:
            df[c] = df[c].round(2)
        return df
    except Exception as e:
        raise Exception(f"Error al obtener FrameWork de {path}: {str(e)}")
    

def get_head(path, sheet):
    head = {"Date": None, "Location": None, "Alarm": None, "Wp": None, "Part": None}
    row = 3

    try:
        for c in head:
            head[c] = pd.read_excel(path, sheet_name=sheet).iloc[row, 1]
            row += 2 if row == 6 or row == 4  else 1
        return head
    except Exception as e:
        raise Exception(f"Error al obtener header de {path}: {str(e)}")
    
    
def export_data(dict, df):
    conn = sqlite3.connect('WORK.db')
    cursor = conn.cursor()

    try:
        head = corrected_dict(dict)

        columns_d = ', '.join(head.keys())
        values_d = ', '.join(['?'] * len(head))

        sql_data = f'INSERT INTO data ({columns_d}) VALUES ({values_d})'

        cursor.execute(sql_data, list(head.values())) 
        data_id = cursor.lastrowid

        columns_p = '", "'.join(df.keys())
        values_p = ', '.join(['?'] * len(df.columns))

        sql_param = f'INSERT INTO Parameters ("{columns_p}") VALUES ({values_p})'
        relation = f'INSERT INTO Relation (id_data, id_parameter) VALUES (?, ?)'
        
        for _, row in df.iterrows():
            framework_values = row.tolist()

            cursor.execute(sql_param, framework_values)
            parameters_id = cursor.lastrowid

            cursor.execute(relation, (data_id, parameters_id))

        conn.commit()
    except Exception as e:
        print (f"Error al exportar datos: {e}")
    finally:
        conn.close()


def corrected_dict(dict):
    head = {"Date": None, "Alarm": None, "Wp": None, "Part": None}

    try:
        for data in dict:
            if data != 'Location':
                head[data] = dict[data]
    except Exception as e:
        raise Exception(f"Error al obtener dict: {str(e)}")
    
    head['Robot'] = int(dict['Location'][3])
    head['Cell'] = dict['Location'][5:].split(':')[0]
    head['Cell'] = cell_name(head['Cell'])

    return head


def cell_name(cell):
    if cell == "10.32.51.61":
        cell = "5.01"
    elif cell == "10.32.51.74":
        cell = "5.02"
    elif cell == "10.32.51.100":
        cell = "5.04"
    elif cell == "10.32.51.127":
        cell = "5.06"
    elif cell == "10.32.51.141":
        cell = "5.07"
    elif cell == "10.32.51.154":
        cell = "5.08"
    elif cell == "10.32.51.168":
        cell = "5.09"
    elif cell == "10.31.51.181":
        cell = "5.10"
    elif cell == "10.32.52.61":
        cell = "5.11"
    elif cell == "10.32.52.140":
        cell = "5.12"
    elif cell == "10.32.51.113":
        cell = "5.13"
    elif cell == "10.32.52.101":
        cell = "5.14"
    elif cell == "10.32.52.127":
        cell = "5.16"
    elif cell == "10.32.52.75":
        cell = "5.17"
    elif cell == "10.32.52.154":
        cell = "5.18"
    elif cell == "10.32.55.21":
        cell = "5.20"
    elif cell == "10.32.55.22":
        cell = "5.21"
    elif cell == "10.32.109.106":
        cell = "5.23"

    return cell