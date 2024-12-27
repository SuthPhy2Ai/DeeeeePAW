from ase.db import connect
from tqdm import tqdm

mysql_url = 'mysql://root:@localhost:3306/temp_chg_sio'
db = connect('/data/chg/chg_aimd_sio2.db')

db2 = connect(mysql_url)

rows = []
for row in tqdm(db.select(), total=len(db)):
    rows.append(row)

for row in tqdm(rows, total=len(rows)):
    # try:
    db2.write(row.toatoms(), data=row.data)
    # except:
    #     continue




# import pandas as pd
# from sqlalchemy import create_engine, text, types
# import sqlite3
# import swifter
# import json


# # 连接到SQLite数据库
# sqlite_conn = sqlite3.connect('/data/chg/chg_mp_try.db')

# # 读取SQLite数据库中的所有表
# sqlite_cursor = sqlite_conn.cursor()
# sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = sqlite_cursor.fetchall()

# # sqlite_cursor.execute(f"SELECT * FROM {'systems'} LIMIT 1")
# # first_sample = sqlite_cursor.fetchone()


# # 连接到MySQL数据库
# mysql_engine = create_engine('mysql+pymysql://root:@localhost/temp_chg')

# column_types = {
#     'id': types.Integer,
#     'unique_id': types.String(length=32),
#     'ctime': types.Float,
#     'mtime': types.Float,
#     'username': types.Text,
#     'numbers': types.BLOB,
#     'positions': types.BLOB,
#     'cell': types.BLOB,
#     'pbc': types.Integer,
#     'initial_magmoms': types.BLOB,
#     'initial_charges': types.BLOB,
#     'masses': types.BLOB,
#     'tags': types.BLOB,
#     'momenta': types.BLOB,
#     'constraints': types.Text,
#     'calculator': types.Text,
#     'calculator_parameters': types.JSON,
#     'energy': types.Float,
#     'free_energy': types.Float,
#     'forces': types.BLOB,
#     'stress': types.BLOB,
#     'dipole': types.BLOB,
#     'magmoms': types.BLOB,
#     'magmom': types.Float,
#     'charges': types.BLOB,
#     'key_value_pairs': types.JSON,
#     'data': types.JSON,
#     'natoms': types.Integer,
#     'fmax': types.Float,
#     'smax': types.Float,
#     'volume': types.Float,
#     'mass': types.Float,
#     'charge': types.Float
# }

# ###########   species  #################
# # column_types = {
# #     'Z': types.Integer,
# #     'n': types.Integer,
# #     'id': types.Integer
# # }



# #########   keys   ##################
# # column_types = {
# #     'attribute_key': types.Text,
# #     'id': types.Integer
# # }


# ########  text_key_values   ############
# # column_types = {
# #     'attribute_key': types.Text,
# #     'value': types.Text,
# #     'id': types.Integer
# # }



# ########  number_key_values   ############  这个可能需要
# # column_types = {
# #     'attribute_key': types.Text,
# #     'value': types.Float,
# #     'id': types.Integer
# # }



# #########   information   ##################
# # column_types = {
# #     'name': types.Text,
# #     'value': types.Text
# # }



# with mysql_engine.connect() as conn:
#     df = pd.read_sql(f"SELECT * FROM {table_name}", sqlite_conn)
#     # df['data'] = df['data'].apply(lambda x: json.loads(x[np.frombuffer(x[:8], np.int64).item() :].decode()))
#     # df['data'] = df['data'].apply(lambda x: json.dumps(data_dict_process(x)))
#     df['data'] = df['data'].swifter.apply(lambda x: json.dumps(data_dict_process(x)))

# ############## 要判断calculator_parameters是否为None #######################
#     df['key_value_pairs'] = df['key_value_pairs'].apply(lambda x: json.loads(x))
#     df['id'] = df['id'].apply(lambda x: x + 1)
#     df.rename(columns={'key': 'attribute_key'}, inplace=True)
#     df.to_sql(table_name, mysql_engine, if_exists='replace', index=False, dtype=column_types)


# # 关闭数据库连接
# sqlite_conn.close()


# import json
# import numpy as np

# def data_dict_process(x):
#     dict_new = json.loads(x[np.frombuffer(x[:8], np.int64).item() :].decode())
#     shape, name, offset = dict_new['chg'].get('__ndarray__')
#     dtype = np.dtype(name)
#     size = dtype.itemsize * np.prod(shape).astype(int)
#     a = np.frombuffer(x[offset:offset + size], dtype)
#     nx = dict_new['nx']
#     ny = dict_new['ny']
#     nz = dict_new['nz']
#     dict_out = {'chg': a.tolist(), 'nx': nx, 'ny': ny, 'nz': nz}
#     return dict_out