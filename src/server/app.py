from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from src.provider_manager.manager import ProviderManager

app = FastAPI(title="CtrlAltBuildIt Provider API")
pm = ProviderManager.from_config()


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]


@app.get("/providers")
def list_providers():
    providers = []
    for name in pm.list_providers():
        p = pm.get(name)
        providers.append({"name": name, "info": p.model_info(), "healthy": p.health_check()})
    return {"providers": providers}


@app.post("/providers/{name}/chat")
def provider_chat(name: str, req: ChatRequest):
    p = pm.get(name)
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    try:
        resp = p.chat(req.messages)
        return {"provider": name, "response": resp}
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Chat not implemented for this provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
