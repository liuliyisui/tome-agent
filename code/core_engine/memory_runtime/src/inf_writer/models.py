"""Provider-independent model boundary. No SDK, credentials or network here."""
import copy
import math
import time
from dataclasses import dataclass, field
from typing import Protocol
from .domain import ContractError, integer, text

@dataclass(frozen=True)
class ModelRequest:
    role: str
    system: str
    payload: dict
    max_output_tokens: int = 4096

@dataclass(frozen=True)
class ModelReply:
    content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    finish_reason: str = 'stop'

class ModelProvider(Protocol):
    def complete(self, request: ModelRequest) -> ModelReply: ...

@dataclass
class Budget:
    max_calls: int = 16
    max_cost_usd: float = 0.0
    max_seconds: float = 120.0
    calls: int = 0
    cost_upper_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    started: float = field(default_factory=time.monotonic,repr=False)

    def reserve(self, amount):
        integer(self.max_calls,"max_calls",1)
        if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in (amount,self.max_cost_usd,self.max_seconds)):
            raise ContractError("Invalid finite budget limit")
        if self.calls>=self.max_calls or self.cost_upper_usd+amount>self.max_cost_usd+1e-12 or time.monotonic()-self.started>=self.max_seconds:
            raise ContractError("Model request budget/deadline exhausted")
        self.calls+=1; self.cost_upper_usd+=amount

class ModelGateway:
    def __init__(self, provider: ModelProvider, budget: Budget, reserve_per_call=0.0):
        self.provider=provider; self.budget=budget; self.reserve_per_call=reserve_per_call
    def complete(self, request: ModelRequest) -> ModelReply:
        integer(request.max_output_tokens,"max_output_tokens",1)
        self.budget.reserve(self.reserve_per_call)
        # If provider/usage fails, retain the full reservation. Never retry network here.
        reply=self.provider.complete(copy.deepcopy(request))
        if not isinstance(reply,ModelReply): raise ContractError("Provider must return ModelReply with usage")
        integer(reply.input_tokens,"input_tokens"); integer(reply.output_tokens,"output_tokens")
        if type(reply.cost_usd) not in (int,float) or not math.isfinite(reply.cost_usd) or reply.cost_usd<0:
            raise ContractError("Missing/invalid cost; reservation retained")
        if reply.cost_usd>self.reserve_per_call+1e-12:
            self.budget.cost_upper_usd+=reply.cost_usd-self.reserve_per_call
            raise ContractError("Provider cost exceeded reservation; review pricing before more calls")
        self.budget.cost_upper_usd+=reply.cost_usd-self.reserve_per_call
        self.budget.input_tokens+=reply.input_tokens; self.budget.output_tokens+=reply.output_tokens
        if reply.output_tokens>request.max_output_tokens: raise ContractError("Provider exceeded output limit")
        text(reply.content,"model content")
        return reply
