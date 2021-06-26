select user_1, user_2, create_time, message
    from messages, scard, user
    where messages.scard_id = scard.id and messages.user_id = user.id
        and  (scard.user_1=2 or scard.user_2=2)
    group by messages.scard_id;
    order by create_time desc limit 1

select friend.scard_id, friend.message, friend.create_time, friend.user_1, friend.user_2 
from 
(select * from messages order by create_time desc limit 9999) friend , scard
where friend.scard_id = scard.id and  (scard.user_1=586 or scard.user_2=586)
group by scard_id;





INSERT INTO postboard (sys_name, show_name, icon) 
VALUES 
    ('relationship', '感情', 'https://d2lzngk4bddvz9.cloudfront.net/board/relationship.svg'), 
    ('trending', '時事', 'https://d2lzngk4bddvz9.cloudfront.net/board/trending.svg'), 
    ('talk', '閒聊', 'https://d2lzngk4bddvz9.cloudfront.net/board/talk.svg'),
    ('mood', '心情', 'https://d2lzngk4bddvz9.cloudfront.net/board/mood.svg'),
    ('job', '工作', 'https://d2lzngk4bddvz9.cloudfront.net/board/job.svg'),
    ('youtuber', 'Youtuber', 'https://d2lzngk4bddvz9.cloudfront.net/board/youtuber.svg'),
    ('acg', '動漫', 'https://d2lzngk4bddvz9.cloudfront.net/board/acg.svg'),
    ('tvepisode', '戲劇綜藝', 'https://d2lzngk4bddvz9.cloudfront.net/board/tvepisode.svg'),
    ('music', '音樂', 'https://d2lzngk4bddvz9.cloudfront.net/board/music.svg'),
    ('COVID-19', 'COVID-19', 'https://d2lzngk4bddvz9.cloudfront.net/board/COVID-19.svg');
