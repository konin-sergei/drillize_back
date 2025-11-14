import difflib


def get_diff():
    text = "nuclear 2family this a great      of "
    words = "nuclear 1family this   great that of" # -- main v
    #    nuclear 40 family this a great chunk of the unit some think that
    # Разбиваем строки на слова
    text = text.split()
    words2 = words.split()

    # Создаем объект SequenceMatcher
    matcher = difflib.SequenceMatcher(None, text, words2)

    res = []


    # Получаем различия и объединяем массивы
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # Заменяем элементы из words1 на элементы из words2
            res.extend(words2[j1:j2])
        elif tag == 'delete':
            # Сохраняем удаленные элементы из words1
            res.extend(text[i1:i2])
        elif tag == 'insert':
            # Вставляем элементы из words2
            res.extend(words2[j1:j2])
        elif tag == 'equal':
            # Добавляем элементы из words1 (они совпадают с words2)
            res.extend(text[i1:i2])

    print(text)
    print(words)
    print(' '.join(res))


if __name__ == '__main__':
    get_diff()
