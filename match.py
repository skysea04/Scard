import sys, random, math, time, json
from datetime import date, timedelta
import threading
from models.model import db, User, Scard, cache
import mysql.connector
from app import app, mysql_host, mysql_user, mysql_password, mysql_database
db.__init__(app)



'''
測試區
'''
start_time = time.time()
today = date.today()
yesterday = today - timedelta(days=1)
dby = yesterday - timedelta(days=1)

'''
測試區
'''
# 新增測試帳號
def create_user():
    def add_user(f_id, l_id):
        user_db = mysql.connector.connect(
            host = mysql_host,
            user = mysql_user,
            password = mysql_password,
            database = mysql_database
        )
        user_cursor = user_db.cursor()
        
        for i in range(f_id, l_id):
            sql = 'INSERT INTO user (email, password, name, collage, department, gender, birthday, verify_status, days_no_open_scard) VALUES (%s, %s, %s, %s, %s, %s, %s ,%s ,%s ,%s)'
            val = (f'test{i}@test.com', '123', f'測試人員{i}', 'test collage', 'test department', 'male', date(1996,5,23), 'scard', 0)
            user_cursor.execute(sql, val)
            print(i)

            # user = User(email=f'test{i}@test.com', password='123', name=f'test{i}', collage='test collage', department='test department', gender='male', birthday=date(1996,5,23), verify=True, scard=True, days_no_open_scard=0)
            # db.session.add(user)

        user_db.commit()
    n = 0
    thread_num = 1
    threads = []
    for i in range(thread_num):
        threads.append(threading.Thread(target=add_user, args= ((i+n)*1000+1, (i+1+n) * 1000+1)))
        threads[i].start()
   
    for i in range(thread_num):
        threads[i].join()

# 增加未開卡天數
def update_no_scard_days():
    User.query.filter(User.days_no_open_scard <= 3).update({User.days_no_open_scard: User.days_no_open_scard + 1})
    db.session.commit()


# 建立配對
def match_user():
    # 建立本次要抽卡的使用者清單, 第一位測試帳號永遠開放抽卡
    user_list = []
    all_users = User.query.filter(User.days_no_open_scard < 3).all()
    for user in all_users:
        user_list.append(user.id)
    
    # 查看本次抽卡人數，若非偶數則剔除第一位測試帳號
    user_count = len(user_list)
    if user_count % 2 != 0:
        user_list.remove(1)
        user_count = len(user_list)
    print(user_count)
    for user_index in range(user_count - 1):
        user_id = user_list[user_index]

        # user_id若已經配對過則值為0，不用再配對，直接進入下一輪
        if user_id == 0: continue

        # 查詢該使用者過去的配對記錄，存到old_match_list中 
        # 這裡的連線在配對1000名使用者的情況下總共會需要運行約20秒的時間
        old_match_list = []
        old_matches = Scard.query.filter_by(user_1=user_id).all()
        for old_match in old_matches:
            old_match_list.append(old_match.user_2)
        
        # 隨機配對一位使用者，配對者id一定大於(>)使用者id
        match_index = random.randrange(user_index + 1, user_count)
        match_id = user_list[match_index]

        # 若match_id為零（已在本輪配對過），或是已經有過相同的配對紀錄(old_match_list)，則重新配對一次
        while (match_id == 0) or (match_id in old_match_list):
            match_index = random.randrange(user_index + 1, user_count)
            match_id = user_list[match_index]
        
        print('user_id: ', user_id, ', match_id: ', match_id)
        match = Scard(user_1=user_id, user_2=match_id)
        db.session.add(match)

        # 先幫使用者們做好抽卡流程的快取
        # scard_1 = Scard.view_scard_1(user_id, today)
        # scard_2 = Scard.view_scard_2(match_id, today)

        # 將已經配對的id設為0
        user_list[user_index] = 0
        user_list[match_index] = 0

    # 最後的commit大約會花費25秒的時間，一次commit會比分開commit快很多倍
    db.session.commit()
    return 'ok'

