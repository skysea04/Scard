const hotNav = document.querySelector('.hot-nav')
const latestNav = document.querySelector('.latest-nav')

const search = location.search
if(search == '?latest=true'){
    hotNav.classList.remove('active')
    latestNav.classList.add('active')
}