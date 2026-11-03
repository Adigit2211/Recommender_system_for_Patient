"""What a patient profile looks like.

The allowed values are fixed on purpose: a misspelt sensitivity is rejected with an error,
instead of being silently ignored."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

DiagnosisContext = Literal[
    "pediatric_oncology", "adult_oncology", "chronic_pediatric_illness", "general_inpatient", "other"
]
TreatmentPhase = Literal["active_high_fatigue", "active_nausea", "post_treatment_recovery", "stable"]
Sensitivity = Literal[
    "photosensitive_seizure_trigger", "grief_sensitive", "anxiety_sensitive",
    "needs_subtitles", "needs_audio_description",
]


class PatientProfile(BaseModel):
    age: int = Field(..., ge=0, le=120)
    diagnosis_context: DiagnosisContext
    treatment_phase: TreatmentPhase
    known_sensitivities: List[Sensitivity] = Field(default_factory=list)
    preferred_genres: List[str] = Field(default_factory=list)
    # optional
    preferred_tones: List[str] = Field(default_factory=list)
    liked_titles: List[str] = Field(default_factory=list)
    diversity_rerank: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 9,
                "diagnosis_context": "pediatric_oncology",
                "treatment_phase": "active_high_fatigue",
                "known_sensitivities": ["photosensitive_seizure_trigger"],
                "preferred_genres": ["Comedy", "Animation"],
            }
        }
    }
