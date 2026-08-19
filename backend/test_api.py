import httpx

url = "https://himalayas.app/jobs/api"

params = {
    "limit": 1,
    "offset": 0
}

response = httpx.get(url, params=params, timeout=20)

print("Status:", response.status_code)

data = response.json()

job = data["jobs"][0]

print("\n========== ONE COMPLETE JOB ==========\n")

print(job)