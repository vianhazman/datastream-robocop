import datetime
import re
import threading
import docker
import requests
import yaml
import glob

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def listen_log(job_name, container_id, keyword, bot_token, bot_chatID):
    client = docker.from_env()
    container = client.containers.get(container_id)
    now = datetime.datetime.utcnow()
    for line in container.logs(stream=True, timestamps=True, since= now):
        if re.compile('|'.join(keyword), re.IGNORECASE).search(str(line.strip())):
            msg = "[ROBOCOP v2] Job: " + job_name + " \n\n Keyword " + str(
                                      keyword) + " found, attempting restart.\n\n Log details: " + str(line.strip())
            telegram_bot_sendtext(bot_token, bot_chatID,
                                  msg)
            root.info(msg)
            try:
                root.info(job_name+" attempting restart")
                container.restart()
            except Exception as e:
                root.error(e)
            success_msg = "[ROBOCOP v2] Job: " + job_name + " restart successful "
            root.info(success_msg)
            telegram_bot_sendtext(bot_token, bot_chatID,
                                  success_msg)



def telegram_bot_sendtext(bot_token, bot_chatID, bot_message):
    send_text = 'https://api.telegram.org/bot' + str(bot_token) + '/sendMessage?chat_id=' + str(
        bot_chatID) + '&parse_mode=Markdown&text=' + str(bot_message)

    response = requests.get(send_text)

    return response.json()


def read_yaml_file(filename):
    with open(filename, 'r') as stream:
        try:
            root.info(filename)
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            root.error(exc)


job = []
threads = []
configs = glob.glob("configs/*.yaml")

for file in configs:
    job.append(read_yaml_file(file))

for i in job:
    t = threading.Thread(target=listen_log, args=(
        i["name"], i["container"], i["keyword"], i["notification"]['chatToken'], i["notification"]['chatID']))
    t.start()
    threads.append(t)
