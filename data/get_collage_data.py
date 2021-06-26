import pandas
import numpy
from app import mysql_host, mysql_user, mysql_password, mysql_database
import mysql.connector


db = mysql.connector.connect(
    host = mysql_host,
    user = mysql_user,
    password = mysql_password,
    database = mysql_database
)
cursor = db.cursor()

# 建立collage內容
df = pandas.read_excel('collage_department_109.ods', engine="odf", usecols=[0,3])
data = numpy.array(df)

collages = data.tolist()
collage_list = []
for collage in collages:
    if collage in collage_list:
        continue
    else:
        collage_list.append(collage)
print(collage_list)

for collage in collage_list:
    print(collage[0], collage[1])
    sql = 'INSERT INTO collage(id, name) VALUES(%s, %s)'
    val = (collage[0], collage[1])
    cursor.execute(sql, val)
db.commit()    

# 建立department內容
df = pandas.read_excel('collage_department_109.ods', engine="odf", usecols=[0, 3, 6])
data = numpy.array(df)
dpts = data.tolist()
for dpt in dpts:
    print(dpt[0], dpt[2])
    sql = 'INSERT INTO collage_department(collage_id, name) VALUES(%s, %s)'
    val = (dpt[0], dpt[2])
    cursor.execute(sql, val)
db.commit()    

