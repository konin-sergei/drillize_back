from pydub import AudioSegment
from pydub.silence import split_on_silence
pydub как разделить mp3 файл на части если у меня есть

def parse_mp3(source_file='', res_folder='', silence_threshold_milliseconds=500, silence_threshold_decibels=14):
    # Загрузим MP3 файл
    audio = AudioSegment.from_mp3(source_file)

    # Порог для определения тишины (в децибелах)
    silence_thresh = audio.dBFS - silence_threshold_decibels

    # Разделим аудио файл на части
    chunks = split_on_silence(
        audio,
        min_silence_len=silence_threshold_milliseconds,
        silence_thresh=silence_thresh,
        keep_silence=500  # Оставить немного тишины в начале и в конце каждого фрагмента
    )

    # Сохраним каждую часть как отдельный файл
    for i, chunk in enumerate(chunks):
        chunk_filename = f"{res_folder}/{i + 1}_312.mp3"
        chunk.export(chunk_filename, format="mp3")
        print(f"Сохранен файл: {chunk_filename}")


if __name__ == "__main__":
    # audio_file = "/Users/admin/my/src/subtitles/web/listening/source/02 1. An expensive picture.mp3"
    # audio_file = "/my/src/subtitles/web/files/Oxford Stories for reproduction Introductory 2 Audio/audio/04 2. A Greek restaurant.mp3"

    audio_file = "/Users/admin/my/src/subtitles/web/files/IELTS/Complete IELTS Bands 5-6.5/CD1/02 Track 2.mp3"
    res_folder = "/my/src/retolu_back/test/public/media/audio312"
    parse_mp3(audio_file, res_folder, 500, 14)

    # text_to_json()
