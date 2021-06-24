// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')

// api
const userAPI = '/api/user'
const profileAPI = '/api/profile'

// 根據是否登入顯示不同的nav內容
const navUser = document.querySelector('.nav-user')
const navStranger = document.querySelector('.nav-stranger')

async function checkSign(){
    const res =await fetch(userAPI)
    const data = await res.json()
    if(data.id){
        navUser.classList.add('d-flex')
        navStranger.classList.add('d-none')
    }
    else{
        navUser.classList.remove('d-flex')
        navStranger.classList.add('d-flex')
        navStranger.classList.remove('d-none')
        try{
            const toSignupModal = new bootstrap.Modal(document.getElementById('to-signup-modal'))
            toSignupModal.show()
        }catch{}
    }
}
// 啟動一次
checkSign()

// 登出機制
const signoutBtn = document.querySelector('.signout')

async function signout(){
    await fetch(userAPI, {method: 'DELETE'})
    const userURL = location.pathname.split('/')[1]
    const toSignUpList = ['new-post', 'scard', 'message', 'my']
    if(toSignUpList.includes(userURL)){
        location = '/signup'
    }else{
        location.reload()
    }
    checkSign()
}

signoutBtn.addEventListener('click', signout)


// 確認使用者的權限是否可以進入某個頁面
const links = navUser.querySelectorAll('a')

async function verifyUser(e){
    e.preventDefault()
    // console.log(this.id)
    const verifyAPI = `/api/verify?a=${this.id}`
    const res = await fetch(verifyAPI)
    const data = await res.json()
    if(data.ok){
        location.assign(data.url)
    }else{
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }

}

links.forEach(link => {
    link.addEventListener('click', verifyUser)
})