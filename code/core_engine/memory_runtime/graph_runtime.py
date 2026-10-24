"""LangGraph orchestration for the actual UI and CLI writing session.

The graph is invocation-local. Durable story/event/memory state remains in the
existing atomic book checkpoints, not in a second competing graph database.
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class WritingGraphState(TypedDict):
    # Per-invocation workspace. Never persisted as a LangGraph checkpoint.
    run: dict


def new_run(session, instruction):
    number = len(session.book['chapters']) + 1
    return dict(instruction=instruction, number=number, trace=[],
                revision_requested=False,
                row=dict(chapter_number=number, status='NO_DRAFT', errors=[],
                         issues=[], suggestions=[], memory_promoted=False,
                         memory_update_status='NOT_RUN', stop_reason=None))


def build_writing_graph(session):
    graph = StateGraph(WritingGraphState)

    def phase(name, action):
        def node(state):
            run = state['run']
            run['trace'].append(dict(role='orchestration', framework='langgraph',
                                     node=name, chapter=run['number']))
            action(run)
            return {'run': run}
        return node

    actions = {
        'event_planner': session._graph_event_plan,
        'event_writer': session._graph_event_writer,
        'event_commit': session._graph_event_commit,
        'legacy_planner': session._graph_legacy_plan,
        'legacy_writer': session._graph_legacy_writer,
        'legacy_commit': session._graph_legacy_commit,
        'memory': lambda run: session.attempt_memory(run['trace']),
        'reviewer': lambda run: session._review_pending(run['trace']),
    }
    for name, action in actions.items():
        graph.add_node(name, phase(name, action))
    def entry(state):
        if state['run'].get('recovery_only'):
            return 'recover'
        return 'event' if session.plan.get('event_first', True) else 'legacy'

    graph.add_conditional_edges(START, entry,
        {'event': 'event_planner', 'legacy': 'legacy_planner', 'recover': 'memory'})
    graph.add_edge('event_planner', 'event_writer')
    graph.add_conditional_edges('event_writer',
        lambda state: 'revise' if state['run']['revision_requested'] else 'save',
        {'revise': 'event_planner', 'save': 'event_commit'})
    graph.add_edge('legacy_planner', 'legacy_writer')
    graph.add_edge('legacy_writer', 'legacy_commit')
    for name in ('event_commit', 'legacy_commit'):
        graph.add_edge(name, 'memory')
    graph.add_edge('memory', 'reviewer')
    graph.add_edge('reviewer', END)
    return graph.compile(name='tome_longform_writing')
