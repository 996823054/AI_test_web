"""敏感信息脱敏服务。"""

import re
from typing import Any, Dict


class MaskingService:
    def mask_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'(password|密码|token|cookie|authorization|api_key)\s*[:=]\s*[^\s,\'"}]+', r'\1: [MASK]', text, flags=re.IGNORECASE)
        text = re.sub(r'\b1[3-9]\d{9}\b', r'[MASK_PHONE]', text)
        text = re.sub(r'\b\d{17}[\dXx]\b', r'[MASK_ID]', text)
        return text

    def mask_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not payload:
            return {}
        result = {}
        for key, value in payload.items():
            if isinstance(value, str):
                result[key] = self.mask_text(value)
            elif isinstance(value, dict):
                result[key] = self.mask_payload(value)
            elif isinstance(value, list):
                result[key] = [
                    self.mask_payload(item) if isinstance(item, dict)
                    else (self.mask_text(item) if isinstance(item, str) else item)
                    for item in value
                ]
            else:
                result[key] = value
        return result
