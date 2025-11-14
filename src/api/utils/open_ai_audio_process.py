# /src/api/utils/open_ai_audio_process.py

import os
import sys

from nltk.tokenize import sent_tokenize

from src.api.utils.clear_utils import clear_text
from src.api.utils.fix_transcribe_file_text_v2 import fix_transcribe_file_text

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
print(folder)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import json
import os
import shutil
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment

from src.config import settings

track_id = 0


# STEP 1
def correct_transcribe_text(file_name_tts):  # not use
    with open(file_name_tts, 'r') as file:
        data = json.load(file)
    transcribe_text = data['text']
    transcribe_words = data['words']

    # normalize text
    words = []
    for x in transcribe_words:
        word_info = {
            'word': x['word'].lower(),
            'start': x['start'],
            'end': x['end']
        }
        words.append(word_info)

    transcribe_text = clear_text(transcribe_text)

    words_total = ''
    for word in words:
        if words_total:
            words_total += ' '
        words_total += word['word']

    print(transcribe_text)
    print(words_total)


def open_ai_transcribe_audio(file_name: str, lesson_id: int) -> str:
    """
    Transcribe audio file
    """
    print('Start transcribe audio')
    if settings.OPENAI_KEY == "":
        print('Error set env!')

    client = OpenAI(api_key=settings.OPENAI_KEY, organization=settings.OPENAI_ORGANIZATION)

    audio_file = open(file_name, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en",
        timestamp_granularities=["word"],
        response_format="verbose_json"
    )

    transcript_dict = transcript.to_dict()

    print('FOR DEBUG')
    folder = os.path.join(settings.UPLOAD_DIRECTORY, "files", "lessons", str(lesson_id))
    Path(folder).mkdir(parents=True, exist_ok=True)

    file_name_relative = os.path.join("files", "lessons", str(lesson_id), 'transcribe_audio.json')
    file_name_tts = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)

    with open(file_name_tts, "w", encoding="utf-8") as file:
        json.dump(transcript_dict, file, ensure_ascii=False, indent=4)

    with open(f'{file_name_tts}.source', "w", encoding="utf-8") as file:
        json.dump(transcript_dict, file, ensure_ascii=False, indent=4)

    print('Finish open_ai_transcribe_audio')
    print('file_transcribe=', file_name_tts)
    return file_name_tts


# STEP 2
def open_ai_split_text(file_name: str, lesson_id: int) -> str:
    """
    Split text on sentences
    """

    with open(file_name, 'r') as file:
        data = json.load(file)
    text = data['text']

    client = OpenAI(api_key=settings.OPENAI_KEY, organization=settings.OPENAI_ORGANIZATION)

    promt = f"""I am learning English.
    Divide the text into simple phrases for studying and memorizing.
    Phrases should be short.
    Mandatory condition - do not change the content of the text (do not correct grammar, do not delete, do not change words, keep various numbers, symbols and other text data).
    The total number of words (including various numbers, symbols) should be the same as in the original text.
    The text should not be divided into any additional blocks.
    Try to avoid making a phrase consisting of one word.
    If possible, try not to make phrases longer than 10 words.
    The response format should be JSON: {{"phrases": ["Phrase 1?", "Phrase 2."]}}.
    Text:
    {text}"""

    # model = "gpt-3.5-turbo"
    # model = "gpt-4o"
    model = "gpt-4o-mini"

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": promt
            }
        ],
        response_format={"type": "json_object"}

    )

    res = completion.choices[0].message
    content = res.content

    json_data = json.loads(content)

    # check if change text
    text_split = ' '.join(json_data['phrases'])
    text_split_clear = clear_text(text_split)
    text_clear = clear_text(text)
    if len(text_split_clear) != len(text_clear):
        return '', 'Not check text'

    file_name_relative = os.path.join("files", "lessons", str(lesson_id), 'split_text_source.json')
    file_name = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

    print('Finish open_ai_split_text')
    print('file_split_text=', file_name)
    return file_name, ''


def standard_split_text(file_name: str, lesson_id: int) -> str:
    """
    Split text on sentences
    """

    with open(file_name, 'r') as file:
        data = json.load(file)
    text = data['text']

    # on prod
    # try:
    #     _create_unverified_https_context = ssl._create_unverified_context
    # except AttributeError:
    #     pass
    # else:
    #     ssl._create_default_https_context = _create_unverified_https_context
    # nltk.download()

    # todo сделать руками разделение с учетом 1. Hello world 2. Hello world  a. Hello world b. Hello world mr.Doctor  dr. Doctor e.c. 4.12
    # for sep in [". ", "? ", "! ", "A. "B "1. 2.]:
    #     text = text.replace(sep, "|")
    # result = [s.strip() for s in text.split("|") if s.strip()]

    sentences = sent_tokenize(text, language="english")

    json_data = {'phrases': sentences}
    file_name_relative = os.path.join("files", "lessons", str(lesson_id), 'split_text_source.json')
    file_name = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

    print('Finish open_ai_split_text')
    print('file_split_text=', file_name)
    return file_name


