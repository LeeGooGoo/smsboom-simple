import json
from datetime import datetime
import threading

import requests
import urllib3
from jinja2 import FileSystemLoader, Environment
from loguru import logger


def render_template(phone: int | str):
	env = Environment(loader=FileSystemLoader("../Mysmsboom"))
	temp = env.get_template("api.json").render(phone=str(phone), timestamp=str(int(datetime.now().timestamp())))
	text: list = json.loads(temp)
	return text


def send_request(args: dict, lk):
	with lk:
		url, headers, data = args["url"], args["header"], args["data"]
		try:
			if isinstance(args["data"], dict):
				res = requests.post(url=url, json=data, headers=headers, timeout=10)
			else:
				res = requests.post(url=url, data=data, headers=headers, timeout=10)
			try:
				desc = json.dumps(res.json(), ensure_ascii=False).replace("\n", " ")[:30]
			except Exception:
				res.encoding = "utf-8"
				desc = res.text.replace("\n", " ")[:30]
			logger.info(f"{args['desc']}-{desc}")
		except Exception as fp:
			logger.error(f"{args['desc']}-{str(fp)[:30]}")


# def update():
# 	api_url = r"https://hk1.monika.love/AdminWhaleFall/SMSBoom/master/api.json"
# 	headers = {
# 		"User-Agent": "Mozilla/5.0 (Linux; U; Android 10; zh-cn; Mi 10 Build/QKQ1.191117.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.147 Mobile Safari/537.36 XiaoMi/MiuiBrowser/13.5.40"
# 	}
# 	try:
# 		logger.info(f"正在拉取最新接口!")
# 		urllib3.disable_warnings()
# 		res = requests.get(url=api_url, headers=headers, verify=False, timeout=10)
# 	except Exception as why:
# 		logger.error(f"拉取更新失败:{why}请关闭所有代理软件多尝试几次!")
# 	else:
# 		with open("api.json", mode="w", encoding="utf-8") as fp:
# 			json.dump(res.json(), fp, ensure_ascii=False, indent=4)
# 			logger.success(f"接口更新成功!")


def main(phone: int | str, frequency: int | str = 1):
	lock = threading.Lock()
# 	update()
	seq = render_template(phone)
	for _ in range(int(frequency)):
		for i in seq:
			threading.Thread(target=send_request, args=(i, lock)).start()


if __name__ == '__main__':
	p = input("请输入手机号:")
	f = input("请输入循环次数:")
	main(p, f)
