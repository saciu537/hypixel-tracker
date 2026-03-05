import requests
import time

API_KEY = "YOUR_HYPIXEL_KEY"
PLAYER_NAME = "saciu"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

CHECK_INTERVAL = 60


def get_uuid(username):
    try:
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            return r.json()["id"]
    except:
        pass

    return None


def check_api_key():
    try:
        url = f"https://api.hypixel.net/key?key={API_KEY}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            data = r.json()

            if data.get("success"):
                return True

    except:
        pass

    return False


def is_online(uuid):
    try:
        url = f"https://api.hypixel.net/status?key={API_KEY}&uuid={uuid}"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            data = r.json()

            if data.get("session"):
                return data["session"].get("online", False)

    except:
        pass

    return False


def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": text
        }

        requests.post(url, data=payload, timeout=10)

    except:
        print("Telegram error")


def main():

    uuid = get_uuid(PLAYER_NAME)

    if not uuid:
        print("Player not found")
        return

    print("UUID:", uuid)

    if not check_api_key():
        print("Hypixel API key invalid")
        send_telegram_message("⚠️ Hypixel API key wygasł lub jest niepoprawny.")
        return

    last_status = False
    api_check_timer = 0

    while True:
        try:

            # co 1h sprawdzamy czy API key nadal działa
            if api_check_timer >= 60:

                if not check_api_key():
                    send_telegram_message("⚠️ Hypixel API key wygasł.")
                    print("API key expired")

                api_check_timer = 0

            current_status = is_online(uuid)

            if current_status and not last_status:
                print("Player joined")
                send_telegram_message(f"🟢 {PLAYER_NAME} jest online!")

            if not current_status and last_status:
                print("Player left")
                send_telegram_message(f"🔴 {PLAYER_NAME} wyszedł.")

            last_status = current_status

            api_check_timer += 1

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print("Error:", e)
            time.sleep(30)


if __name__ == "__main__":
    main()
