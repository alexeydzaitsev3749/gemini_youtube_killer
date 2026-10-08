#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gemini_youtube_killer.py

Отбойный молоток: удаляет из лога Gemini (AI Studio) ВСЕ вложения YouTube
(чанки youtubeVideo) на месте (in-place, r+). Без параметров, кроме имени файла.

Зачем: закрытый или удалённый ролик валит любой запрос к чату
(internal error), хотя сам чат открывается нормально.

Использование:
    python gemini_youtube_killer.py <путь_к_логу.json>

Удалённые чанки дописываются в <лог>_youtube.json (до правки основного файла).
"""

import json
import os
import sys


def kill_all_youtube(filepath):
    with open(filepath, 'r+', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] Ошибка: Файл '{filepath}' не является валидным JSON. {e}", file=sys.stderr)
            return

        if 'chunkedPrompt' not in data or 'chunks' not in data['chunkedPrompt']:
            print("[!] Ошибка: JSON не содержит структуры 'chunkedPrompt.chunks'.", file=sys.stderr)
            return

        chunks = data['chunkedPrompt']['chunks']
        removed = [{"chunkIndex": i, "chunk": c} for i, c in enumerate(chunks) if 'youtubeVideo' in c]

        if not removed:
            print("[*] Роликов YouTube в логе нет. Файл не изменен.")
            return

        # Сначала сохраняем вырезанное (дописываем, если файл уже есть)
        base, ext = os.path.splitext(filepath)
        side = f"{base}_youtube{ext}"
        if os.path.exists(side):
            with open(side, 'r', encoding='utf-8') as sf:
                removed = json.load(sf) + removed
        with open(side, 'w', encoding='utf-8') as sf:
            json.dump(removed, sf, indent=2, ensure_ascii=False)

        kept = [c for c in chunks if 'youtubeVideo' not in c]
        killed = len(chunks) - len(kept)
        data['chunkedPrompt']['chunks'] = kept

        out = json.dumps(data, indent=2, ensure_ascii=False)
        f.seek(0)
        f.write(out)
        f.truncate()
        print(f"[+] Удалено роликов: {killed}, осталось чанков: {len(kept)}. Копия: '{side}'")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python gemini_youtube_killer.py <путь_к_логу.json>", file=sys.stderr)
        sys.exit(1)
    kill_all_youtube(sys.argv[1])
