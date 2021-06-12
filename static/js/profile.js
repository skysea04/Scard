const toVerifyModal = new bootstrap.Modal(document.getElementById('to-verify-modal'))
const finshModal = new bootstrap.Modal(document.getElementById('finish-update'))

//// 編輯頭像功能
const avatarInput = document.querySelector('#avatar')
const tempAvatar = document.querySelector('#temp-avatar')
const avatarConfirm = new bootstrap.Modal(document.getElementById('avatar-confirm'))
const avatarConfirmModel = document.querySelector("#avatar-confirm")
const saveAvatarBtn = avatarConfirmModel.querySelector('.save-avatar')
const closeBtn = avatarConfirmModel.querySelector('.btn-close')
const avatarAlertMessage = avatarConfirmModel.querySelector('p.message')


// 顯示預覽的圖像樣貌
function showUpload(){
    const [file] = avatarInput.files
    if(file){
        tempAvatar.src = URL.createObjectURL(file)
        avatarConfirm.show()
    }
}

// 送出頭像並儲存
async function saveAvatar(){
    const avatarData = new FormData();
    avatarData.append('avatar', avatarInput.files[0])
    const res = await fetch('/api/profile/avatar', {
        method: 'PATCH',
        body: avatarData
    })
    const data = await res.json()
    if(data.ok){
        closeBtn.click()
        avatar.src = data.src
    }else{
        avatarAlertMessage.innerText = data.message
    }
}

avatarInput.addEventListener('change', showUpload)
saveAvatarBtn.addEventListener('click', saveAvatar)



//// 查看、編輯個人資訊
const profileForm = document.querySelector('form.profile')
const avatar = document.querySelector('.avatar-container img')
const name = document.querySelector('input[name="name"]')
const collage = document.querySelector('input[name="collage"]')
const department = document.querySelector('input[name="department"]')
const relationship = document.querySelector('select[name="relationship"]')
const interest = document.querySelector('textarea[name="interest"]')
const club = document.querySelector('textarea[name="club"]')
const course = document.querySelector('textarea[name="course"]')
const country = document.querySelector('textarea[name="country"]')
const worry = document.querySelector('textarea[name="worry"]')
const swap = document.querySelector('textarea[name="swap"]')
const wantToTry = document.querySelector('textarea[name="want_to_try"]')
const alertMessage = document.querySelector('form.profile>p.message')


// 檢查是否通過驗證
async function verify(){
    const res = await fetch(verifyAPI)
    const data = await res.json()
    if(data.ok){
        getProfile()
    }else{
        toVerifyModal.show()
    }
}

// 查看人個資訊
async function getProfile(){
    const res = await fetch(profileAPI)
    const data = await res.json()
    if(data.error){
        console.log(data.message)
    }else{
        // 改變select option的函式
        function select(selectId, optionValToSelect){
            //Get the select element by it's unique ID.
            var selectElement = document.getElementById(selectId);
            //Get the options.
            var selectOptions = selectElement.options;
            //Loop through these options using a for loop.
            for (var opt, j = 0; opt = selectOptions[j]; j++) {
                //If the option of value is equal to the option we want to select.
                if (opt.value == optionValToSelect) {
                    //Select the option and break out of the for loop.
                    selectElement.selectedIndex = j;
                    break;
                }
            }
        }
        avatar.src = data.avatar
        name.value = data.name
        collage.value = data.collage
        department.value = data.department
        select('relationship', data.relationship)
        interest.value = data.interest
        club.value = data.club
        course.value = data.course
        country.value = data.country
        worry.value = data.worry
        swap.value = data.swap
        wantToTry.value = data.want_to_try
    }
}

// 更新自我介紹
async function updateProfile(e){
    e.preventDefault()

    const profileData = {
        collage: collage.value,
        department: department.value,
        relationship: relationship.value,
        interest: interest.value,
        club: club.value,
        course: course.value,
        country: country.value,
        worry: worry.value,
        swap: swap.value,
        want_to_try: wantToTry.value
    }

    const res = await fetch(profileAPI, {
        method: 'PATCH',
        body: JSON.stringify(profileData),
        headers: {'Content-Type': 'application/json'}
    })
    const data = await res.json()
    if(data.ok){
        alertMessage.innerText = ''
        finshModal.show()
    }else{
        alertMessage.innerText = data.message
    }
}

profileForm.addEventListener('submit', updateProfile)