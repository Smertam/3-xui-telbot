import asyncio, aiohttp, re
from urllib.parse import urlencode

panel_url = "https://212.87.199.33:16504/YYqxXzfBAVcrlmwdQw"
panel_user = "elyas"
panel_pass = "elyas1386z"

async def test():
    session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
    try:
        # Get page
        await session.get(panel_url, ssl=False, timeout=aiohttp.ClientTimeout(total=10))
        
        # Get CSRF token
        csrf = ""
        async with session.get(f"{panel_url}/csrf-token", headers={"X-Requested-With": "XMLHttpRequest"}, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                csrf = data.get("obj", "")
                print(f"CSRF: {csrf[:20]}...")
        
        # Login
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-Token": csrf,
        }
        async with session.post(f"{panel_url}/login", data=urlencode({"username": panel_user, "password": panel_pass}), headers=headers, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            print(f"Login: {data}")
        
        # Get inbounds
        json_headers = {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest", "X-CSRF-Token": csrf}
        async with session.get(f"{panel_url}/panel/api/inbounds/list", headers=json_headers, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            if data.get("success"):
                for inbound in data.get("obj", []):
                    print(f"Inbound #{inbound['id']}: {inbound.get('tag','')} protocol={inbound.get('protocol','')} enable={inbound.get('enable')}")
            else:
                print(f"Inbounds error: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await session.close()

asyncio.run(test())
