import difflib
import json
from copy import deepcopy
from pprint import pprint

from src.api.utils.clear_text import clear_text_ls


def align_texts_and_words(text1, text2, words):
    print(text1)
    print(text2)

    words1 = text1.split()
    words2 = text2.split()

    words1_clear = clear_text_ls(words1)
    words2_clear = clear_text_ls(words2)

    matcher = difflib.SequenceMatcher(None, words1_clear, words2_clear)

    modified_text1 = words1[:]  # Копируем text1
    modified_words = deepcopy(words)  # Копируем `words`, чтобы не менять оригинал

    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        if tag == 'equal':
            # Обновляем слова в структуре `words` вместо списка
            for k in range(i2 - i1):
                modified_words[j1 + k]['word'] = words1[i1 + k]
        elif tag == 'delete':
            # Вставляем удаленные слова в `words` как словари
            for k in range(i2 - 1, i1 - 1, -1):
                modified_words.insert(j1, {'word': words1[k], 'start': None, 'end': None})
        elif tag == 'insert':
            # Вставляем недостающие слова в text1
            for k in range(j2 - 1, j1 - 1, -1):
                modified_text1.insert(i1, words2[k])
        elif tag == 'replace':
            # Заменяем слова в `words` напрямую
            for k in range(min(i2 - i1, j2 - j1)):
                modified_words[j1 + k]['word'] = words1[i1 + k]
            if i2 - i1 > j2 - j1:
                for k in range(i1 + (j2 - j1), i2):
                    modified_words.insert(j1 + (j2 - j1), {'word': words1[k], 'start': None, 'end': None})
            elif j2 - j1 > i2 - i1:
                del modified_words[j1 + (i2 - i1):j2]

    new_text1 = " ".join(modified_text1)
    new_text2 = " ".join([w['word'] for w in modified_words])  # Собираем текст обратно

    return new_text1, new_text2, modified_words


def fill_missing_timestamps(words):
    last_start = 0
    last_end = 0

    for word in words:
        # Если start == None, подставляем предыдущее значение
        if word['start'] is None:
            word['start'] = last_start
        else:
            last_start = word['start']  # Обновляем последнее известное start

        # Если end == None, подставляем предыдущее значение
        if word['end'] is None:
            word['end'] = last_end
        else:
            last_end = word['end']  # Обновляем последнее известное end

    return words


def fix_transcribe_file_text(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    text = data['text']
    words = data['words']

    words_text = ' '.join([x['word'] for x in words])

    new_text, new_words_text, updated_words = align_texts_and_words(text, words_text, words)

    updated_words = fill_missing_timestamps(updated_words)

    # print(f"Updated text1: {new_text}")
    # print(f"Updated text2: {new_text}")
    # pprint(updated_words)

    data['text'] = new_text
    data['words'] = updated_words

    # with open(file_name, "w", encoding="utf-8") as file:
    #     json.dump(data, file, ensure_ascii=False, indent=4)


def check():
    # Пример:
    text = 'I On Ona! Have. good% gg Car'

    words = [
        {'word': 'have', 'start': 0, 'end': 2.12354},
        {'word': 'a', 'start': 2.21342345, 'end': 3.124423},
        {'word': 'good', 'start': 2.21342345, 'end': 3.124423},

        {'word': 'car', 'start': 5.9235, 'end': 6.124},
    ]
    words_text = ' '.join([x['word'] for x in words])

    new_text, new_words_text, updated_words = align_texts_and_words(text, words_text, words)

    updated_words = fill_missing_timestamps(updated_words)

    print(f"Updated text1: {new_text}")
    print(f"Updated text2: {new_text}")
    pprint(updated_words)


if __name__ == '__main__':
    file_name = '/Users/admin/my/src/retolu_back/public/media/files/lessons/5_02/transcribe_audio_source.json'
    fix_transcribe_file_text(file_name)

    # check()