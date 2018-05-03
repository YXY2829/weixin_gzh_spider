import requests
import json
from urllib.parse import quote
from pprint import pprint

url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&token=1478878797&lang=zh_CN' \
      '&f=json&ajax=1&random=0.18320165449846337&query={}&begin=0&count=5'

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	'Cookie': 'tvfe_boss_uuid=7643641b94938155; _qpsvr_localtk=0.037841212154183346; '
	'RK=lYvDWWLbea;'
	'pgv_pvid=8407970835; o_cookie=364585454; ptisp=cnc; '
	'ptcz=a46f914fac24790fe3289d6048820cc33852016f4628bdd510bfd98e4a858d24; '
	'wxtokenkey=777; FTN5K=d59e185b; pt2gguin=o0364585454; uin=o0364585454; '
	'OUTFOX_SEARCH_USER_ID_NCOO=1865991911.1785605; skey=@X9agDQb3e; '
	'ua_id=NQSZvMPrUsQGYbJcAAAAAK3iV6nHgMyWm7j1tS3eYzY=; mm_lang=zh_CN; '
	'uuid=0f6da54430eee39e175815c1e1dd2a68; ticket=97b3d3444c221a42848e3677696ddbeab93c2c62; '
	'ticket_id=gh_ca33a0b13059; cert=PKP89M8WQHkLeceIW1GDwxTGTOAKnmS1; noticeLoginFlag=1; '
	'data_bizuin=3071856695; bizuin=3000536892; '
	'data_ticket=5x0psWcOeIlBW1AjhN6YQBt67mE9/KwgxzXG8AuEYZyYbxNBne8deWmeMXiIJXrI; '
	'slave_sid=VF91MEpENGhSbm40NEQ3WlRIMFJ2V2RtQnhXaUd6X1c0RTkzY2Vrdlc5N0JhNTNsRkxNSHdy'
	'dzVRZlR1cnowbENwZXhtNllxa0N3Zk1iRzhEQXJJWkNBeHh4dkFmelppUkY3VnBwUDlOQnBvYkVNUlB4Zz'
	'ZJYnlxZ1FBdHd6UmRJWUEyM2VuYjJCQ2tab2po; slave_user=gh_ca33a0b13059',
	'Host': 'mp.weixin.qq.com',
	'Referer': 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=1478878797&lang=zh_CN',
}

s = requests.Session()
r = s.get(url.format('进击的Coder'), headers=headers)
s.headers.update(headers)

"""
{'base_resp': {'err_msg': 'ok', 'ret': 0},
 'list': [{'alias': 'FightingCoder',
           'fakeid': 'MzIzNzA4NDk3Nw==',
           'nickname': '进击的Coder',
           'round_head_img': 'http://mmbiz.qpic.cn/mmbiz_png/yjdDibu0qm7EUhr6JbKJibia3ZDUYeeMu1soalaib2Zf2rz0Glq3I3vSVwEFAicpu06qRVVcyibmxB9HR27ZtN7oe50A/0?wx_fmt=png',
           'service_type': 1},
          {'alias': 'AllenLee_World',
           'fakeid': 'MzIxNzE4MTczNQ==',
           'nickname': '进击的菜鸟Coder',
           'round_head_img': 'http://mmbiz.qpic.cn/mmbiz_png/IMVrEia3c8DBGXcKJ0QwY3RPv8Tp41ge57Fn4BfXqlZIgYXgTrC83iavic5Mx5CmGjdTgyfkwsSzUPZ1sB0boofOg/0?wx_fmt=png',
           'service_type': 1}],
 'total': 2}
"""

j = r.json()

c_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?token=1478878797&lang=zh_CN&f=json' \
        '&ajax=1&random=0.5601484271148798&action=list_ex&begin=0&count=5&query=&fakeid={}&type=9'

is_ok = j.get('base_resp', {}).get('err_msg', '')
if is_ok == 'ok':
	gzh_list = j.get('list')
	for l in gzh_list:
		alias = l.get('alias')
		fakeid = l.get('fakeid')
		nickname = l.get('nickname')
		if alias == '进击的Coder' or nickname == '进击的Coder':
			article_url = c_url.format(quote(fakeid))
			rr = s.get(article_url)
			pprint(rr.json())