# STEP 3
# TRANSLATE TO RUSSIAN
def open_ai_translate(file_name: str, lesson_id: int) -> str:
    """
    Translate each sentence
    """

    with open(file_name, 'r') as file:
        data = json.load(file)
    text = data['phrases']

    client = OpenAI(api_key=settings.OPENAI_KEY, organization=settings.OPENAI_ORGANIZATION)

    text_encode = json.dumps(text, indent=4)

    content = f"""Translate this text into Russian language.
    The response format must be json like - {{"phrases": ["Sentence 1.", "Sentence 2."]}}.
    Text:
    {{"phrases": {text_encode}}}
    """

    # model = "gpt-3.5-turbo"
    # model = "gpt-4o"
    model = "gpt-4o-mini"

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": content
            }
        ],
        response_format={"type": "json_object"}
    )

    res = completion.choices[0].message
    content = res.content

    json_data = json.loads(content)
    file_name_relative = os.path.join("files", "lessons", str(lesson_id), 'split_text_translate.json')
    file_name = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

    print('Finish open_ai_translate')
    print('file_translation=', file_name)
    return file_name


# STEP 4
def open_ai_tts_translation(file_name: str, lesson_id: int) -> str:
    """
    Make mp3 files from russian sentences
    """

    with open(file_name, 'r') as file:
        data = json.load(file)
    texts = data['phrases']

    client = OpenAI(api_key=settings.OPENAI_KEY, organization=settings.OPENAI_ORGANIZATION)

    folder_relative = os.path.join("files", "lessons", str(lesson_id), "split_audio_translate")
    folder = os.path.join(settings.UPLOAD_DIRECTORY, folder_relative)

    if os.path.exists(folder):
        shutil.rmtree(folder)

    Path(folder).mkdir(parents=True, exist_ok=True)

    language = "Russian"

    for index, text in enumerate(texts):
        input_text = f"[in {language}] {text}"

        response = client.audio.speech.create(
            model="tts-1",
            # model="tts-1-hd",
            voice="alloy",
            input=input_text,
        )
        file_name = f"{folder}/{index}.mp3"
        response.write_to_file(file_name)

    print('Finish step text to speach translation')
    print('folder_audio_translation=', folder)
    return folder


# STEP 5
def get_split_text_timing(file_transcribe, file_split_text, lesson_id):
    """
    Get timing from splitting sentences
    """

    with open(file_transcribe, 'r') as file:
        data_transcribe = json.load(file)

    with open(file_split_text, 'r') as file:
        data_split_text = json.load(file)

    source_words = data_transcribe['words']
    source_phrases = data_split_text['phrases']
    total_phrases = " ".join(source_phrases)
    total_words = ' '.join(x['word'] for x in source_words)

    if total_words != total_phrases:
        print(90 * '-')
        print('total_words != total_phrases')
        print(90 * '-')

    words = source_words
    phrases = [x.split() for x in source_phrases]

    # Формируем список из предложений с временами начала и конца
    sentences = []
    i_word = 0
    for i_phrase, phrase_words in enumerate(phrases):
        sentence = []
        for i_phrase_word, phrase_word in enumerate(phrase_words):
            word = words[i_word]['word']
            if phrase_word != word:
                print('Error text phrase_word != word identical after fix text function')
            sentence.append(words[i_word])
            i_word += 1
        sentences.append(sentence)

    sentences_timing = []
    for i, sentence in enumerate(sentences):
        sentences_timing.append((sentence[0]['start'], sentence[-1]['end']))

    # Список с добавленными началами и концами соседних предложений
    sentences_timing_extend = []

    for i in range(len(sentences_timing)):
        if i == 0:
            # Для первой строки:
            # Берём первый элемент первого подсписка дважды, затем второй элемент первого подсписка
            # и первый элемент второго подсписка
            if len(sentences_timing) == 1:
                row = [sentences_timing[0][0], sentences_timing[0][0], sentences_timing[0][1], sentences_timing[0][1]]
            else:
                row = [sentences_timing[0][0], sentences_timing[0][0], sentences_timing[0][1], sentences_timing[1][0]]
        elif i < len(sentences_timing) - 1:
            # Для строк со 2-й по предпоследнюю:
            # Первый элемент строки – это второй элемент предыдущего подсписка,
            # затем первый и второй элементы текущего подсписка,
            # и первый элемент следующего подсписка.
            row = [sentences_timing[i - 1][1], sentences_timing[i][0], sentences_timing[i][1], sentences_timing[i + 1][0]]
        else:
            # Для последней строки:
            # Первый элемент – второй элемент предпоследнего подсписка,
            # затем первый и второй элементы последнего подсписка,
            # и в конце повторяем второй элемент последнего подсписка.
            row = [sentences_timing[i - 1][1], sentences_timing[i][0], sentences_timing[i][1], sentences_timing[i][1]]

        sentences_timing_extend.append(row)

    # Адаптируем начала и концы предложений
    sentences_timing_adjust = []
    for i in range(len(sentences_timing_extend)):
        start_prev = sentences_timing_extend[i][0]
        start_cur = sentences_timing_extend[i][1]
        start = (start_prev + start_cur) / 2
        end_prev = sentences_timing_extend[i][2]
        end_cur = sentences_timing_extend[i][3]
        end = (end_prev + end_cur) / 2
        row = (start, end)
        sentences_timing_adjust.append(row)

    file_name_relative = os.path.join("files", "lessons", str(lesson_id), 'split_text_source_timing.json')
    file_name = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(sentences_timing_adjust, file, ensure_ascii=False, indent=4)

    print('Finish step get_file_split_text_timing')
    print('file_split_text_timing=', file_name)
    return file_name


