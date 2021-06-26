# [Scard](http://54.249.129.189:8000/b)

本專案為Dcard複製品，專案內容還在建置中，目前已完成功能：帳號系統、基本資料、自介填寫、抽卡配對、聊天系統、PO文系統(首頁瀏覽熱門貼文尚未完成)。
## Demo
點擊該網址即可前往Scard登入頁面 : http://54.249.129.189:8000/b

已開通所有權限的Test帳號：</br>
Account : test1@test.com ~ test1000@test.com</br>
Password : 123

亦可在註冊/登入建立自己的帳號，成為網站會員之一

## 使用技術
* Python Flask
* Socket.io
* AWS EC2 RDS S3 CDN ElastiCache
* BootStrap5
* Responsive Web Design(聊天頁面除外)

## 功能介紹

### 登入／註冊

在登入／註冊頁面輸入帳號密碼，未註冊過的帳號會同時處理註冊與登入，已註冊過的帳號則會辨別帳號密碼是否正確。
![image](https://user-images.githubusercontent.com/73434165/122114542-fd2c1a00-ce55-11eb-97f5-127ec0f9d879.png)


### 帳戶功能

* 使用者登入後若要編輯自我介紹、撰寫貼文，都要做基本資料的撰寫

![image](https://user-images.githubusercontent.com/73434165/123520759-d935c780-d6e4-11eb-806c-bd983e0e47b2.png)

* 以下分別呈現撰寫、瀏覽貼文、自我介紹編輯畫面
  
![image](https://user-images.githubusercontent.com/73434165/123520686-69274180-d6e4-11eb-942e-1229926abf29.png)

![image](https://user-images.githubusercontent.com/73434165/123520549-ddadb080-d6e3-11eb-86d6-6d1fc2a52fe8.png)

![image](https://user-images.githubusercontent.com/73434165/122115394-04075c80-ce57-11eb-90f0-7ff80f0ed7b0.png)

### 抽卡機制  

* 本網站採用與Dcard相同基礎的抽卡機制：每到午夜12點，符合抽卡資格者將會在抽卡頁面瀏覽到當天的Scard，已經抽過的卡將永遠不再被配對到。
* 抽卡的配對在前一天的23:59進行，目前已測試10萬人配對，可以在30秒內完成。使用者在午夜00:00:00即可看到當天配對的Scard資訊。
* 三天沒有開啟Scard頁面者將暫時失去抽卡資格，直到使用者重新點開scard頁面，即會獲得隔天的抽卡機會(23:59後開卡者不算)。
* 若兩人都送出交友邀請，兩人將成為卡友

![image](https://user-images.githubusercontent.com/73434165/122116836-ae33b400-ce58-11eb-90dd-b086f1c16093.png)

![image](https://user-images.githubusercontent.com/73434165/122117004-e63af700-ce58-11eb-97b0-56fc8a9ceae2.png)

### 聊天機制

* 成為好友的兩人可以進行送信聊天，聊天以socket.io實作，朋友的最新對話也會隨時更新至好友欄順序呈現

![image](https://user-images.githubusercontent.com/73434165/122117614-a58fad80-ce59-11eb-89b8-86ec7923084f.png)
