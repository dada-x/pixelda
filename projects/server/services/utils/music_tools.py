import os
from typing import cast
import music21
from symusic import Score, Synthesizer, dump_wav
from symusic.core import ScoreQuarter

from services.utils.path import get_cache_file_path


def get_music_cache_file_path(file_name: str) -> str:
    return get_cache_file_path(file_name, subfolder="music")


def cache_abc_to_file(abc_notation: str) -> str:
    file_path = get_music_cache_file_path("abc.abc")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(abc_notation)
    return abc_notation


def to_original_wav(abc_notation: str) -> str:
    try:
        score = Score.from_abc(abc_notation, ttype="tick")
        score = cast(ScoreQuarter, score)
        audio = Synthesizer().render(score, True)

        filePath = get_music_cache_file_path("original.wav")
        dump_wav(filePath, audio, sample_rate=44100, use_int16=True)
        return filePath
    except Exception as e:
        raise ValueError(f"Failed to convert ABC to original WAV: {str(e)}")


def to_chiptune_wav(abc_notation: str) -> str:
    try:
        score = Score.from_abc(abc_notation, ttype="tick")
        score = cast(ScoreQuarter, score)
        audio = Synthesizer(
            sf_path=os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "8bit.sf2"
            )
        ).render(score, True)

        filePath = get_music_cache_file_path("chiptune.wav")
        dump_wav(filePath, audio, sample_rate=44100, use_int16=True)
        return filePath
    except Exception as e:
        raise ValueError(f"Failed to convert ABC to chiptune WAV: {str(e)}")
