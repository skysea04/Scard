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


