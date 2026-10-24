"""Render declared references only. No arithmetic, coverage or story checking."""
import re
from inf_writer.domain import ContractError,canonical
from .numeric_grounding import render as render_quantities,sources
from .time_calculation import render as render_time

EVENT=re.compile(r'\[\[event:([A-Za-z][A-Za-z0-9_]{0,63})\]\]')


def render(prose,commit,quantity_sources=()):
    from .event_first import verify
    verify(commit)
    if canonical(list(quantity_sources))!=canonical(sources(commit)):
        raise ContractError('Quantity source table differs from its event data')
    catalogue={}
    for scene in commit['scenes']:
        for beat in scene['beats']:
            catalogue[beat['id']]=beat['statement']
            catalogue[beat.get('token_id',beat['id'])]=beat['statement']
    # A marker immediately annotating its own literal is an encoding pair.
    # No global sentence deduplication or event-completeness inspection occurs.
    for identifier,statement in catalogue.items():
        token='[[event:'+identifier+']]'
        prose=re.sub(re.escape(token)+r'\s*'+re.escape(statement),lambda _:token,prose)
        prose=re.sub(re.escape(statement)+r'\s*'+re.escape(token),lambda _:token,prose)
    def replace(match):
        if match[1] not in catalogue:raise ContractError('Unknown event source slot')
        return catalogue[match[1]]
    result=EVENT.sub(replace,prose)
    result=render_quantities(result,quantity_sources)
    result=render_time(result,commit['computed_times'],check_semantics=False)
    if '[[event:' in result:raise ContractError('Malformed event source slot')
    return result


def saved_text(chapter):
    if chapter.get('prose_policy')=='unchecked':
        if chapter.get('prose_encoding')=='literal':return chapter['realization_template']
        return render(chapter['realization_template'],chapter['event_commit'],chapter.get('quantity_sources',[]))
    from .event_first import realize
    return realize(chapter['realization_template'],chapter['event_commit'])
