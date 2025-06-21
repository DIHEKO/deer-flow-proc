from typing import List, Optional, Dict
import json
import time
# from boto3 import Session

class static_secret_manager:
    def __init__(self, secret: str):
        self._secret: str = secret

    def get_verification_secrets(self) -> [str]:
        return [self._secret]

    def get_signing_secret(self) -> str:
        return self._secret

class diheko_aws_secret_Manager:
    def __init__(self, client, secret_id: str, update_interval_seconds: float=60*60):
        """
        client: boto3 secrets manager client
        """
        self._client = client
        self._secret_id: str = secret_id
        self._cache: Dict[str, str] = {}
        self._last_update: Optional[float] = None
        self._update_interval_seconds: float = update_interval_seconds
        self._update()
        
    def _update(self):
        if self._last_update != None and time.time() - self._last_update < self._update_interval_seconds:
            return

        result = self._client.get_secret_value(SecretId=self._secret_id)
        self._cache = json.loads(result['SecretString'])
        self._last_update = time.time()

    def get_verification_secrets() -> List[str]:
        self._update()
        return list(self._cache.values())

    def get_signing_secret() -> str:
        self._update()
        return self.cache['current']
