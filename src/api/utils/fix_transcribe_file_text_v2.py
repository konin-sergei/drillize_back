import difflib
import json
from copy import deepcopy

from src.api.utils.clear_utils import clear_text_ls


def align_texts_and_words(text, words):
    """
    Иногда text не совпадает с words[audio time] и нужно это выровнять
    """

    # Разбиваем строки на слова
    text_ls = text.split()

    words = [x for x in words if x['word'] != '']

    # words_text = ' '.join([x['word'] for x in words])
    # words_ls = words_text.split()
    words_ls = [x['word'] for x in words]

    text_ls_clear = clear_text_ls(text_ls)
    words_text_ls_clear = clear_text_ls(words_ls)

    # Создаём объект SequenceMatcher для сравнения списков слов
    matcher = difflib.SequenceMatcher(None, text_ls_clear, words_text_ls_clear)

    new_text_ls = []
    steps = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Для совпадающих слов выводим каждое слово отдельно
            for word in text_ls[i1:i2]:
                steps.append(f"Оставить слово '{word}'")
                new_text_ls.append(word)
        elif tag == 'delete':
            # Для удаляемых слов выводим действие для каждого слова
            for word in text_ls[i1:i2]:
                steps.append(f"Удалить слово '{word}'")
        elif tag == 'insert':
            # Для вставляемых слов выводим действие для каждого слова
            for word in words_ls[j1:j2]:
                steps.append(f"Вставить слово '{word}'")
                if not word:
                    word = '_'
                new_text_ls.append(word)
        elif tag == 'replace':
            # В случае замены сравним количество слов
            old_words = text_ls[i1:i2]
            new_words = words_ls[j1:j2]
            if len(old_words) == len(new_words):
                # Если количество совпадает – заменяем слово на слово
                for old, new in zip(old_words, new_words):
                    steps.append(f"Заменить слово '{old}' на '{new}'")
                    if not new:
                        new = old
                    new_text_ls.append(new)
            else:
                # Если количество различается – сначала удаляем старые, затем вставляем новые слова
                for word in old_words:
                    steps.append(f"Удалить слово '{word}'")
                for word in new_words:
                    steps.append(f"Вставить слово '{word}'")
                    if not word:
                        word = '_'
                    new_text_ls.append(word)

    # Выводим шаги с нумерацией
    show_step = False
    if show_step == True:
        for idx, step in enumerate(steps, start=1):
            print(f"Шаг {idx}: {step}")

    if len(new_text_ls) != len(words):
        print('Error length fix text')

    new_words = deepcopy(words)
    for i, word in enumerate(new_text_ls):
        new_words[i]['word'] = new_text_ls[i]

    new_text = ' '.join(new_text_ls)

    return new_text, new_words


def fix_transcribe_file_text(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    text = data['text']
    words = data['words']

    new_text, new_words = align_texts_and_words(text, words)

    data['text'] = new_text
    data['words'] = new_words

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    file_name = '/Users/admin/my/src/retolu_back/public/media/files/lessons/5_30/transcribe_audio.json.source'
    fix_transcribe_file_text(file_name)
