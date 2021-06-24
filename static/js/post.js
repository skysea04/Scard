//網址ID
const postID = location.pathname.split('/').pop()
// api
const postAPI = `/api/post/${postID}`
const commentAPI = `/api/comment/${postID}`
const newPostAPI = '/api/new-post'
const postImageAPI = '/api/new-post/image'

modalHref.addEventListener('click',()=> errorModal.hide())

//// 匯入文章至頁面
const thePost = document.querySelector('.the-post')
const postAvatar = thePost.querySelector('.author-field img')
const userName = thePost.querySelector('.author-field .user-name')
const postTitle = thePost.querySelector('.post-title')
const postBoard = thePost.querySelector('.post-board')
const postCreateTime = thePost.querySelector('.create-time')
const postContent = thePost.querySelector('.post-content')
const postLikeCount = thePost.querySelector('.like-count')
const postCommentCounts = document.querySelectorAll('.comment-count')

const comments = document.querySelector('.comments')

// 獲得文章內容
fetch(postAPI)
    .then(res => res.json())
    .then(data => {
        postAvatar.src = data.avatar
        userName.innerText = data.userName
        postTitle.innerText = data.title
        postBoard.href = data.boardSrc
        postBoard.innerText = data.boardName
        postCreateTime.innerText = data.createTime
        postContent.innerHTML = data.content
        postLikeCount.innerText = data.likeCount
        postCommentCounts.forEach( count =>{
            count.innerText = data.commentCount
        })
        // if(data.commentCount == 0){
        //     comments.classList.add('d-none')
        //     thePost.classList.add('no-comment')
        // }
    })

//// 匯入留言至頁面



//// 使用者留言編輯區
const commentBlank = document.querySelector('.comment-blank')
const postComment = document.querySelector('.post-comment') // 整個留言區塊
const cancelComment = postComment.querySelector('.cancel')
const postCommentContent = postComment.querySelector('.post-comment-content') //留言內容區塊
const postCommentAvatar = postComment.querySelector('.post-comment-avatar')
const nameSelect = postComment.querySelector('.name-select')
const sendBtn = postComment.querySelector('.send-comment')
const expandBtn = postComment.querySelector('#expand-btn')
const contractBtn = postComment.querySelector('#contract-btn')

// 將個人名稱資訊匯入留言區
fetch(newPostAPI)
    .then(res => res.json())
    .then(data => {
        if(data.error){ 
            //點擊時出現錯誤，顯示提示Modal
            commentBlank.addEventListener('click',()=>{
                modalTitle.innText = data.title
                modalBody.innerText = data.message
                modalHref.innerText = data.confirm
                modalHref.href = data.url
                errorModal.show()
            })
        }
        else{
            // 新增發文身份名稱選項
            const fullName = document.createElement('option')
            fullName.value = 'full'
            fullName.innerText = `${data.collage} ${data.department}`
            const collageName = document.createElement('option')
            collageName.value = 'collage'
            collageName.innerText = data.collage
            const anonymous = document.createElement('option')
            anonymous.value = '匿名'
            anonymous.innerText = '匿名'
            nameSelect.append(fullName, collageName, anonymous)

            // 新增發文頭像
            postCommentAvatar.src = data.avatar

            commentBlank.addEventListener('click', commentToggle)
            cancelComment.addEventListener('click', commentToggle)
        }
    })

// 顯現、關閉留言面板
function commentToggle(){
    commentBlank.classList.toggle('d-none')
    postComment.classList.toggle('d-none')
}

// 擴展、縮小留言面板區域
function commentExpandToggle(){
    postComment.classList.toggle('expand')
    expandBtn.classList.toggle('d-none')
    contractBtn.classList.toggle('d-none')
}
expandBtn.addEventListener('click', commentExpandToggle)
contractBtn.addEventListener('click', commentExpandToggle)


let postCommentContentHTML = postCommentContent.innerHTML
let allContent = postCommentContent.childNodes
let textCursor = allContent[allContent.length - 2]

// 每次輸入內文就會儲存完整html
function inputSave(){
    selectImages()
    postCommentContentHTML = postCommentContent.innerHTML
    if(postCommentContentHTML == ''){
        postCommentContent.innerHTML = '<p><br></p>'
        textCursor = postCommentContent.querySelector('p')
    }else{
        textCursor = window.getSelection().anchorNode
        if(textCursor.nodeName == '#text'){
            textCursor = textCursor.parentNode
        }
    }
}
// 在postCommentContent內更改點擊位置可以改變textCursor元素
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
                // textCursor = e.target.parentNode
                const words = s.split(/\n|\r/)
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
            console.log(e.target)
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
postCommentContent.addEventListener('click', changetextCursor)
// 每次輸入皆改動
postCommentContent.addEventListener('input', inputSave)
// 每次paste是情況上傳照片或呈線文字
postCommentContent.addEventListener('paste', pasteSave)

// 上傳圖片到回覆內容中
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
        
        // 儲存到localStorage
        selectImages()   
    }else{
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
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

// 發送留言
async function sendComment(){
    const commentData = {
        name: nameSelect.value,
        content: postCommentContent.innerHTML
    }
    const res = await fetch(commentAPI, {
        method: 'POST',
        body: JSON.stringify(commentData),
        headers: {'Content-Type': 'application/json'}
    })
    const data = await res.json()
    if(data.error){
        modalTitle.innText = data.title
        modalBody.innerText = data.message
        modalHref.innerText = data.confirm
        modalHref.href = data.url
        errorModal.show()
    }
    else{
        postCommentContent.innerHTML = ''
        commentToggle()
        // 加入留言到頁面
        // 更改留言數量
    }

}
sendBtn.addEventListener('click', sendComment)