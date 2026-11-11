"""
Unit Tests for Audio Dictation, Speaker Diarisation, and Person Tagging.

Verifies acoustic feature extraction, speaker turn clustering, tag updates,
and institutional attendance note synthesis.
"""

import json
from pathlib import Path
import numpy as np
import pytest

from app.audio import AudioDiarisationEngine, SpeechTurn


def test_acoustic_feature_extraction(tmp_path: Path):
    """Verify spectral centroid, zero-crossing rate, and RMS energy."""
    engine = AudioDiarisationEngine(storage_dir=tmp_path / "dictations")
    sr = 16000
    t = np.linspace(0, 1, sr, endpoint=False)

    # 150 Hz pure tone (low pitch voice).
    low_voice = 0.5 * np.sin(2 * np.pi * 150 * t).astype(np.float32)
    feats_low = engine._extract_acoustic_features(low_voice, sample_rate=sr)

    # 350 Hz pure tone (higher pitch voice).
    high_voice = 0.5 * np.sin(2 * np.pi * 350 * t).astype(np.float32)
    feats_high = engine._extract_acoustic_features(high_voice, sample_rate=sr)

    assert len(feats_low) == 3
    assert len(feats_high) == 3
    # Spectral centroid for higher voice must exceed lower voice.
    assert feats_high[0] > feats_low[0]


def test_speaker_clustering(tmp_path: Path):
    """Verify speaker turn partitioning across two distinct voices."""
    engine = AudioDiarisationEngine(storage_dir=tmp_path / "dictations")

    # Feature vectors for 2 turns of Speaker A, 2 turns of Speaker B.
    speaker_a_features = [
        np.array([150.0, 10.0, 5.0]),
        np.array([155.0, 11.0, 5.2]),
    ]
    speaker_b_features = [
        np.array([350.0, 25.0, 4.8]),
        np.array([360.0, 24.0, 4.9]),
    ]
    all_features = [
        speaker_a_features[0],
        speaker_b_features[0],
        speaker_a_features[1],
        speaker_b_features[1],
    ]

    assignments = engine._cluster_speakers(all_features, max_speakers=2)
    assert len(assignments) == 4
    # Turns 0 and 2 must match (Speaker 1); Turns 1 and 3 must match (Speaker 2).
    assert assignments[0] == assignments[2]
    assert assignments[1] == assignments[3]
    assert assignments[0] != assignments[1]


def test_tag_speakers_and_generate_note(tmp_path: Path):
    """Verify person tagging and attendance note generation."""
    storage = tmp_path / "dictations"
    storage.mkdir(parents=True, exist_ok=True)
    engine = AudioDiarisationEngine(storage_dir=storage)

    dictation_id = "dictation_20261111_test"
    sample_data = {
        "dictation_id": dictation_id,
        "file_name": "conference_call.wav",
        "duration_seconds": 120.0,
        "duration_display": "02:00",
        "language": "en",
        "speakers_detected": ["Speaker 1", "Speaker 2"],
        "speech_turns": [
            {
                "start": 0.0,
                "end": 15.0,
                "timestamp_display": "00:00 - 00:15",
                "speaker_id": "Speaker 1",
                "speaker_name": "Speaker 1",
                "speaker_role": "Participant",
                "text": "Good morning Neville, we need advice on the contract.",
                "confidence": 0.95,
            },
            {
                "start": 16.0,
                "end": 35.0,
                "timestamp_display": "00:16 - 00:35",
                "speaker_id": "Speaker 2",
                "speaker_name": "Speaker 2",
                "speaker_role": "Participant",
                "text": "The statutory limitation deadline expires in 30 days.",
                "confidence": 0.98,
            },
        ],
        "created_at": "2026-11-11T01:00:00Z",
    }
    (storage / f"{dictation_id}.json").write_text(
        json.dumps(sample_data, indent=2), encoding="utf-8"
    )

    # Apply person tagging.
    tag_mapping = {
        "Speaker 1": {
            "name": "William McAdam",
            "role": "Instructing Solicitor",
        },
        "Speaker 2": {
            "name": "Neville (Counsel)",
            "role": "Barrister",
        },
    }
    updated = engine.tag_speakers(dictation_id, tag_mapping)

    turns = updated["speech_turns"]
    assert turns[0]["speaker_name"] == "William McAdam"
    assert turns[0]["speaker_role"] == "Instructing Solicitor"
    assert turns[1]["speaker_name"] == "Neville (Counsel)"
    assert turns[1]["speaker_role"] == "Barrister"

    # Synthesise Attendance Note.
    note = engine.generate_attendance_note(
        dictation_id, matter_title="Corringham Settlement Advice"
    )
    assert "Chambers Attendance Note: Corringham Settlement Advice" in note
    assert "William McAdam" in note
    assert "Instructing Solicitor" in note
    assert "Neville (Counsel)" in note
    assert "The statutory limitation deadline expires in 30 days." in note
    assert "UK GDPR" in note
