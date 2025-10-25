from typing import cast
import music21
import numpy as np
import wave

from services.utils.path import get_cache_file_path


def cache_abc_to_file(abc_notation: str | None) -> str:
    if abc_notation is None:
        raise ValueError("No content to save")

    file_path = get_cache_file_path(f"abc.abc")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(abc_notation)

    return abc_notation


def write_abc_notation_to_file(abc_notation: str | None) -> str:
    if abc_notation is None:
        raise ValueError("No content to save")
    try:
        file_path = get_cache_file_path(f"music.mid")
        score = music21.stream.Score()
        tune = cast(
            music21.stream.Score, music21.converter.parse(abc_notation, format="abc")
        )
        for part in tune.parts:
            print(f"Voice ID: {part.id}")
        score.insert(0, tune)
        score.write("midi", fp=file_path)
        return file_path
    except Exception as e:
        raise ValueError(f"Failed to write ABC notation to file: {str(e)}")


def midi_to_chiptune_wav(midi_path: str) -> str:
    try:
        # Load MIDI file
        score = music21.converter.parse(midi_path)

        # Get tempo
        tempos = score.flat.getElementsByClass(music21.tempo.MetronomeMark)
        tempo = tempos[0].number if tempos else 120
        quarter_duration = 60 / tempo

        # Extract notes
        notes = []
        for element in score.flat.notes:
            if isinstance(element, music21.note.Note):
                notes.append(
                    {
                        "pitch": element.pitch.frequency,
                        "start": element.offset,
                        "duration": element.duration.quarterLength,
                        "velocity": element.volume.velocity if element.volume else 64,
                    }
                )
            # Skip chords for simplicity

        # Audio parameters
        sample_rate = 44100
        max_time = (
            max((note["start"] + note["duration"]) * quarter_duration for note in notes)
            if notes
            else 0
        )
        total_samples = int(max_time * sample_rate) + 1
        audio = np.zeros(total_samples, dtype=np.float32)

        # Generate audio for each note
        for note in notes:
            freq = note["pitch"]
            start_sample = int(note["start"] * quarter_duration * sample_rate)
            duration_samples = int(note["duration"] * quarter_duration * sample_rate)
            end_sample = min(start_sample + duration_samples, total_samples)

            if freq > 0:  # Avoid zero frequency
                t = np.arange(end_sample - start_sample) / sample_rate
                # Square wave
                wave_data = np.sign(np.sin(2 * np.pi * freq * t)) * (
                    note["velocity"] / 127.0
                )
                audio[start_sample:end_sample] += wave_data

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8

        # Convert to int16
        audio_int = (audio * 32767).astype(np.int16)

        # Write WAV file
        wav_path = get_cache_file_path("chiptune.wav")
        with wave.open(wav_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int.tobytes())

        return wav_path
    except Exception as e:
        raise ValueError(f"Failed to convert MIDI to chiptune WAV: {str(e)}")
