// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')

// scard頁面相關變數
const addFriendBtn = document.querySelector('.add-friend-btn')
const scardPage = document.querySelector('.scard-card')
const avatar = scardPage.querySelector('.avatar-container img')
const name = scardPage.querySelector('.name')
const collage = scardPage.querySelector('.collage')
const department = scardPage.querySelector('.department')
const interest = scardPage.querySelector('.interest')
const club = scardPage.querySelector('.club')
const course = scardPage.querySelector('.course')
const country = scardPage.querySelector('.country')
const worry = scardPage.querySelector('.worry')
const swap = scardPage.querySelector('.swap')
const wantToTry = scardPage.querySelector('.want-to-try')


fetch(scardAPI)
    .then(res => res.json())
    .then(data => {
        if(data.error){
            modalTitle.innText = data.title
            modalBody.innerText = data.message
            modalHref.innerText = data.confirm
            modalHref.href = data.url
            errorModal.show()
        }else{
            if(data.isFriend){
                addFriendBtn.innerText = '已成為卡有'
                // 這裡還要幫他加入對方聊天的連結，之後補
            }else if(data.invited){
                addFriendBtn.innerText = '已送出邀請'
                addFriendBtn.classList.add('btn-secondary')
                addFriendBtn.setAttribute("disabled", "")
            }

            avatar.src = data.avatar
            name.innerText = data.name
            collage.innerText = data.collage
            department.innerText = data.department
            interest.innerText = data.interest
            club.innerText = data.club
            course.innerText = data.course
            country.innerText = data.country
            worry.innerText = data.worry
            swap.innerText = data.swap
            wantToTry.innerText = data.wantToTry          
        }
    })

// 
const addModalContain = document.getElementById('add-friend-modal')
const addModal = new bootstrap.Modal(addModalContain)
const addFriendForm = addModalContain.querySelector('form')
const message = addFriendForm.querySelector('textarea')

addFriendBtn.addEventListener('click', () => {
    addModal.show()
})

async function addFriend(e){
    e.preventDefault()
    const messageData = {
        message: message.value
    }
    const res = await fetch(scardAPI, {
        method: 'POST',
        body: JSON.stringify(messageData),
        headers: {'content-type': 'application/json'}
    })
    const data = await res.json()
    if(data.ok){
        if(data.isFriend){
            addFriendBtn.innerText = '已成為卡友'
            // 這裡還要幫他加入對方聊天的連結，之後補
        }else{
            addFriendBtn.innerText = '已送出邀請'
            addFriendBtn.classList.add('btn-secondary')
            addFriendBtn.setAttribute("disabled", "")
        }
    }else{
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }
    
}

addFriendForm.addEventListener('submit', addFriend)