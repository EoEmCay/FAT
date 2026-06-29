import requests
from datetime import datetime

TOKEN = "EAAeqPrspEhoBRx2VHjQOXUZCySI9V1qChBi0L9FBjM8Wr3afruK1UTVwPWPhI9QQB9AbhJ5mS67Ae5umYDS2RUGqVhRvFZBzDlPXLiqxnxceNK5z3o0zSbDpzSRji97RxHfqVuczZC4UjitB4EWB3ErHzIk4gZCZB3uvgu9Ob29lufOAyMwzRnginZBSE3v9WlPWoLqHMZD"

r = requests.get(
    "https://graph.facebook.com/debug_token",
    params={"input_token": TOKEN, "access_token": TOKEN},
    timeout=10
)

data = r.json().get("data", {})
expires_at = data.get("expires_at", 0)

if expires_at == 0:
    print("✅ Token: KHÔNG CÓ HẠN (vĩnh viễn hoặc page token dài hạn)")
else:
    exp_date = datetime.fromtimestamp(expires_at)
    days_left = (exp_date - datetime.now()).days
    print(f"✅ Token hết hạn: {exp_date.strftime('%d/%m/%Y')} ({days_left} ngày nữa)")

print(f"   Type: {data.get('type')}")
print(f"   App:  {data.get('application')}")
