import requests
key = "x2rpZ0ewr3pe40WpyTaFENRd5fUsfOsCJlPycXc3wfk"
r = requests.get(
    "https://api.unsplash.com/search/photos",
    params={"query": "artificial intelligence", "per_page": 1, "client_id": key},
    timeout=10
)
if r.status_code == 200:
    photo = r.json()["results"][0]
    print("✅ Unsplash API: HOẠT ĐỘNG")
    print(f"   Ảnh: {photo['urls']['regular']}")
    print(f"   Tác giả: {photo['user']['name']}")
else:
    print(f"❌ Error {r.status_code}: {r.text}")
