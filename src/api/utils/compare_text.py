def clear_text(text):
    text = text.lower()
    text = text.replace('\n', '')
    text = text.replace('.', ' ')
    text = text.replace(',', ' ')
    text = text.replace('?', ' ')
    text = text.replace('!', ' ')
    text = text.replace('   ', ' ')
    text = text.replace('  ', ' ')

    return text


def compare_text(text_1, text_2):
    text_1 = clear_text(text_1)
    text_2 = clear_text(text_2)

    if text_1 == text_2:
        return True
    return False


def compare_files(file_name_1, file_name_2):
    text_1 = ''
    with open(file_name_1, 'r') as file:
        text_1 = file.read()

    text_2 = ''
    with open(file_name_1, 'r') as file:
        text_2 = file.read()

    res = compare_text(text_1, text_2)
    print(res)


if __name__ == '__main__':
    file_name_1 = '/my/src/retolu_back/public/media/stt/text_from_json.txt'
    file_name_2 = '/my/src/retolu_back/public/media/stt/chat_gpt_answer_mini.txt'

    compare_files(file_name_1, file_name_2)
