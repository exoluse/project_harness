"""Stable facade for governed canonical mutations.

Authority boundaries live in dedicated modules: transaction integrity,
evidence attachment, and lifecycle transition policy.
"""

from .evidence_mutations import record_evidence
from .lifecycle_mutations import transition_project, transition_record
from .mutation_service import AtomicMutationService

__all__ = [
    "AtomicMutationService",
    "record_evidence",
    "transition_project",
    "transition_record",
]
