import sys, random
from datetime import date
# sys.path.append("..")
from models.model import db, User, Scard
from sqlalchemy import update
from app import app
db.__init__(app)


today = date.today()

# 新增測試帳號
def create_user():
    for i in range(1000):
        user = User(email=f'test{i}@test.com', password='123', name=f'test{i}', collage='test collage', department='test department', gender='male', birthday=date(1996,5,23), verify=True, scard=True, days_no_open_scard=0)
        db.session.add(user)
    db.session.commit()
# create_user()

# 增加未開卡天數
def update_no_scard_days():
    User.query.filter(User.days_no_open_scard < 3).update({User.days_no_open_scard: User.days_no_open_scard + 1})
    db.session.commit()
# update_no_scard_days()


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

        # 將已經配對的id設為0
        user_list[user_index] = 0
        user_list[match_index] = 0

    # 最後的commit大約會花費25秒的時間，一次commit會比分開commit快很多倍
    db.session.commit()
    return 'ok'

match_user()


