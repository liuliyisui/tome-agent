"""Deterministic demonstration only. No inference or network requests."""
import json
from .models import ModelReply

class DemoModel:
    def __init__(self): self.calls=0
    def complete(self,request):
        self.calls+=1; n=request.payload["chapter_number"]
        if n not in (1,2): raise ValueError("Offline demonstration contains exactly two fixture chapters")
        body="艾岚的眼睛是灰色。她在灯塔前等候守卫。" if n==1 else "艾岚喝下药剂，眼睛变为金色。守卫在自然光下确认了变化。"
        if request.role=="planner":
            data={"number":n,"title":"灯塔前的约定" if n==1 else "金色的双眼","brief":"展示眼色与身份核验事件","future_updates":[]}
        elif request.role=="writer": data={"text":body}
        elif request.role=="memory":
            data={"changes":[{"action":"store" if n==1 else "update","subject":"艾岚","attribute":"eye_color","value":"灰色" if n==1 else "金色",
               "expected_revision":None if n==1 else 1,"quote":"艾岚的眼睛是灰色。" if n==1 else "艾岚喝下药剂，眼睛变为金色。","reason":"当前正文明确给出眼色或变化"}]}
        elif request.role=="reviewer": data={"approved":True,"issues":[]}
        else: raise ValueError("Unknown role")
        return ModelReply(json.dumps(data,ensure_ascii=False),0,0,0.0)
