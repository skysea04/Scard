const postID = location.pathname.split('/')[4]
//// api資訊
const postAPI = '/api/post/' + postID
const postImageAPI = '/api/new-post/image'

//// 定義文章各欄位變數
const boardOption = document.querySelector('.board-select option')
const nameOption= document.querySelector('.name-select option')
const postTitle = document.querySelector('.post-title')
const postContent = document.querySelector('.post-content')
const postAvatar = document.querySelector('.post-avatar')
//// 將看版資訊與個人名稱資訊匯入
fetch(postAPI)
.then(res => res.json())
.then(data => {
    if(data.error){ //出現錯誤，顯示提示Modal
        showErrorModal(data)
    }
    else{
        boardOption.innerText = data.boardName
        nameOption.innerText = data.userName
        postAvatar.src = data.avatar
        postTitle.value = data.title
        postContent.innerHTML = data.content
        selectImages()
    }
})


let postContentHTML = postContent.innerHTML
let allContent = postContent.childNodes
let textCursor = allContent[allContent.length - 1]

// 每次輸入內文就會儲存完整html到localhost
function inputSave(){
    selectImages()
    postContentHTML = postContent.innerHTML
    if(postContentHTML == ''){
        postContent.innerHTML = '<p><br></p>'
        textCursor = postContent.querySelector('p')
    }else{
        textCursor = window.getSelection().anchorNode
        if(textCursor.nodeName == '#text'){
            textCursor = textCursor.parentNode
        }
    }
}
// 在postContent內更改點擊位置可以改變textCursor元素
function changetextCursor(){
    tempCursor = window.getSelection().anchorNode
    if(tempCursor.nodeName == '#text' && tempCursor.parentNode.nodeName=='P'){
        textCursor = window.getSelection().anchorNode.parentElement
    }else if(tempCursor.nodeName == 'P'){
        textCursor = window.getSelection().anchorNode
    }
}
// 滿足貼上內容的情境，將文字與單一貼上的圖片留下
function pasteSave(e){
    e.preventDefault()
    const cp = e.clipboardData
    const pasteData = cp.items
    for (var i = 0; i < pasteData.length; i += 1) {
        if ((pasteData[i].kind == 'string') && 
            (pasteData[i].type.match('^text/plain'))) {
            // This item is the target node
            pasteData[i].getAsString(function (s){
                // console.log(s)
                // console.log(e.target)
                const words = s.split(/\n/)
                const len = words.length
                for(let index = 0; index < len; index++){
                    // console.log(words[index])
                    if(words[index] == '') continue
                    const page = document.createElement('p')
                    page.innerText = words[index]
                    textCursor.insertAdjacentElement('afterend', page)
                    textCursor = page
                }
            });
        } else if ((pasteData[i].kind == 'string') &&
                    (pasteData[i].type.match('^text/html'))) {
            // Drag pasteData item is HTML
            console.log("... Drop: HTML");
        } else if ((pasteData[i].kind == 'string') &&
                    (pasteData[i].type.match('^text/uri-list'))) {
            // Drag pasteData item is URI
            console.log("... Drop: URI");
        } else if ((pasteData[i].kind == 'file') &&
                    (pasteData[i].type.match('^image/'))) {
            var f = pasteData[i].getAsFile();
            // 上傳圖片返回內容
            showUpload(f)
        }
    }
}
// 每次點擊皆改動
postContent.addEventListener('click', changetextCursor)
// 每次輸入皆改動
postContent.addEventListener('input', inputSave)
// 每次paste是情況上傳照片或呈線文字
postContent.addEventListener('paste', pasteSave)

//// 上傳圖片到文章中
const imgInput = document.querySelector('#img')
const uploadImgSpinner = document.querySelector('.upload-img-spinner')
async function showUpload(inputImage){
    // 讀取圈圈轉起來
    uploadImgSpinner.classList.remove('d-none')
    
    const imgData = new FormData();
    console.log(imgData)
    imgData.append('image', inputImage) 
    console.log(imgInput)
    const res = await fetch(postImageAPI, {
        method: 'POST',
        body: imgData
    })
    const data = await res.json()
    
    // 得到結果，讀取圈圈消失
    uploadImgSpinner.classList.add('d-none')

    if(data.ok){
        const imgSelf = document.createElement('img')
        imgSelf.className = 'upload-img'
        imgSelf.src = data.src
        if(textCursor.innerHTML == '<br>'){
            textCursor.innerHTML = ''
            textCursor.append(imgSelf)
        }else{
            const imgContainer = document.createElement('p')
            imgContainer.appendChild(imgSelf)
            textCursor.insertAdjacentElement('afterend', imgContainer)
            textCursor = imgContainer
        }
        selectImages()   
    }else{
        showErrorModal(data)
    }    
}
imgInput.addEventListener('change',()=>{
    showUpload(imgInput.files[0])
})

// 點選上傳圖片時，可以選取整張圖
function selectImages(){
    let contentImgs = document.querySelectorAll('p .upload-img')
    contentImgs.forEach(contentImg => {
        function selectImg(){
            let selection = window.getSelection()
            selection.removeAllRanges()
            let theImage = this
            let range = document.createRange()
            range.selectNode(theImage)
            selection.addRange(range)
        }
        contentImg.addEventListener('click', selectImg)
    })
}
// 先執行一次
selectImages()

//// 上傳貼文
const sendPostBtn = document.querySelector('.send-post')
async function sendPost(){
    const patchData = {
        title: postTitle.value,
        content: postContent.innerHTML
    }
    const res = await fetch(postAPI, {
        method: 'PATCH',
        body: JSON.stringify(patchData),
        headers: {'Content-Type': 'application/json'}
    })
    const data = await res.json()
    if(data.error){//出現錯誤，顯示提示Modal
        showErrorModal(data)
    }else{
        location = location.pathname.slice(0, -5)
    }
}

sendPostBtn.addEventListener('click', sendPost)