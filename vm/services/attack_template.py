#!/usr/bin/env python3


#Usefull libs for python using 'pip install requests pwntools'

#CHANGE ME!!!!
class config:
    service = "Notes" # "PCSS" "Pwnzer0tt1Shop-Article" "Pwnzer0tt1Shop-User"
    team_token = "my_team_token"
    my_team_ip = "10.60.my_team_id.1" 


#Write your attack here

def attack(team_ip: str, flag_id):
    #Run me!
    return "Text with some flags ... :)"

# --- Attacker stuff (you are free to change this, but is not necessary) ---

import multiprocessing, re, traceback, requests, time, queue

class g:
    tick_time = None
    flag_regex = None
    flag_queue = multiprocessing.Queue()

def submit_flags_loop(flg_queue: queue.Queue):
    flags_submitted = set()
    try:
        while True:
            flags = []
            while True:
                try:
                    flg = flg_queue.get(block=False)
                    if flg not in flags_submitted:
                        flags.append(flg)
                except queue.Empty as e:
                    break
            if len(flags) > 0:
                try:
                    resp = requests.put('http://10.10.0.1:8080/flags', headers={
                        'X-Team-Token': config.team_token
                    }, json=flags)
                    if resp.status_code != 200:
                        print(f"Error while submitting flags: [200 != {resp.status_code}]{resp.text}")
                        for ele in flags:
                            flg_queue.put(ele)
                    else:
                        for ele in flags:
                            flags_submitted.add(ele)
                        print(f"Submitted {len(flags)} flags")
                except Exception as e:
                    print(f"Error while submitting flags: {e}")
                    for ele in flags:
                        flg_queue.put(ele)
            time.sleep(3)
    except KeyboardInterrupt:
        exit(0)

def attack_wrapper(team_ip: str, flag_id, flag_reg, flg_queue: queue.Queue):
    try:
        result = attack(team_ip, flag_id)
        result = str(result)
        for ele in re.findall(flag_reg, result):
            print(f"Found flag {ele}")
            flg_queue.put(ele)
    except Exception as e:
        print(f"Error while attacking {team_ip} with flag_id {flag_id}: {e}")
        traceback.print_exc()

def attack_list_flag_ids(team_ip: str, flag_ids: list):
    for flag_id in flag_ids:
        p = multiprocessing.Process(target=attack_wrapper, args=(team_ip, flag_id, g.flag_regex, g.flag_queue))
        p.start()
        p.join(timeout=g.tick_time)
        if p.is_alive():
            print(f"Attack on {team_ip} with flag_id {flag_id} is taking too long, killing it")
        p.terminate()
        p.kill()
        p.join()

def run_once():
    configs = requests.get("http://10.10.0.1/api/config").json()
    services = configs["services"]
    config.service = config.service.strip()
    if not config.service in services:
        print(f"Service {config.service} is not available, choose one of {services}")
        return
    g.flag_regex = configs["flag_regex"]
    flag_ids = requests.get("http://10.10.0.1:8081/flagIds").json()
    res = attack("10.60.0.1", flag_ids[config.service]["10.60.0.1"][-1])
    print("GOT FLAGS:", re.findall(g.flag_regex, res))

def main():
    configs = requests.get("http://10.10.0.1/api/config").json()
    services = configs["services"]
    config.service = config.service.strip()
    config.my_team_ip = config.my_team_ip.strip()
    if not config.service in services:
        print(f"Service {config.service} is not available, choose one of {services}")
        return
    teams = [ele["host"] for ele in configs["teams"] if not ele["nop"] and ele["host"] != config.my_team_ip]
    g.tick_time = configs["round_len"]/1000
    g.flag_regex = configs["flag_regex"]
    #For each tick
    multiprocessing.Process(target=submit_flags_loop, args=(g.flag_queue,)).start()
    while True:
        start_time = time.time()
        print("Starting new attack cycle!!!")
        flag_ids = requests.get("http://10.10.0.1:8081/flagIds").json()
        for team in teams:
            if not config.service in flag_ids.keys() or not team in flag_ids[config.service] or len(flag_ids[config.service][team]) == 0:
                print(f"Flag for {config.service} is not available yet")
            else:
                attack_list_flag_ids(team, flag_ids[config.service][team])
        delta_time = time.time() - start_time
        print(f"Attack cycle finished in {delta_time} seconds")
        if delta_time < g.tick_time:
            print(f"Sleeping for {g.tick_time - delta_time} seconds")
            time.sleep(g.tick_time - delta_time)

if __name__ == "__main__":
    try:
        while True:
            print("1. Test the attack (with NOP team)")
            print("2. Run the attack for all teams")
            print("3. Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                run_once()
            elif choice == 2:
                main()
            elif choice == 3:
                exit(0)
            else:
                print("Invalid choice")
                continue
            break
    except KeyboardInterrupt:
        exit(0)