# STEP 6
def split_main_audio(file_audio, file_split_text_timing, lesson_id):
    """
    Split main audio file base on split sentences
    """

    # Загрузка MP3-файла
    audio = AudioSegment.from_mp3(file_audio)

    folder_relative = os.path.join("files", "lessons", str(lesson_id), "split_audio_source")
    folder = os.path.join(settings.UPLOAD_DIRECTORY, folder_relative)

    if os.path.exists(folder):
        shutil.rmtree(folder)

    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(file_split_text_timing, 'r') as file:
        split_text_timing = json.load(file)

    # Разделение и сохранение фрагментов
    for i, (start, end) in enumerate(split_text_timing):
        segment = audio[int(start * 1000):int(end * 1000)]  # Перевод в миллисекунды
        segment.export(f"{folder}/{i}.mp3", format="mp3")

    print("Файлы сохранены в папке:", folder)


def process_audio(file_main_audio: str, lesson_id: int, file_split_text: str) -> bool:
    print(90 * '-')
    print('Start processing main audio')

    if file_split_text:
        # GET EXIST TRANSCRIBE FILE
        file_name_relative = os.path.join("files", "lessons", str(lesson_id), 'transcribe_audio.json')
        file_transcribe = os.path.join(settings.UPLOAD_DIRECTORY, file_name_relative)
    else:
        # AUDIO TO SPEACH
        file_transcribe = open_ai_transcribe_audio(file_main_audio, lesson_id)

        # FIX SOURCE TEXT WITH WORD
        fix_transcribe_file_text(file_transcribe)

        # SPLIT TEXT
        file_split_text, error = open_ai_split_text(file_transcribe, lesson_id)
        if error:
            file_split_text = standard_split_text(file_transcribe, lesson_id)

    # WORD TIMING
    print(90 * '-')
    print(file_transcribe)
    print(file_split_text)
    print(90 * '-')
    file_split_text_timing = get_split_text_timing(file_transcribe, file_split_text, lesson_id)

    # SPLIT MAIN AUDIO
    split_main_audio(file_main_audio, file_split_text_timing, lesson_id)

    # TRANSLATE TO RUSSIAN
    file_translation = open_ai_translate(file_split_text, lesson_id)

    # TEXT TO SPEACH TRANSLATE
    folder_audio_translation = open_ai_tts_translation(file_translation, lesson_id)

    print('Finish processing main audio')
    return True


if __name__ == '__main__':
    file_name = '/my/src/retolu_back/public/media/files/lessons/21/transcribe_audio.json'
    lesson_id = 1
    open_ai_split_text(file_name, lesson_id)
    exit(0)

    # open_ai_split_text_auto('/Users/admin/my/src/retolu_back/public/media/files/lessons/5/transcribe_audio.json', 5)
    # correct_transcribe_text('/Users/admin/my/src/retolu_back/public/media/files/lessons/5/transcribe_audio.json')
    # exit(0)

    # file_transcribe = '/Users/admin/my/src/retolu_back/public/media/files/lessons/5/transcribe_audio.json'
    # file_split_text = '/my/src/retolu_back/public/media/files/lessons/5/split_text.json'
    # file_split_text_timing = get_split_text_timing(file_transcribe, file_split_text, 5)
    # exit(0)
    #
    for track_id in range(1, 70):
        if track_id < 10:
            track_id = f'0{track_id}'
        file_main_audio = f"/Users/admin/my/src/retolu_back/data/Collins IELTS Listening/collin's IELTS Listening 64k/HC IELTS_Listening_Track {track_id}.mp3"
        print(file_main_audio)

        lesson_id = f'5_{track_id}'
        lesson_id = f'5'
        folder = os.path.join(settings.UPLOAD_DIRECTORY, "files", "lessons", str(lesson_id))
        Path(folder).mkdir(parents=True, exist_ok=True)
        destination_file = os.path.join(settings.UPLOAD_DIRECTORY, "files", "lessons", str(lesson_id), 'audio_source.mp3')
        shutil.copy(file_main_audio, destination_file)

        process_audio(file_main_audio, lesson_id)
        break
