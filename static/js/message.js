//// 切換訊息與卡友資訊分頁
const messageNav = document.querySelector('#nav-message')
const friendInfoNav = document.querySelector('#nav-friend-info')
const messageField = document.querySelector('.messages')
const friendInfoPage = document.querySelector('.friend-info')

function showMessage(e){
    e.preventDefault()
    messageNav.classList.add('active')
    friendInfoNav.classList.remove('active')
    messageField.classList.add('d-block')
    friendInfoPage.classList.remove('d-block')
}
function showFriendInfo(e){
    e.preventDefault()
    messageNav.classList.remove('active')
    friendInfoNav.classList.add('active')
    messageField.classList.remove('d-block')
    friendInfoPage.classList.add('d-block')
}

messageNav.addEventListener('click', showMessage)
friendInfoNav.addEventListener('click', showFriendInfo)


//// 獲取好友列表
const messageRoomAPI = '/api/message_room'
const friendlistAPI = '/api/friendlist'
const friendList = document.querySelector('.friends .list-group')
async function getFriends(){
    // 清空後重新render
    const res = await fetch(friendlistAPI)
    const data = await res.json()
    // 列出朋友
    if(data.data){ // 正常render資料
        friendList.innerHTML = ''
        data.data.forEach(friend => {
            // 獲取個別朋友資訊
            getFriend(friend)
        })
    }else{ //出現錯誤，顯示提示Modal
        showErrorModal(data)
    }
}

// 獲取好友列表最新聊天內容
function getFriend(friend){
    // 朋友姓名
    const friendName = document.createElement('h6')
    friendName.innerText = friend.name
    friendName.classList.add('name', 'text-white', 'm-0')

    // 訊息時間
    const messageTime = document.createElement('p')
    messageTime.innerText = friend.time
    messageTime.classList.add('time', 'text-white-50', 'm-0', 'f-14')
    
    // 朋友資訊內框
    const innerContainer = document.createElement('div')
    innerContainer.classList.add('d-flex', 'justify-content-between', 'align-items-center', 'mb-1', 'lh-l')

    innerContainer.append(friendName, messageTime)
    
    // 最近信件
    const lastestMessage = document.createElement('p')
    lastestMessage.innerText = friend.message
    lastestMessage.classList.add('short-letter', 'm-0', 'text-truncate', 'text-white-50')

    // 朋友資訊外框
    const outerContainer = document.createElement('div')
    outerContainer.classList.add('w-220', 'p-2')

    outerContainer.append(innerContainer, lastestMessage)
    
    // 朋友頭像
    const avatar = document.createElement('img')
    avatar.src = friend.avatar
    avatar.classList.add('rounded')

    // 朋友欄位連結(最大框)
    const a = document.createElement('a')
    a.classList.add('friend', 'p-3', 'pe-0','d-flex', 'w-100')
    const messageHref = `/message/${friend.messageRoomId}`
    if(messageHref == location.pathname){
        a.classList.add('active')
    }
    a.href = messageHref
    a.append(avatar, outerContainer)

    friendList.append(a)
}

getFriends()

//// 獲取聊天訊息
const messageRoomId = location.pathname.split('/').pop()
const messageAPI = `/api/message/${messageRoomId}?page=`
let messagePage = 0
const messageList = document.querySelector('.messages ul')
const messageLoadIcon = document.querySelector('#message-load')
const userAvatar = document.querySelector('.send-message .message-avatar img')

////滾動render////
let options = {threshold: 0.5}
// 符合設定條件下，loading icon進入viewport時觸發此 callback 函式
let renderNextMessages = (entries) => {
    // entries 能拿到所有目標元素進出(intersect)變化的資訊
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            //  目標元素進入 viewport 時做一些事情
            getMessages()
        } 
    })
}
let observer = new IntersectionObserver(renderNextMessages, options)

observer.observe(messageLoadIcon)
///////////////