# 建立配對(比對user的match_list)
def match_user_method_2():
    db.session.execute('DELETE FROM scard WHERE is_friend IS Null AND create_date = :dby', {"dby": dby})

    # 建立本次要抽卡的使用者清單, 第一位測試帳號永遠開放抽卡
    user_list = []
    matches_list = []
    all_users = User.query.filter(User.days_no_open_scard < 3).all()
    for user in all_users:
        user_list.append(user.id)
        matches_list.append(user.match_list)
    
    # 查看本次抽卡人數，若非偶數則剔除第一位測試帳號
    user_count = len(user_list)
    if user_count % 2 != 0:
        del user_list[0]
        del matches_list[0]
        user_count = len(user_list)
    print(user_count)
    for user_index in range(user_count - 1):
        user_id = user_list[user_index]
        match_list = matches_list[user_index]

        # user_id若已經配對過則值為0，不用再配對，直接進入下一輪
        if user_id == 0: continue
        
        # 隨機配對一位使用者，配對者id一定大於(>)使用者id
        match_index = random.randrange(user_index + 1, user_count)
        match_id = user_list[match_index]

        # 若match_id為零（已在本輪配對過），或是已經有過相同的配對紀錄(old_match_list)，則重新配對一次
        while (match_id == 0) or (match_id in match_list):
            match_index = random.randrange(user_index + 1, user_count)
            match_id = user_list[match_index]
        
        match_list.append(match_id)
        db.session.execute('UPDATE user SET match_list=JSON_ARRAY_APPEND(match_list, "$" , :match_id) WHERE id=:user_id', {"user_id":user_id, "match_id": match_id})
        # User.query.filter_by(id=user_id).update({User.match_list: match_list})
        
        print('user_id: ', user_id, ', match_id: ', match_id)
        db.session.execute('INSERT INTO scard (user_1, user_2) VALUES (:user_id, :match_id, :date)', {"user_id":user_id, "match_id":match_id})
        # match = Scard(user_1=user_id, user_2=match_id)
        # db.session.add(match)

        # 先幫使用者們做好抽卡流程的快取
        scard_1 = Scard.view_scard_1(user_id, today)
        scard_2 = Scard.view_scard_2(match_id, today)

        # 將已經配對的id設為0
        user_list[user_index] = 0
        user_list[match_index] = 0

    # 最後的commit大約會花費25秒的時間，一次commit會比分開commit快很多倍
    db.session.commit()
    return 'ok'

# 建立配對(多執行緒)
def match_user_method_3():
    new_db = mysql.connector.connect(
            host = mysql_host,
            user = mysql_user,
            password = mysql_password,
            database = mysql_database
        )
    new_cursor = new_db.cursor()
    # 刪掉昨天沒有成為朋友的配對
    new_cursor.execute('DELETE FROM scard WHERE is_friend IS False AND create_date=%s', (dby,))

    # 建立本次要抽卡的使用者清單, 第一位測試帳號永遠開放抽卡
    new_cursor.execute('UPDATE user SET days_no_open_scard=0 WHERE id=1')
    new_db.commit()
    user_list, matches_list = [], []
    new_cursor.execute('SELECT id, match_list FROM user WHERE verify_status="scard" AND days_no_open_scard <= 3')
    all_users = new_cursor.fetchall()
    for user in all_users:
        user_list.append(user[0])
        matches_list.append(json.loads(user[1]))
    
    new_db.close()

    # 查看本次抽卡人數，若非偶數則剔除第一位測試帳號
    user_count = len(user_list)
    if user_count % 2 != 0:
        del user_list[0]
        del matches_list[0]
        user_count -= 1
    # print(user_count)

    # 配對函式
    def matching(first_index, end_index):
        # print(first_index, end_index)
        
        scard_db = mysql.connector.connect(
            host = mysql_host,
            user = mysql_user,
            password = mysql_password,
            database = mysql_database
        )
        cursor = scard_db.cursor()

        for user_index in range(first_index, end_index):
            user_id = user_list[user_index]
            match_list = matches_list[user_index]

            # user_id若已經配對過則值為0，不用再配對，直接進入下一輪
            if user_id == 0: continue

            # 隨機配對一位使用者，配對者id一定大於(>)使用者id
            match_index = random.randrange(user_index + 1, end_index)
            match_id = user_list[match_index]

            # 若match_id為零（已在本輪配對過），或是已經有過相同的配對紀錄(old_match_list)，則重新配對一次
            while (match_id == 0) or (match_id in match_list):
                match_index = random.randrange(user_index + 1, end_index)
                match_id = user_list[match_index]

            print('user_id: ', user_id, ', match_id: ', match_id)
            cursor.execute('UPDATE user SET match_list=JSON_ARRAY_APPEND(match_list, "$" , %s) WHERE id=%s'%(match_id, user_id))
           
            cursor.execute('INSERT INTO scard (user_1, user_2) VALUES (%s, %s)'%(user_id, match_id))
            # 將已經配對的id設為0
            user_list[user_index] = 0
            user_list[match_index] = 0

        scard_db.commit() 
        scard_db.close()
        
        return 'ok'
    
    # 如果配對人數不多，直接執行配對函式
    if user_count <= 10000:
        matching(0, user_count)

    # 若人數大於10000，分10個執行緒，執行配對函式
    else:
        group_user_count = math.ceil(user_count / 10)
        # print(group_user_count)

        # 確認每組人數也都是偶數
        if (group_user_count % 2) != 0:
            group_user_count += 1

        threads = []
        # 永遠開10個執行緒跑
        for i in range(10):
            if i == 9:
                threads.append(threading.Thread(target=matching, args= (i*group_user_count, user_count)))
            else:
                threads.append(threading.Thread(target=matching, args= (i*group_user_count, (i+1)*group_user_count)))
            threads[i].start()
    
        for i in range(10):
            threads[i].join()

# 新增測試帳號
# create_user()

# 增加未開卡天數
update_no_scard_days()

# 建立配對(ver0.1)
# match_user()

# 建立配對(ver0.2 比對user的match_list)
# match_user_method_2()

# 建立配對(ver0.3 多執行緒)
match_user_method_3()

end_time = time.time()
print(f'共花{end_time-start_time}秒')