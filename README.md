# [Scard](https://scard.skysea.fun/b)

本專案為Dcard複製品，主功能如下：

1. 帳號系統：個人帳號之建置、認證與個人資料填寫。
2. 抽卡系統：每日進行不重複對象之抽卡配對，雙方送出交友邀請後可在聊天室對談互動。
3. 文章系統：使用者可以發佈文章並在文章下留言、按讚、追蹤，並設有通知系統，隨時發送追蹤貼文的最新通知。

## Demo
點擊該網址即可前往Scard登入頁面 : https://scard.skysea.fun/b

已開通所有權限的Test帳號：</br>
Account : test1@test.com ~ test1000@test.com</br>
Password : 123

亦可在註冊/登入頁面建立自己的帳號（註冊當下即登入），成為網站會員之一

## 使用技術
* **Python Flask**
* **Multi-thread** (強化抽卡配對效率)
* **MySQL + Redis** (資料庫系統)
* **Socket.io + Redis Pub/Sub + ELB** (實踐多開機器情境的聊天/通知播送功能)
* **AWS &nbsp; EC2 / ELB / RDS / S3 / CDN / ElastiCache**
* **BootStrap5**
* **Facebook / Google Login**
## 功能介紹

### 瀏覽首頁

登入首頁後即可看到文章列表，並能點選進入不同的文章分頁
![image](https://user-images.githubusercontent.com/73434165/125581872-2fb36f19-f011-4c0b-88eb-670ec0a81476.png)

### 登入／註冊

在登入／註冊頁面輸入帳號密碼，未註冊過的帳號會同時處理註冊與登入，已註冊過的帳號則會辨別帳號密碼是否正確。
![image](https://user-images.githubusercontent.com/73434165/125582373-d90e5ae8-d6fe-42b9-ace2-c015fa513932.png)

### 帳戶功能

* 使用者登入後若要編輯自我介紹、撰寫貼文，都要做基本資料的撰寫

![image](https://user-images.githubusercontent.com/73434165/125604428-a0e9eeca-8dad-4f52-98ef-bcf1b5dd5200.png)

* 以下分別呈現撰寫、瀏覽貼文頁面
  
![image](https://user-images.githubusercontent.com/73434165/125604268-c49e9ccb-3754-4df7-8feb-2f06577e3444.png)

![image](https://user-images.githubusercontent.com/73434165/125581650-0fd06bb4-e01e-406f-8c3e-071b2fa37aa6.png)

### 抽卡機制  

* 本網站採用與Dcard相同基礎的抽卡機制：每到午夜12點，符合抽卡資格者將會在抽卡頁面瀏覽到當天的Scard，已經抽過的卡將永遠不再被配對到。
* 抽卡的配對在前一天的23:59進行，目前已測試10萬人配對，可以在30秒內完成。使用者在午夜00:00:00即可看到當天配對的Scard資訊。
* 三天沒有開啟Scard頁面者將暫時失去抽卡資格，直到使用者重新點開scard頁面，即會獲得隔天的抽卡機會(23:59後開卡者不算)。
* 若兩人都送出交友邀請，兩人將成為卡友

![image](https://user-images.githubusercontent.com/73434165/122116836-ae33b400-ce58-11eb-90dd-b086f1c16093.png)

### 聊天機制

* 成為好友的兩人可以進行送信聊天，聊天以socket.io實作，朋友的最新對話也會隨時更新至好友欄順序呈現

![image](https://user-images.githubusercontent.com/73434165/122117614-a58fad80-ce59-11eb-89b8-86ec7923084f.png)


### MySQL資料庫架構
![image](https://user-images.githubusercontent.com/73434165/125291328-d7f6d280-e353-11eb-8fba-bcf5b6c55d5b.png)
