import argparse
import requests

def send_message(ntfy_url, ntfy_token, message):
    response = requests.post(
        ntfy_url,
        data=message,
        headers={"Authorization": f"Bearer {ntfy_token}"}
    )
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a message.")
    parser.add_argument("url", help="NTFY URL")
    parser.add_argument("token", help="NTFY Token")
    parser.add_argument("message", help="Message to send")
    args = parser.parse_args()

    response = send_message(args.url, args.token, args.message)
    print(response)