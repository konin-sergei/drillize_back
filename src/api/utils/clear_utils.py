from copy import deepcopy


def clear_text(text):
    replace_chars = str.maketrans(",:;-.?!'", "        ")
    text = text.translate(replace_chars)
    text = text.replace('"', ' ')
    text = text.replace('%', ' ')
    text = text.replace('$', ' ')
    text = text.replace('£', ' ')
    text = text.replace('€', ' ')
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')

    text = text.lower()
    text = " ".join(text.split())
    return text


def clear_text_ls(source_ls):
    ls = deepcopy(source_ls)
    for i, item in enumerate(ls):
        ls[i] = clear_text(item)
    return ls