import requests
key = "9W01NButyrKjr9YnarjQCRG5QN9OtThJIPNTwWh7XDve7J1gMarYGXcy"
r = requests.get(
    "https://api.pexels.com/v1/search",
    params={"query": "artificial intelligence", "per_page": 1},
    headers={"Authorization": key},
    timeout=10
)
if r.status_code == 200:
    photo = r.json()["photos"][0]
    print("✅ Pexels API: HOẠT ĐỘNG")
    print(f"   Ảnh: {photo['src']['large']}")
    print(f"   Tác giả: {photo['photographer']}")
else:
    print(f"❌ Error {r.status_code}: {r.text}")
