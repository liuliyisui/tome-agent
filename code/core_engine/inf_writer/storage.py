"""Single-writer JSON checkpoints with CAS, exclusive locks and atomic replacement.

Not a distributed database. A crash may leave a lock requiring explicit recovery.
"""
import json
import os
import tempfile
from pathlib import Path
from .domain import ContractError, ConflictError, Snapshot, canonical, project_id, strict_json

class FileStore:
    def __init__(self,root): self.root=Path(root).resolve()
    def directory(self,identifier):
        candidate=self.root/project_id(identifier)
        # Also reject a preexisting symlink/junction escaping the selected run root.
        if candidate.resolve().parent!=self.root: raise ContractError("Project directory escapes run root")
        return candidate
    def _atomic(self,path,data):
        path.parent.mkdir(parents=True,exist_ok=True)
        fd,name=tempfile.mkstemp(prefix=".inf-",suffix=".tmp",dir=path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as stream:
                stream.write(canonical(data)+"\n"); stream.flush(); os.fsync(stream.fileno())
            os.replace(name,path)
        finally:
            if os.path.exists(name): os.unlink(name)
    def initialize(self,state):
        state=Snapshot.from_dict(state.to_dict())
        if state.revision!=0: raise ContractError("Initialize requires an empty chapter checkpoint")
        folder=self.directory(state.project_id); folder.mkdir(parents=True,exist_ok=True)
        lock=folder/"checkpoint.lock"
        try: handle=lock.open("x",encoding="utf-8")
        except FileExistsError as exc: raise ConflictError("Project is locked; inspect recovery before retry") from exc
        try:
            with handle: handle.write(str(os.getpid()))
            path=folder/"checkpoint.json"
            if path.exists(): raise ConflictError("Project already initialized; never overwrite")
            self._atomic(path,state.to_dict())
        finally: lock.unlink()
    def load(self,identifier):
        path=self.directory(identifier)/"checkpoint.json"
        state=Snapshot.from_dict(strict_json(path.read_text(encoding="utf-8")))
        if state.project_id!=identifier: raise ContractError("Checkpoint project mismatch")
        return state
    def commit(self,state,expected_revision):
        candidate=Snapshot.from_dict(state.to_dict()); folder=self.directory(candidate.project_id)
        lock=folder/"checkpoint.lock"
        try: handle=lock.open("x",encoding="utf-8")
        except FileExistsError as exc: raise ConflictError("Project is locked; do not remove another writer's lock") from exc
        try:
            with handle: handle.write(str(os.getpid()))
            previous=self.load(candidate.project_id)
            if previous.revision!=expected_revision or candidate.revision!=expected_revision+1: raise ConflictError("Stale checkpoint revision")
            if (candidate.goal,candidate.constraints)!=(previous.goal,previous.constraints): raise ConflictError("Chapter commit cannot rewrite story contract")
            if candidate.chapters[:len(previous.chapters)]!=previous.chapters or candidate.history[:len(previous.history)]!=previous.history:
                raise ConflictError("Chapter commit cannot rewrite accepted prose/history")
            if any(candidate.receipts.get(k)!=v for k,v in previous.receipts.items()): raise ConflictError("Existing receipt changed")
            if any(candidate.plan.get(k)!=v for k,v in previous.plan.items() if int(k)<=previous.revision): raise ConflictError("Written chapter plan changed")
            self._atomic(folder/"checkpoint.json",candidate.to_dict())
        finally: lock.unlink()
    def save_audit(self,identifier,attempt_id,record):
        project_id(attempt_id)
        folder=self.directory(identifier)/"audit"
        if folder.resolve().parent!=self.directory(identifier).resolve(): raise ContractError("Audit directory escapes project")
        path=folder/(attempt_id+".json")
        if path.exists(): raise ConflictError("Audit attempt exists; never overwrite")
        self._atomic(path,record)
