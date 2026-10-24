"""Reusable atomic memory pipeline, independent of any test novel/run path."""
import copy
import sys
from pathlib import Path

SOURCE=Path(__file__).resolve().parent/'src'
sys.path.insert(0,str(SOURCE))
from inf_writer.domain import ContractError
from inf_writer.tiered_memory import empty_memory,select_context
from .pipeline import ExtractionAdapter,ReviewedTemporal,LayerAgent,recall_probe
from inf_writer.tiered_runtime import TieredMemoryAgent
from .semantics import guard_extraction,guard_temporal


class MemoryEngine:
    def __init__(self,gateway):
        self.gateway=gateway
        self.transport=ExtractionAdapter(gateway)
        self.agent=TieredMemoryAgent(self.transport)
        self.temporal=ReviewedTemporal(self.transport)
        self.layers=LayerAgent(gateway)

    def advance(self,memory,chapters,number,trace):
        """Publish nothing until extraction, time and tier phases all succeed."""
        if type(number) is not int or number!=memory.get('processed_through',0)+1:
            raise ContractError('Process chapters sequentially from the last committed checkpoint')
        prefix=copy.deepcopy(chapters[:number])
        if len(prefix)!=number or any(c['number']!=i for i,c in enumerate(prefix,1)):
            raise ContractError('Missing or unordered chapter prefix')
        if 'event_commit' in prefix[-1]:
            from .event_first import project_memory
            candidate=project_memory(memory,prefix,number,trace)
            candidate,layer_report=self.layers.run(candidate,prefix,number,prefix[-1]['title'],trace)
            return candidate,dict(chapter=number,layers=layer_report,selection_ids=[],withheld_mutations=0,
                temporal_omitted_ids=[],temporal_coverage='Canonical events own state changes; memory only chooses storage tiers',
                extraction_transforms=[],canonical_projection=True)
        selection=select_context(memory,query=prefix[-1]['text'],max_bytes=48000)
        start=len(self.transport.transforms)
        self.transport.full_memory=copy.deepcopy(memory)
        candidate=self.agent.extract(copy.deepcopy(memory),prefix,number,selection,trace)
        candidate=guard_extraction(memory,candidate,prefix,number,self.gateway,trace)
        timed=self.temporal.run(memory,candidate,prefix,number,selection,trace)
        candidate=guard_temporal(candidate,timed,prefix,number,self.gateway,trace)
        for entry in self.transport.transforms[start:]:
            for note in entry.get('normalizations',[]):
                if note.get('rule')=='attribute_storage_identifier':
                    candidate.setdefault('attribute_labels',{})[note['new']]=note['old']
        candidate,layer_report=self.layers.run(candidate,prefix,number,prefix[-1]['title'],trace)
        return candidate,dict(chapter=number,layers=layer_report,selection_ids=selection['selected_ids'],
            withheld_mutations=len(candidate.get('withheld_memory_mutations',[]))-len(memory.get('withheld_memory_mutations',[])),
            temporal_omitted_ids=selection['omitted_ids'],
            temporal_coverage='selected_old_records_only',
            extraction_transforms=copy.deepcopy(self.transport.transforms[start:]))

    def recall(self,memory,question,trace,label='query'):
        return recall_probe(memory,question,self.gateway,trace,label)

    @staticmethod
    def empty():return empty_memory()
