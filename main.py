import requests
import time
from threading import Thread
from pyduinocoin import DuinoClient
from colorama import init, Fore, Style
from tabulate import tabulate
from datetime import datetime


# Initialize colorama
init()
last_duco_price = None

DUCO_STATISTICS_ENDPOINT = "https://server.duinocoin.com/statistics"

# Get the current DUCO price
def get_duco_price():
    try:
        response = requests.get(DUCO_STATISTICS_ENDPOINT)
        response.raise_for_status() 
        statistics = response.json()
        duco_price = statistics.get("Duco price", 0.00023600)  
        return duco_price
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to retrieve Duco price: {e}")
        return None

def get_user_data(username):
    try:
        result = client.user(username)
        balance = result.balance.balance
        miners_data = [[miner['identifier'], miner['hashrate'], miner['pool']] for miner in result.miners]
        transactions_data = [[transaction['datetime'], transaction['amount'], transaction['memo']] for transaction in result.transactions]

        # Convert transaction dates from string to datetime
        transactions_dates = [datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S") for date_str, _, _ in transactions_data]
        first_transaction_date = min(transactions_dates) if transactions_dates else None

        return balance, miners_data, transactions_data, first_transaction_date
    except Exception as error:
        print(Fore.RED + "Error:", error)
        return None, None, None, None

# Mining function
def mine(username):
    last_transaction_count = 0
    while True:
        try:
            current_date = datetime.now()
            balance, miners_data, transactions_data, first_transaction_date = get_user_data(username)

            if balance is not None and first_transaction_date:
                print(Fore.GREEN + "\nCurrent Balance: ")
                print_table([["Balance", balance]])
                print(Fore.CYAN + "\nMiners:")
                print_table(miners_data, headers=["Identifier", "Hashrate", "Pool"])
                print(Fore.LIGHTMAGENTA_EX + "\nTransactions:")
                print_table(transactions_data, headers=["Datetime", "Amount", "Memo"])

                if len(transactions_data) > last_transaction_count:
                    print(Fore.YELLOW + "\nNew transaction detected!")
                    print(ascii_logo())
                    last_transaction_count = len(transactions_data)

                calculate_show_earnings(username, first_transaction_date, current_date, balance)
            else:
                print(Fore.RED + "Failed to retrieve or parse first transaction date.")

            print_coin_icon()
            print(Style.RESET_ALL)
            time.sleep(5)  # Wait for 5 seconds
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nMining stopped.")
            break
    print("\nMining process completed!")

# Calculate and display earnings
def calculate_show_earnings(username, first_transaction_date, current_date, current_balance):
    try:
        if isinstance(first_transaction_date, datetime):
            # Calculate the elapsed time since the first transaction
            time_elapsed = current_date - first_transaction_date

            # Display the current balance
            print(Fore.YELLOW + f"\nCurrent balance since {first_transaction_date.strftime('%Y-%m-%d %H:%M:%S')}: {current_balance:.8f} DUCO")
            print_table([["Current Balance", f"{current_balance:.8f} DUCO"]])

            # Calculate and display earnings
            earnings_table = [
                ["Rate per minute", f"{current_balance / (time_elapsed.total_seconds() / 60):.8f} DUCO/min"],
                ["Rate per hour", f"{current_balance / (time_elapsed.total_seconds() / 3600):.8f} DUCO/hr"],
                ["Rate per day", f"{current_balance / (time_elapsed.total_seconds() / 86400):.8f} DUCO/day"],
                ["Rate per week", f"{current_balance / (time_elapsed.total_seconds() / 604800):.8f} DUCO/week"],
                ["Rate per month", f"{current_balance / (time_elapsed.total_seconds() / 2592000):.8f} DUCO/month"],
                ["Rate per year", f"{current_balance / (time_elapsed.total_seconds() / 31536000):.8f} DUCO/year"],
                ["Time since first transaction", f"{time_elapsed.days} days {time_elapsed.seconds // 3600} hours {time_elapsed.seconds % 3600 // 60} minutes"]
            ]
            print_table(earnings_table)
        else:
            print(Fore.GREEN + "Start mining to calculate earnings.")
    except Exception as e:
        print(Fore.RED + f"Error calculating earnings: {e}")

def print_table(data, headers=["Description", "Value"]):
    try:
        print(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(Fore.RED + f"Error displaying table: {e}")

def ascii_logo():
    return """
██████╗ ██╗   ██╗ ██████╗ ██████╗     ██████╗ ███████╗██╗    ██╗ █████╗ ██████╗ ██████╗ ███████╗
██╔══██╗██║   ██║██╔════╝██╔═══██╗    ██╔══██╗██╔════╝██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝
██║  ██║██║   ██║██║     ██║   ██║    ██████╔╝█████╗  ██║ █╗ ██║███████║██████╔╝██║  ██║███████╗
██║  ██║██║   ██║██║     ██║   ██║    ██╔══██╗██╔══╝  ██║███╗██║██╔══██║██╔══██╗██║  ██║╚════██║
██████╔╝╚██████╔╝╚██████╗╚██████╔╝    ██║  ██║███████╗╚███╔███╔╝██║  ██║██║  ██║██████╔╝███████║
"""

def print_coin_icon():
    try:
        length_of_bar = 63 # Progress bar length
        # Coin icons
        coin_icons = [f"{Fore.YELLOW}🪙{Style.RESET_ALL}", f"{Fore.YELLOW}🪙{Style.RESET_ALL}"]

        for i in range(length_of_bar):
            # Coin icon
            coin_icon = coin_icons[i % 2]  # Alternate between two coin icons
            # Spaces before the coin icon
            espacio_anterior = " " * i
            # Empty spaces after the coin icon
            espacio_posterior = " " * (length_of_bar - i - 1)

            # Create the line with the coin icon
            linea_movil = f"{espacio_anterior}{coin_icon}{espacio_posterior}"

            # Print the line with the coin icon
            print(f"\r{linea_movil}", end="")
            time.sleep(0.2)  # Delay to create the animation

        # Clear the line
        print("\r", end="")
    except Exception as e:
        print(Fore.RED + "Error:", e)


def main():
    while True:
        # Print the ASCII logo
        print(Fore.CYAN + """
        ____        _                      ______      _     
       / __ \__  __(_)___  ____  ____     / ____/___  (_)___ 
      / / / / / / / / __ \/ __ \/ __ \   / /   / __ \/ / __ \\
     / /_/ / /_/ / / /_/ / / / / /_/ /  / /___/ /_/ / / / / /
    /_____/\__,_/_/\____/_/ /_/\____/   \____/\____/_/_/ /_/ 
                                                             
    """)

        # Get the username
        username = input(Fore.YELLOW + "Please enter your username: ")
        if not username:
            print(Fore.RED + "Username cannot be empty.")
            continue

        try:
            result = client.user(username)
            dates = [transaction['datetime'] for transaction in result.transactions]

            # Get the farthest date
            farthest_date = max(dates)

            # Get the current date
            current_date = datetime.now()

            # Get the user data
            calculate_show_earnings(username, farthest_date, current_date, result.balance.balance)  # Use the farthest date as the start date          
            # Check if the user exists
        except Exception as e:
            print(Fore.RED + "Error:", e)
            print(Fore.RED + "Failed to check user existence.")
            continue

        # Create a thread for mining
        mine_thread = Thread(target=mine, args=(username,))
        mine_thread.daemon = True
        mine_thread.start()

        # Wait for the mining thread to finish
        mine_thread.join()

        print(Style.RESET_ALL)
        break

if __name__ == "__main__":
    client = DuinoClient()  # Create a DuinoClient instance
    main()
