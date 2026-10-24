"""Shared storage identifiers; display labels remain separate and unchanged."""
import hashlib
import re


def attribute_identifier(value):
    if not isinstance(value,str) or not value.strip():return value
    if re.fullmatch(r'[a-z][a-z0-9_]{0,63}',value):return value
    if re.fullmatch(r'[0-9][a-z0-9_]{0,57}',value):return 'field_'+value
    return 'field_'+hashlib.sha256(value.encode('utf-8')).hexdigest()[:32]


def record_identifier(value):
    if not isinstance(value,str) or not value.strip():
        from inf_writer.domain import ContractError
        raise ContractError('Record identifier must be nonempty text')
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',value):return value
    return 'id_'+hashlib.sha256(value.encode('utf-8')).hexdigest()[:32]
