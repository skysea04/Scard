const PostsAPIBase = '/api/posts'

let page = 0

//決定要搜尋的看板
const board = location.pathname.split('/').pop()
// console.log(board)
let boardSearch = ''
if(board == 'b'){
    boardSearch = 'board=all'
}else{
    boardSearch = `board=${board}`
}

//決定要搜尋的方式
const hotNav = document.querySelector('.hot-nav')
const latestNav = document.querySelector('.latest-nav')
const isPopular = location.search
let popularSearch = ''

if(isPopular == '?popular=true'){
    popularSearch = 'popular=true'
    latestNav.classList.remove('active')
    hotNav.classList.add('active')
}else{
    popularSearch = 'popular=false'
}

let postsAPI = `${PostsAPIBase}?${boardSearch}&${popularSearch}&page=${page}`
const postsField = document.querySelector('.posts')

async function getPosts(){
    const res = await fetch(postsAPI)
    const data = await res.json()
    
    // 更動頁數
    page = data.nextPage
    // console.log(data.data)
    // 將文章資訊寫入網頁
    data.data.forEach(post => {
        // authorField
        const avatar = document.createElement('img')
        avatar.src = post.avatar
        avatar.className = 'me-2 rounded-circle avatar'

        const board = document.createElement('p')
        board.className = 'board-name'
        board.innerText = `${post.board}・`

        const userName = document.createElement('p')
        userName.className = 'user-name'
        userName.innerText = post.userName

        const authorField = document.createElement('div')
        authorField.className = 'd-flex text-black-50 fs-6 mb-2 author-field'
        authorField.append(avatar, board, userName)

        // infoField in MainField
        const likeIcon = document.createElement('img')
        likeIcon.className = 'me-2'
        likeIcon.src = '/static/icons/like.svg'

        const likeCount = document.createElement('p')
        likeCount.className = 'me-2'
        likeCount.innerText = post.likeCount

        const commentIcon = document.createElement('img')
        commentIcon.className = 'me-2'
        commentIcon.src = '/static/icons/comment.svg'

        const commentCount = document.createElement('p')
        commentCount.className = 'me-2'
        commentCount.innerText = post.commentCount

        const infoField = document.createElement('div')
        infoField.className = 'post-info d-flex text-black-50'
        infoField.append(likeIcon, likeCount, commentIcon, commentCount)

        // postField in MainField
        const title = document.createElement('h4')
        title.className = 'fs-5 mb-1 fw-normal post-title'
        title.innerText = post.title
        
        const content = document.createElement('p')
        content.className = 'mb-3 post-content'
        const postContent =  post.content.replace(/<[^>]+>/g, ' ');
        // console.log(postContent)
        content.append(postContent)
        // console.log(htmlToElem(post.content))

        const postField = document.createElement('div')
        postField.className = 'flex-fill post-container'
        postField.append(title, content, infoField)
        
        // MainField
        const mainField = document.createElement('div')
        mainField.className = 'd-flex'
        mainField.append(postField)

        // first Img in MainField
        if(post.img != null){
            const img = document.createElement('img')
            img.className = 'rounded border post-img'
            img.src = post.img
            
            const imgContainer = document.createElement('div')
            imgContainer.className = 'ms-2'
            imgContainer.append(img)

            mainField.append(imgContainer)
        }

        // postField
        const aHref = document.createElement('a')
        aHref.className = 'pe-2 w-100 border-bottom post'
        aHref.href = post.url

        aHref.append(authorField, mainField)
        postsField.append(aHref)
    })
}

getPosts()