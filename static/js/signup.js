// 登入/註冊流程
const signupForm = document.querySelector('form.signup')

async function signup(e){
    e.preventDefault()
    const signupData = {
        email : this.querySelector('input[name="email"]').value,
        password : this.querySelector('input[name="password"]').value,
        fromAPI: false
    }
    const res = await fetch(userAPI, {
                    method: 'POST',
                    body: JSON.stringify(signupData),
                    headers: {'Content-Type': 'application/json'}
                })
    const data =await res.json()
    if(data.ok){
        window.location.replace('/')
    }else{
        const message = this.querySelector('.message')
        message.innerText = data.message
    }
}

signupForm.addEventListener('submit', signup)