// 定義使用者ID, 姓名, 頭像 變數
let usrID, usrName, usrAvatar, friendID, friendName
// 獲取朋友自介資訊與聊天訊息
async function getMessages(){
    const res = await fetch(messageAPI+messagePage)
    const data = await res.json()
    if(data.data){ //正常render資料
        const user = data.user
        const friend = data.friend
        usrID = user.id
        usrName = user.name 
        usrAvatar= user.avatar
        friendName = friend.name
        friendID = friend.id
        // 更動messagePage判斷有沒有下一頁
        messagePage = data.nextPage
        if(messagePage == null){
            messageLoadIcon.style.display = 'none'
        }
        
        // render friend資訊頁
        let relationship
        switch(friend.relationship){
            case 'secret':
                relationship = '秘密'
                break
            case 'single':
                relationship = '單身'
                break
            case 'in_a_relationship':
                relationship = '穩定交往中'
                break
            case 'complicated':
                relationship = '一言難盡'
                break
            case 'open_relationship':
                relationship = '交往中但保有交友空間'
                break
            default:
                relationship = '不顯示'
        }
        const friendInfo = document.querySelector('.friend-info')
        friendInfo.querySelector('.avatar-container img').src = friend.avatar
        friendInfo.querySelector('.friend-name').innerText = friend.name
        friendInfo.querySelector('.collage').innerText = friend.collage
        friendInfo.querySelector('.department').innerText = friend.department
        friendInfo.querySelector('.birthday').innerText = friend.birthday
        friendInfo.querySelector('.relationship').innerText = relationship
        friendInfo.querySelector('.interest').innerText = friend.interest
        friendInfo.querySelector('.club').innerText = friend.club
        friendInfo.querySelector('.course').innerText = friend.course
        friendInfo.querySelector('.country').innerText = friend.country
        friendInfo.querySelector('.worry').innerText = friend.worry
        friendInfo.querySelector('.swap').innerText = friend.swap
        friendInfo.querySelector('.want-to-try').innerText = friend.wantToTry
        
        // render 朋友頁nav
        const navMessage = document.querySelector('#nav-message')
        const navFriendInfo = document.querySelector('#nav-friend-info')
        navMessage.innerText = `${friend.name}來信`
        navFriendInfo.innerText = `關於${friend.name}`

        // render 自己的送信頭像
        userAvatar.src = user.avatar

        // 填充訊息
        data.data.forEach(message => {
            // 訊息發送者頭貼
            const avatar = document.createElement('img')
            avatar.src = message.userId === user.id ? user.avatar : friend.avatar
            avatar.classList.add('rounded-circle')

            // 頭貼外框
            const avatarContainer = document.createElement('div')
            avatarContainer.classList.add('message-avatar', 'pt-2')
            avatarContainer.append(avatar)

            // 訊息發送者
            const messageUser = document.createElement('h6')
            messageUser.innerText =message.userId === user.id ? user.name : friend.name
            messageUser.classList.add('name', 'text-black-50', 'm-0')

            // 訊息日期
            const messageTime = document.createElement('p')
            messageTime.innerText = message.time
            messageTime.classList.add('time', 'text-black-50', 'm-0', 'f-14')

            // 訊息資訊內框
            const innerContainer = document.createElement('div')
            innerContainer.classList.add('d-flex', 'justify-content-between', 'align-items-center', 'mb-1', 'lh-l')
            innerContainer.append(messageUser, messageTime)

            // 訊息
            const theMessage = document.createElement('p')
            theMessage.innerText = message.message
            theMessage.classList.add('letter', 'pt-2', 'm-0')

            // 訊息資訊外框
            const outerContainer = document.createElement('div')
            outerContainer.classList.add('py-3', 'w-100')
            outerContainer.append(innerContainer, theMessage)

            // 訊息欄位最外層
            const li = document.createElement('li')
            li.classList.add('list-group-item', 'd-flex')
            li.append(avatarContainer, outerContainer)

            messageLoadIcon.insertAdjacentElement('beforebegin', li);

            // messageList.append(li)
        })
    }else{ //出現錯誤，顯示提示Modal
        showErrorModal(data)
    }
}

//// 刪除好友
const delFriendAPI = `/api/scard/${messageRoomId}`
const delDot = document.querySelector('.del-dots')
const delBtn = document.createElement('a')
delBtn.className = 'btn  text-danger '
delBtn.innerText = '刪除好友'
const delPopover = new bootstrap.Popover(delDot, {
    container: 'body',
    placement: "bottom",
    html: true,
    trigger: 'manual',
    content: delBtn
})

delDot.addEventListener('click', ()=>{
    delPopover.toggle()
})
delDot.addEventListener('blur', ()=>{
    delPopover.hide()
})

