import requests

TOKEN = "EAAeqPrspEhoBRx2VHjQOXUZCySI9V1qChBi0L9FBjM8Wr3afruK1UTVwPWPhI9QQB9AbhJ5mS67Ae5umYDS2RUGqVhRvFZBzDlPXLiqxnxceNK5z3o0zSbDpzSRji97RxHfqVuczZC4UjitB4EWB3ErHzIk4gZCZB3uvgu9Ob29lufOAyMwzRnginZBSE3v9WlPWoLqHMZD"
PAGE_ID = "104351191587455"

r = requests.get(
    f"https://graph.facebook.com/v18.0/{PAGE_ID}",
    params={"fields": "name,fan_count", "access_token": TOKEN},
    timeout=10
)

if r.status_code == 200:
    data = r.json()
    print("✅ Facebook Token: HOẠT ĐỘNG")
    print(f"   Page: {data.get('name')}")
    print(f"   Followers: {data.get('fan_count', 0):,}")
else:
    err = r.json().get("error", {})
    print(f"❌ Error: {err.get('message')}")
    print(f"   Code: {err.get('code')}")
