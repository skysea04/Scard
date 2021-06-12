// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')


//// 切換訊息與卡友資訊分頁
const messageNav = document.querySelector('#nav-message')
const friendInfoNav = document.querySelector('#nav-friend-info')
const messagePage = document.querySelector('.messages')
const friendInfoPage = document.querySelector('.friend-info')

function showMessage(e){
    e.preventDefault()
    messageNav.classList.add('active')
    friendInfoNav.classList.remove('active')
    messagePage.classList.add('d-block')
    friendInfoPage.classList.remove('d-block')
}
function showFriendInfo(e){
    e.preventDefault()
    messageNav.classList.remove('active')
    friendInfoNav.classList.add('active')
    messagePage.classList.remove('d-block')
    friendInfoPage.classList.add('d-block')
}

messageNav.addEventListener('click', showMessage)
friendInfoNav.addEventListener('click', showFriendInfo)


//// 獲取好友列表
const friendlistAPI = '/api/friendlist'
const friendList = document.querySelector('.friends .list-group')
async function getFriend(){
    // 清空後重新render
    const res = await fetch(friendlistAPI)
    const data = await res.json()
    // 列出朋友
    if(data.data){ // 正常render資料
        friendList.innerHTML = ''
        data.data.forEach(friend => {
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
            outerContainer.classList.add('w-240', 'p-2')

            outerContainer.append(innerContainer, lastestMessage)
            
            // 朋友頭像
            const avatar = document.createElement('img')
            avatar.src = friend.avatar
            avatar.classList.add('rounded')

            // 朋友欄位連結(最大框)
            const a = document.createElement('a')
            a.href = `/message/${friend.messageRoomId}`
            a.classList.add('friend', 'p-3', 'd-flex', 'w-100')

            a.append(avatar, outerContainer)
            friendList.append(a)
        })
        const friendInThisMessage = document.querySelector(`a[href=\'${location.pathname}\']`)
        friendInThisMessage.classList.add('active')
    }else{ //出現錯誤，顯示提示Modal
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }
}

getFriend()


//// 獲取聊天訊息
const messageRoomId = location.pathname.split('/').pop()
const messageAPI = `/api/message/${messageRoomId}`
const messageList = document.querySelector('.messages ul')
const userAvatar = document.querySelector('.send-message .message-avatar img')
// 定義使用者id, 姓名, 頭像 變數
let usrId, usrName, usrAvatar

async function getMessages(){
    const res = await fetch(messageAPI)
    const data = await res.json()
    if(data.data){ //正常render資料
        const user = data.user
        const friend = data.friend
        usrId = user.id
        usrName = user.name 
        usrAvatar= user.avatar
        
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
            messageList.append(li)
        })
    }else{ //出現錯誤，顯示提示Modal
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }
}

getMessages()


//// 傳送訊息
const socket = io()
socket.on('connect', function(){
    socket.emit('join_room', messageRoomId)

    const message = document.querySelector('#send-message')
    const sendBtn = document.querySelector('#send-btn')

    function sendMessage(){
        const alertMessage = document.querySelector('#alert-message')
        if(message.value == ''){ // 如果沒有輸入內容顯示提醒文字，並不送出訊息
            alertMessage.innerText = '尚未輸入內容！'
        }else{ // 若有內容送出訊息
            alertMessage.innerText = ''
            socket.emit('send_message', {
                id: usrId,
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

    getFriend()
})


