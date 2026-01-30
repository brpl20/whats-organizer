"""
Integration test: runs convert_opus_to_mp3 on a directory with .opus files.
Tests the full pipeline: opus -> mp3 (ffmpeg) -> Groq/OpenAI transcription.

Usage:
    python scripts/test_transcription.py [path_to_dir_with_opus_files]
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils.converter_mp3 import convert_opus_to_mp3
from src.utils.config import config

DEFAULT_TEST_DIR = os.path.join(
    os.path.dirname(__file__), "..",
    "zip_tests", "20260129_143918_433308_processing_1954dec8"
)


def main():
    test_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_DIR
    test_dir = os.path.abspath(test_dir)

    print("=" * 60)
    print("  Teste de transcrição end-to-end")
    print("=" * 60)
    print()
    print(f"Diretório: {test_dir}")
    print(f"Provider primário: {'Groq' if config.WHISPER_GROQ else 'OpenAI'}")
    print(f"Fallback:          {'OpenAI' if config.WHISPER else 'Nenhum'}")
    print(f"Idioma:            {config.WHISPER_LANG}")
    print()

    opus_files = [f for f in os.listdir(test_dir) if f.endswith('.opus')]
    print(f"Arquivos .opus encontrados: {len(opus_files)}")
    for f in opus_files:
        size_kb = os.path.getsize(os.path.join(test_dir, f)) / 1024
        print(f"  - {f} ({size_kb:.1f} KB)")
    print()

    print("Iniciando transcrição...")
    print("-" * 60)
    results = convert_opus_to_mp3(test_dir)
    print("-" * 60)
    print()

    print(f"Resultados ({len(results)} transcrições):")
    print()
    for r in results:
        status = "✅" if r['Transcription'] else "❌ (vazio)"
        print(f"  {status} {r['FileName']}")
        if r['Transcription']:
            print(f"     → {r['Transcription'][:120]}")
        print()

    print("=" * 60)
    ok = sum(1 for r in results if r['Transcription'])
    print(f"  {ok}/{len(results)} transcrições com sucesso")
    print("=" * 60)


if __name__ == "__main__":
    main()
