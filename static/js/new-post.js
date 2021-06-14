//// errorModal相關變數
const errorModalContain = document.getElementById('error-modal')
const errorModal = new bootstrap.Modal(errorModalContain)
const modalTitle = errorModalContain.querySelector('.modal-title')
const modalBody = errorModalContain.querySelector('.modal-body')
const modalHref = errorModalContain.querySelector('.modal-href')

//// api資訊
const newPostAPI = '/api/new-post'
const postImageAPI = '/api/new-post/image'


//// 將看版資訊與個人名稱資訊匯入
const boardSelect = document.querySelector('.board-select')
const nameSelect = document.querySelector('.name-select')

fetch(newPostAPI)
    .then(res => res.json())
    .then(data => {
        if(data.error){ //出現錯誤，顯示提示Modal
            modalTitle.innText = data.title
            modalBody.innerText = data.message
            modalHref.innerText = data.confirm
            modalHref.href = data.url
            errorModal.show()
        }
        else{
            // 新增發文身份名稱選項
            const fullName = document.createElement('option')
            fullName.value = `${data.collage} ${data.department}`
            fullName.innerText = `${data.collage} ${data.department}`
            const collageName = document.createElement('option')
            collageName.value = data.collage
            collageName.innerText = data.collage
            const anonymous = document.createElement('option')
            anonymous.value = '匿名'
            anonymous.innerText = '匿名'
            nameSelect.append(fullName, collageName, anonymous)

            // 新增發文看板選項
            data.boardList.forEach(board => {
                const boardOption = document.createElement('option')
                boardOption.value = board.boardId
                boardOption.innerText = board.showName
                boardSelect.append(boardOption)
            })
        }
    })


//// 內文編輯器
const editField = document.querySelector('.post-content')
editField.innerHTML = localStorage.getItem('new-post')
let postContent = editField.innerHTML
let textCursor = editField.querySelector('div')

editField.addEventListener('input', function(){
    // console.log(editField.innerHTML)
    postContent = editField.innerHTML
    // console.log('content', postContent)
    if(postContent == ''){
        postContent = '<div><br></div>'
        localStorage.setItem('new-post', postContent);
        editField.innerHTML = localStorage.getItem('new-post')
        textCursor = editField.querySelector('div')
    }else{
        textCursor = window.getSelection().anchorNode
        if(textCursor.nodeName == '#text'){
            textCursor = window.getSelection().baseNode.parentElement
        }
    }
    // console.log('textCursor', textCursor)
    localStorage.setItem('new-post', postContent);
})

editField.addEventListener('click', function(){
    textCursor = window.getSelection().anchorNode
    // console.log('mouseup', window.getSelection())
    if(textCursor.nodeName == '#text'){
        textCursor = window.getSelection().baseNode.parentElement
    }
    else if(textCursor.classList.contains('post-form') || textCursor.nodeName == 'LABEL'){
        textCursor = editField.querySelector('div')
    }
    // console.log('textCursor', textCursor)
})

//// 上傳圖片
const imgInput = document.querySelector('#img')
async function showUpload(){
    const imgData = new FormData();
    imgData.append('image', imgInput.files[0]) 
    const res = await fetch(postImageAPI, {
        method: 'POST',
        body: imgData
    })
    const data = await res.json()
    if(data.ok){
        const imgContainer = document.createElement('div')
        const imgSelf = document.createElement('img')
        imgSelf.className = 'upload-img'
        imgSelf.src = data.src
        imgContainer.appendChild(imgSelf)
        textCursor.insertAdjacentElement('afterend', imgContainer)
        textCursor = imgContainer

        postContent = editField.innerHTML
        localStorage.setItem('new-post', postContent);
    }else{
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }    
}

imgInput.addEventListener('change', showUpload)

