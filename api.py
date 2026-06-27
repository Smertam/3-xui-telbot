import uuid
import json
import re
import aiohttp
from urllib.parse import urlencode
from datetime import datetime, timedelta
import web_db


class PanelAPI:
    def __init__(self):
        self.panel_url = ""
        self.panel_user = ""
        self.panel_pass = ""
        self.sub_link_template = ""
        self.inbound_ids = []
        self.base_path = ""
        self.session: aiohttp.ClientSession | None = None
        self.csrf_token: str = ""
        try:
            self.reload_config()
        except Exception:
            pass

    def reload_config(self):
        self.panel_url = (web_db.get_setting("panel_url") or "").rstrip("/")
        self.panel_user = web_db.get_setting("panel_user") or ""
        self.panel_pass = web_db.get_setting("panel_pass") or ""
        self.sub_link_template = web_db.get_setting("sub_link_template") or ""
        raw = web_db.get_setting("inbound_id") or ""
        self.inbound_ids = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
        self.base_path = ""
        self._extract_base_path()

    def _extract_base_path(self):
        match = re.search(r"https?://[^/]+(/.+)", self.panel_url)
        if match:
            self.base_path = match.group(1).rstrip("/")
        else:
            self.base_path = ""

    @property
    def base_url(self):
        return self.panel_url

    @property
    def api_url(self):
        return f"{self.panel_url}{self.base_path}/panel/api"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                cookie_jar=aiohttp.CookieJar(unsafe=True)
            )
        return self.session

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-Token": self.csrf_token,
        }

    def _json_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-Token": self.csrf_token,
        }

    async def login(self) -> bool:
        session = await self._get_session()
        try:
            await session.get(
                self.panel_url,
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10),
            )

            async with session.get(
                f"{self.panel_url}/csrf-token",
                headers={"X-Requested-With": "XMLHttpRequest"},
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.csrf_token = data.get("obj", "")

            async with session.post(
                f"{self.panel_url}/login",
                data=urlencode({"username": self.panel_user, "password": self.panel_pass}),
                headers=self._headers(),
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return True
        except Exception as e:
            print(f"Panel login error: {e}")
        return False

    async def _get(self, path: str) -> dict | None:
        session = await self._get_session()
        url = f"{self.panel_url}{path}"
        try:
            async with session.get(
                url,
                headers=self._json_headers(),
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status in (401, 403):
                    if await self.login():
                        async with session.get(
                            url,
                            headers=self._json_headers(),
                            ssl=False,
                            timeout=aiohttp.ClientTimeout(total=15),
                        ) as retry_resp:
                            if retry_resp.status == 200:
                                return await retry_resp.json()
        except Exception as e:
            print(f"Panel GET error: {e}")
        return None

    async def _post(self, path: str, data: dict | None = None, use_json: bool = True) -> dict | None:
        session = await self._get_session()
        url = f"{self.panel_url}{path}"
        try:
            kwargs = {"ssl": False, "timeout": aiohttp.ClientTimeout(total=15)}
            if use_json:
                kwargs["json"] = data or {}
                kwargs["headers"] = self._json_headers()
            else:
                kwargs["data"] = urlencode(data or {})
                kwargs["headers"] = self._headers()

            async with session.post(url, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status in (401, 403):
                    if await self.login():
                        kwargs["headers"] = self._json_headers() if use_json else self._headers()
                        async with session.post(url, **kwargs) as retry_resp:
                            if retry_resp.status == 200:
                                return await retry_resp.json()
        except Exception as e:
            print(f"Panel POST error: {e}")
        return None

    async def get_inbounds(self) -> list:
        data = await self._get("/panel/api/inbounds/list")
        if data and data.get("success"):
            return data.get("obj", [])
        return []

    async def get_inbound(self, inbound_id: int) -> dict | None:
        data = await self._get(f"/panel/api/inbounds/get/{inbound_id}")
        if data and data.get("success"):
            return data.get("obj")
        return None

    async def get_vless_inbound_id(self) -> int | None:
        inbounds = await self.get_inbounds()
        for inbound in inbounds:
            if inbound.get("protocol") == "vless" and inbound.get("enable"):
                return inbound.get("id")
        return None

    async def add_client(self, inbound_ids: list[int], email: str, total_gb: float = 0, days: int = 0) -> dict | None:
        user_uuid = str(uuid.uuid4())
        sub_id = uuid.uuid4().hex[:16]

        total_bytes = int(total_gb * 1024 * 1024 * 1024) if total_gb > 0 else 0
        expiry_time = 0
        if days > 0:
            expiry_time = int((datetime.utcnow() + timedelta(days=days)).timestamp() * 1000)

        client_payload = {
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
            "inboundIds": inbound_ids,
        }

        result = await self._post("/panel/api/clients/add", client_payload)
        if result and result.get("success"):
            return {"uuid": user_uuid, "sub_id": sub_id, "email": email}
        return None

    def get_sub_link(self, email: str, sub_id: str) -> str:
        if self.sub_link_template:
            return self.sub_link_template.replace("{sub_id}", sub_id).replace("{id}", sub_id)
        import re
        match = re.search(r"https?://([^:/]+)", self.panel_url)
        host = match.group(1) if match else "localhost"
        return f"https://{host}:2096/sub/{sub_id}"

    async def create_config(self, email: str, days: int = 30, total_gb: int = 0) -> dict | None:
        inbound_ids = self.inbound_ids if self.inbound_ids else []
        if not inbound_ids:
            vid = await self.get_vless_inbound_id()
            if vid is not None:
                inbound_ids = [vid]

        if not inbound_ids:
            print("No inbounds configured")
            return None

        result = await self.add_client(inbound_ids, email, total_gb=total_gb, days=days)
        if result:
            sub_link = self.get_sub_link(email, result["sub_id"])
            expire_date = (datetime.utcnow() + timedelta(days=days)).isoformat()
            return {
                "uuid": result["uuid"],
                "email": result["email"],
                "sub_link": sub_link,
                "expire_date": expire_date,
            }

        print("Failed to add client")
        return None

    async def create_test_config(self, email: str, total_mb: int = 102400) -> dict | None:
        inbound_ids = self.inbound_ids if self.inbound_ids else []
        if not inbound_ids:
            vid = await self.get_vless_inbound_id()
            if vid is not None:
                inbound_ids = [vid]

        if not inbound_ids:
            print("No inbounds configured")
            return None

        total_gb = total_mb / 1024
        result = await self.add_client(inbound_ids, email, total_gb=total_gb, days=1)
        if result:
            sub_link = self.get_sub_link(email, result["sub_id"])
            expire_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
            return {
                "uuid": result["uuid"],
                "email": result["email"],
                "sub_link": sub_link,
                "expire_date": expire_date,
            }

        print("Failed to add test client")
        return None

    async def get_client_configs(self, email: str) -> list:
        inbounds = await self.get_inbounds()
        configs = []
        for inbound in inbounds:
            clients = inbound.get("settings", {}).get("clients", [])
            for client in clients:
                if client.get("email") == email:
                    configs.append({
                        "inbound_id": inbound["id"],
                        "tag": inbound.get("tag", ""),
                        "protocol": inbound.get("protocol", ""),
                        "email": client.get("email", ""),
                    })
        return configs

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


panel_api = PanelAPI()
