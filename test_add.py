import asyncio, aiohttp, uuid, json
from urllib.parse import urlencode
from datetime import datetime, timedelta

panel_url = "https://212.87.199.33:16504/YYqxXzfBAVcrlmwdQw"
panel_user = "elyas"
panel_pass = "elyas1386z"

async def test():
    session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
    try:
        await session.get(panel_url, ssl=False, timeout=aiohttp.ClientTimeout(total=10))
        csrf = ""
        async with session.get(f"{panel_url}/csrf-token", headers={"X-Requested-With": "XMLHttpRequest"}, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            csrf = data.get("obj", "")

        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "X-CSRF-Token": csrf}
        async with session.post(f"{panel_url}/login", data=urlencode({"username": panel_user, "password": panel_pass}), headers=headers, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            await resp.json()

        json_headers = {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest", "X-CSRF-Token": csrf}
        
        user_uuid = str(uuid.uuid4())
        sub_id = uuid.uuid4().hex[:16]
        email = f"test_bot_{int(datetime.utcnow().timestamp())}"
        days = 30
        total_bytes = int(50 * 1024 * 1024 * 1024)
        expiry_time = int((datetime.utcnow() + timedelta(days=days)).timestamp() * 1000)
        
        payload = {
            "client": {
                "email": email,
                "subId": sub_id,
                "id": user_uuid,
                "password": "",
                "auth": "",
                "flow": "",
                "security": "auto",
                "totalGB": total_bytes,
                "expiryTime": expiry_time,
                "reset": 0,
                "limitIp": 0,
                "tgId": 0,
                "group": "",
                "comment": "",
                "enable": True,
            },
            "inboundIds": [1],
        }
        
        print(f"Adding client to inbound 1...")
        async with session.post(f"{panel_url}/panel/api/clients/add", json=payload, headers=json_headers, ssl=False, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            data = await resp.json()
            print(f"Result: {json.dumps(data, indent=2)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await session.close()

asyncio.run(test())
