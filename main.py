import time
import os
import datetime
from pyduinocoin import DuinoClient
from colorama import init, Fore, Style
from tabulate import tabulate
from threading import Thread

# Initialize colorama
init()

def get_user_data(username):
    try:
        result = client.user(username)
        balance = result.balance.balance
        miners_data = [[miner['identifier'], miner['hashrate'], miner['pool']] for miner in result.miners]
        transactions_data = [[transaction['datetime'], transaction['amount'], transaction['memo']] for transaction in result.transactions]
        return balance, miners_data, transactions_data
    except Exception as error:
        print(Fore.RED + "Error:", error)
        return None, None, None

def read_initial_balance():
    if os.path.exists("initial_balance.txt"):
        with open("initial_balance.txt", "r") as file:
            data = file.read().split(',')
            initial_date = datetime.datetime.fromisoformat(data[0])
            initial_balance = float(data[1].strip())
            return initial_date, initial_balance
    else:
        return None, None

def save_initial_balance(initial_date, initial_balance):
    with open("initial_balance.txt", "w") as file:
        file.write(f"{initial_date.isoformat()},{initial_balance}")

def read_mining_start_time():
    if os.path.exists("mining_start_time.txt"):
        with open("mining_start_time.txt", "r") as file:
            start_time = datetime.datetime.fromisoformat(file.read().strip())
        return start_time
    else:
        return datetime.datetime.now()

def save_mining_start_time(start_time):
    with open("mining_start_time.txt", "w") as file:
        file.write(start_time.isoformat())

def update_data(username):
    initial_date, initial_balance = read_initial_balance()
    mining_start_time = read_mining_start_time()

    # Check if it's the first run and save the start time
    if not os.path.exists("mining_start_time.txt"):
        save_mining_start_time(mining_start_time)
    while True:
        print(Fore.CYAN + """
    ____        _                      ______      _     
   / __ \__  __(_)___  ____  ____     / ____/___  (_)___ 
  / / / / / / / / __ \/ __ \/ __ \   / /   / __ \/ / __ \\
 / /_/ / /_/ / / /_/ / / / / /_/ /  / /___/ /_/ / / / / /
/_____/\__,_/_/\____/_/ /_/\____/   \____/\____/_/_/ /_/ 
                                                         
        """)
        print(Fore.CYAN + "Index:\n")
        
        balance, miners_data, transactions_data = get_user_data(username)
        if balance is not None:
            print(Fore.GREEN + "Current Balance: ", balance)
            print(Fore.CYAN + "\nMiners:")
            print(tabulate(miners_data, headers=["Identifier", "Hashrate", "Pool"], tablefmt="plain"))
            print(Fore.LIGHTMAGENTA_EX + "\nTransactions:")
            print(tabulate(transactions_data, headers=["Datetime", "Amount", "Memo"], tablefmt="plain"))
            
            if initial_balance is None:
                initial_date = datetime.datetime.now()
                initial_balance = balance
                save_initial_balance(initial_date, initial_balance)
            
            earnings, time_elapsed = calculate_show_earnings(initial_date, initial_balance, balance)
            show_earnings_by_period(earnings, time_elapsed)
            show_mining_duration(mining_start_time)

        time.sleep(60)

def calculate_show_earnings(initial_date, initial_balance, current_balance):
    earnings = current_balance - initial_balance
    time_elapsed = datetime.datetime.now() - initial_date
    print(Fore.YELLOW + f"\nTotal earnings since {initial_date.strftime('%Y-%m-%d %H:%M:%S')}: {earnings:.2f}")
    return earnings, time_elapsed

def show_earnings_by_period(earnings, time_elapsed):
    seconds = time_elapsed.total_seconds()
    minutes = seconds / 60
    hours = seconds / 3600
    days = time_elapsed.days
    weeks = days / 7
    months = days / 30
    years = days / 365
    
    print(Fore.YELLOW + f"Earnings per minute: {earnings / minutes if minutes else 0:.2f}")
    print(Fore.YELLOW + f"Earnings per hour: {earnings / hours if hours else 0:.2f}")
    print(Fore.YELLOW + f"Earnings per day: {earnings / days if days else 0:.2f}")
    print(Fore.YELLOW + f"Earnings per week: {earnings / weeks if weeks else 0:.2f}")
    print(Fore.YELLOW + f"Earnings per month: {earnings / months if months else 0:.2f}")
    print(Fore.YELLOW + f"Earnings per year: {earnings / years if years else 0:.2f}")

def show_mining_duration(mining_start_time):
    mining_duration = datetime.datetime.now() - mining_start_time
    print(Fore.YELLOW + f"Mining Duration: {mining_duration.days} days, {mining_duration.seconds // 3600} hours")

client = DuinoClient()
username = input("Please enter your username: ")
update_thread = Thread(target=update_data, args=(username,))
update_thread.daemon = True
update_thread.start()
update_thread.join()
print(Style.RESET_ALL)
