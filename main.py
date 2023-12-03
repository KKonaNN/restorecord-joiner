import os
import time
import json
import threading
import requests
from colorama import Fore, init

class UI:
    """User Interface class for updating the console display"""
    def __init__(self):
        self.start = time.time()
        self.hits = 0
        self.bad = 0
        self.cpm = 0
        self.clear_console()
        self.print_logo()
        threading.Thread(target=self.update_title).start()
        threading.Thread(target=self.calculate_cpm).start()

    def clear_console(self):
        os.system('cls')

    def print_logo(self):
        print('''
     __       .__                     
    |__| ____ |__| ____   ___________ 
    |  |/  _ \|  |/    \_/ __ \_  __ \\
    |  (  <_> )  |   |  \  ___/|  | \/
/\__|  |\____/|__|___|  /\___  >__|   
\______|              \/     \/                   
''')

    def update_title(self):
        while True:
            elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start))
            os.system(f"title [DISCORD JOINER] Hits: {self.hits} ^| Bad: {self.bad} ^| CPM: {self.cpm} ^| Threads: {threading.active_count() - 3} ^| Time elapsed: {elapsed}")
            time.sleep(1)

    def calculate_cpm(self):
        while True:
            old_hits = self.hits
            time.sleep(4)
            self.cpm = (self.hits - old_hits) * 15


class Discord:
    """Discord class for handling Discord operations"""
    def __init__(self, token, guild):
        self.token = token
        self.guild = guild
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bot {token}',
            'Content-Type': 'application/json',
        })

    def join(self, user):
        userid = user.get('id')
        access_token = user.get('at')
        if not userid or not access_token:
            print(f'[{time.strftime("%H:%M:%S")}] {Fore.RED} {userid} Invalid user ! {Fore.RESET}')
            ui.bad += 1
            return
        response = self.session.put(f'https://discordapp.com/api/guilds/{self.guild}/members/{userid}', json={'access_token': access_token})
        self.handle_response(response, userid)

    def handle_response(self, response, userid):
        if response.status_code == 201:
            print(f'[{time.strftime("%H:%M:%S")}] {Fore.GREEN} {userid} Joined guild ! {Fore.RESET}')
            ui.hits += 1
        elif response.status_code == 204:
            print(f'[{time.strftime("%H:%M:%S")}] {Fore.BLUE} {userid} Already in guild ! {Fore.RESET}')
        elif response.status_code == 429:
            print(f'[{time.strftime("%H:%M:%S")}] {Fore.YELLOW} {userid} Ratelimited ! {Fore.RESET}')
            time.sleep(int(response.headers['Retry-After']))
            self.join(user)
        elif response.status_code == 403:
            print(f'[{time.strftime("%H:%M:%S")}] {Fore.RED} {userid} Invalid token ! {Fore.RESET}')
            ui.bad += 1
            os._exit(0)
        else:
            print(f'[{time.strftime("%H:%M:%S")}] {Fore.RED} {userid} Failed to join guild ! {Fore.RESET}')
            ui.bad += 1
        time.sleep(5)


if __name__ == '__main__':
    ui = UI()
    users_path = input('Enter the path to the users.json file: ')
    with open(users_path, 'r') as f:
        users = json.load(f)
    token = input('Enter your discord token: ')
    guild = input('Enter the guild id: ')
    discord = Discord(token, guild)
    for user in users:
        user_dict = {'id': user['discord_Id'], 'at': user['Access_token']}
        discord.join(user_dict)