// delModal變數
const delModalContain = document.getElementById('del-modal')
const delModal = new bootstrap.Modal(delModalContain)
const delModalTitle = delModalContain.querySelector('.modal-title')
const delModalBody = delModalContain.querySelector('.modal-body')
const delModalHref = delModalContain.querySelector('.modal-href')

// 請使用者確認是否刪除好友
function showDelModal(){
    delModalBody.innerText = `確定要刪除卡友「${friendName}」嗎？`
    delModal.show()
}
// 執行刪除好友動作
async function delFriend(){
    const friendData = {
        friendID: friendID
    }
    const res = await fetch(delFriendAPI, {
        method: 'DELETE',
        body: JSON.stringify(friendData),
        headers: {'content-type': 'application/json'}
    })
    const data = await res.json()
    // console.log(data)
    data.ok ? location = '/message' : showErrorModal(data)
    delModal.hide()
}

delBtn.addEventListener('click', showDelModal)
delModalHref.addEventListener('click', delFriend)


//// 傳送訊息
socket.on('connect', function(){
    fetch(messageRoomAPI)
    .then(res => res.json())
    .then(data => {
        if(data.data){
            data.data.forEach(roomId => {
                // console.log(roomId)
                socket.emit('join_room', roomId.toString())
            })
        }
    })

    const message = document.querySelector('#send-message')
    const sendBtn = document.querySelector('#send-btn')

    function sendMessage(){
        const alertMessage = document.querySelector('#alert-message')
        if(message.value == ''){ // 如果沒有輸入內容顯示提醒文字，並不送出訊息
            alertMessage.innerText = '尚未輸入內容！'
        }
        else{ // 若有內容送出訊息
            alertMessage.innerText = ''
            socket.emit('send_message', {
                id: usrID,
                name: usrName,
                avatar: usrAvatar,
                room: messageRoomId,
                message: message.value.trim()
            })
            message.value = ''
        }
    }

    sendBtn.addEventListener('click', sendMessage)
})

socket.on('receive_message', data => {
    // console.log(data)
    // 當使用者在該正確聊天頁面才更新訊息在聊天視窗
    if(data.room == messageRoomId){
        receiveMessage(data)    
    }
    // 更新朋友訊息欄位的資訊
    updatefriendList(data)
})

// 更新聊天資訊
function receiveMessage(data){
    // 訊息發送者頭貼
    const avatar = document.createElement('img')
    avatar.src = data.avatar
    avatar.classList.add('rounded-circle')

    // 頭貼外框
    const avatarContainer = document.createElement('div')
    avatarContainer.classList.add('message-avatar', 'pt-2')
    avatarContainer.append(avatar)

    // 訊息發送者
    const messageUser = document.createElement('h6')
    messageUser.innerText = data.name
    messageUser.classList.add('name', 'text-black-50', 'm-0')

    // 訊息日期
    const messageTime = document.createElement('p')
    messageTime.innerText = data.time
    messageTime.classList.add('time', 'text-black-50', 'm-0', 'f-14')

    // 訊息資訊內框
    const innerContainer = document.createElement('div')
    innerContainer.classList.add('d-flex', 'justify-content-between', 'align-items-center', 'mb-1', 'lh-l')
    innerContainer.append(messageUser, messageTime)

    // 訊息
    const theMessage = document.createElement('p')
    theMessage.innerText = data.message
    theMessage.classList.add('letter', 'pt-2', 'm-0')

    // 訊息資訊外框
    const outerContainer = document.createElement('div')
    outerContainer.classList.add('py-3', 'w-100')
    outerContainer.append(innerContainer, theMessage)

    // 訊息欄位最外層
    const li = document.createElement('li')
    li.classList.add('list-group-item', 'd-flex')
    li.append(avatarContainer, outerContainer)

    messageList.prepend(li) 
}

// 更新朋友欄位資訊
function updatefriendList(data){
    const updateMessage = friendList.querySelector(`a[href="/message/${data.room}"]`)
    const messageTime = updateMessage.querySelector('.time')
    messageTime.innerText = data.time
    const messageContent = updateMessage.querySelector('.short-letter')
    messageContent.innerText = data.message
    friendList.prepend(updateMessage)
}


