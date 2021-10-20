# [Scard](https://scard.skysea.fun/b)

本專為參考Dcard的社群論壇與交友平台，主功能如下：

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

* Python Flask
* RESTful API架構實踐專案功能
* 支援Facebook / Google Login，並對直接註冊使用者進行email驗證
* 結合Bootstrap完成網頁版面設置
* 以原生Contenteditable實作文章編輯系統
* 使用index加速MySQL查詢效率
* 使用Redis存取個人資料快取與通知
* 運用Multi-thread加速抽卡配對效率
* 以S3儲存使用者上傳的圖片與大頭貼
* 結合Socket.io + Redis pub/sub + ELB實踐多開機器情境的聊天 / 通知播送功能
* 申請SSL憑證實踐HTTPS

## 系統架構圖

![image](https://user-images.githubusercontent.com/73434165/125689230-d7c18637-3669-42a1-9416-8c690d22273f.png)

## MySQL資料庫架構
![image](https://user-images.githubusercontent.com/73434165/125606523-74c5a56d-2e0e-4e50-a7a1-7f05b5b52178.png)


## 功能介紹

### 瀏覽首頁

登入首頁後即可看到文章列表，並能點選進入不同的文章分頁。
![image](https://user-images.githubusercontent.com/73434165/125607108-6d6180fc-b4a7-48fb-877a-5c476c12e0c4.png)

### 登入／註冊

在登入／註冊頁面輸入帳號密碼，未註冊過的帳號會同時處理註冊與登入，已註冊過的帳號則會辨別帳號密碼是否正確。

![image](https://user-images.githubusercontent.com/73434165/125607300-d8f4d0ec-0f88-45c6-9d75-5c8c66214670.png)

### 帳戶功能

* 使用者登入後若要編輯自我介紹、撰寫貼文，都要做基本資料的撰寫。

![image](https://user-images.githubusercontent.com/73434165/125607552-81825dc6-7ffd-4cce-aa2c-7a294b3ae003.png)

* 以下分別呈現撰寫、瀏覽貼文頁面。
  
![image](https://user-images.githubusercontent.com/73434165/125604268-c49e9ccb-3754-4df7-8feb-2f06577e3444.png)

![image](https://user-images.githubusercontent.com/73434165/125606823-a0f1cc6a-3608-40c3-ba29-eeda3583e46c.png)

### 抽卡機制  

* 本網站採用與Dcard相同基礎的抽卡機制：每到午夜12點，符合抽卡資格者將會在抽卡頁面瀏覽到當天的Scard，已經抽過的卡將永遠不再被配對到。
* 為增加配對效率，當抽卡人次多於1萬人時將使用muti-thread分為10條子執行緒進行，加速配對效率
* 抽卡的配對在前一天的23:59進行，10萬人配對可在30秒內完成。使用者在午夜00:00:00即可看到當天配對的Scard資訊。
* 三天沒有開啟Scard頁面者將暫時失去抽卡資格，直到使用者重新點開scard頁面，即會獲得隔天的抽卡機會(23:59後開卡者不算)。
* 若兩人都送出交友邀請，兩人將成為卡友

![image](https://user-images.githubusercontent.com/73434165/125691939-591113f1-c092-4da2-accc-b4a5040e6c04.png)

### 聊天機制

* 成為好友的兩人可以進行送信聊天，聊天以socket.io實作，好友的最新回應也會隨時更新，並調整好友欄呈現順序。

![image](https://user-images.githubusercontent.com/73434165/125691429-43909640-8b17-4d31-8571-7129958dd6fb.png)
