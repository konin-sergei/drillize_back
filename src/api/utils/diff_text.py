import difflib
import json


def clear_text(text):
    replace_chars = str.maketrans(",:;-.?!", "       ")
    text = text.translate(replace_chars)
    text = text.replace('%', ' percent ')
    text = text.lower()
    # Удаляем лишние пробелы и обрезаем пробелы по краям
    text = " ".join(text.split())
    return text


def get_diff(file_transcribe):
    with open(file_transcribe, 'r') as file:
        data_transcribe = json.load(file)

    transcribe_text = data_transcribe['text']
    transcribe_words = data_transcribe['words']

    # Разбиваем строки на слова
    transcribe_text = clear_text(transcribe_text)
    ls_text = transcribe_text.split()

    ls_words = []
    for word in transcribe_words:
        ls_words.append(word['word'])

    total_ls_words = ' '.join(ls_words)
    total_ls_words = clear_text(total_ls_words)
    ls_words = total_ls_words.split()

    ls_text = ls_text[130:140]
    ls_words = ls_words[130:140]

    print(' '.join(ls_text))
    print(' '.join(ls_words))

    # Создаем объект SequenceMatcher
    matcher = difflib.SequenceMatcher(None, ls_text, ls_words)

    res = []

    # Получаем различия и объединяем массивы
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # Заменяем элементы из ls_text на элементы из ls_words
            print('Заменяем элементы из ls_text на элементы из ls_words')
            print(ls_words[j1:j2])
            res.extend(ls_words[j1:j2])
        elif tag == 'delete':
            # Сохраняем удаленные элементы из ls_text
            print('Сохраняем удаленные элементы из ls_text')
            print(ls_text[i1:i2])
            res.extend(ls_text[i1:i2])
        elif tag == 'insert':
            # Вставляем элементы из ls_words
            print('Вставляем элементы из ls_words')
            print(ls_words[j1:j2])
            res.extend(ls_words[j1:j2])
        elif tag == 'equal':
            # Добавляем элементы из ls_text (они совпадают с ls_words)
            res.extend(ls_text[i1:i2])

    # print("Объединенный массив:", res)


if __name__ == '__main__':
    file_transcribe = '/Users/admin/my/src/retolu_back/public/media/files/lessons/5/transcribe_audio.json'
    get_diff(file_transcribe)
