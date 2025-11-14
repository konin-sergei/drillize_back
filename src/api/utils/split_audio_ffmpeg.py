import subprocess
import json
import os


def detect_silence(source_file, silence_threshold_decibels=-30, min_silence_duration=0.5):
    """
    Использует FFmpeg для обнаружения тишины в аудиофайле.
    :param source_file: путь к файлу MP3
    :param silence_threshold_decibels: уровень громкости тишины в дБ
    :param min_silence_duration: минимальная продолжительность тишины в секундах
    :return: список (start, end) фрагментов звука
    """
    command = [
        "ffmpeg",
        "-i", source_file,
        "-af", f"silencedetect=noise={silence_threshold_decibels}dB:d={min_silence_duration}",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    silence_log = result.stderr  # FFmpeg выводит логи в stderr

    # Печатаем логи FFmpeg
    print("Логи FFmpeg:")
    print(silence_log)

    timestamps = []
    last_end = 0

    for line in silence_log.split("\n"):
        if "silence_start" in line:
            start = float(line.split("silence_start: ")[1])
            timestamps.append((last_end, start))
        if "silence_end" in line:
            last_end = float(line.split("silence_end: ")[1].split(" |")[0])

    return timestamps


def split_audio_ffmpeg(source_file, res_folder, silence_threshold_decibels=-30, min_silence_duration=0.5):
    """
    Разрезает MP3 по тишине.
    :param source_file: путь к файлу MP3
    :param res_folder: папка для сохранения
    :param silence_threshold_decibels: громкость тишины
    :param min_silence_duration: минимальная длина тишины
    """
    if not os.path.exists(res_folder):
        os.makedirs(res_folder)

    timestamps = detect_silence(source_file, silence_threshold_decibels, min_silence_duration)
    print("Найденные временные метки:")
    print(timestamps)

    for i, (start, end) in enumerate(timestamps):
        output_file = os.path.join(res_folder, f"{i+1}_313.mp3")
        command = [
            "ffmpeg",
            "-i", source_file,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output_file
        ]
        # Запускаем команду FFmpeg и выводим логи в консоль
        print(f"Выполняется команда: {' '.join(command)}")
        subprocess.run(command)  # Логи stdout и stderr будут выведены в консоль
        print(f"Сохранен файл: {output_file}")


if __name__ == "__main__":
    audio_file = "/Users/admin/my/src/subtitles/web/files/IELTS/Complete IELTS Bands 5-6.5/CD1/02 Track 2.mp3"
    res_folder = "/Users/admin/my/src/retolu_back/test/public/media/audio"

    split_audio_ffmpeg(audio_file, res_folder, -16, 0.5)