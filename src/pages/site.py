# src/pages/site.py

import json
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

BASE_DIR = "/my/src/drillize_back/data"


def parse_query_file(file_path: Path) -> dict:
	"""Парсит файл запроса и возвращает словарь с данными."""
	with open(file_path, 'r', encoding='utf-8') as f:
		content = f.read()

	# Извлекаем номер и название из имени файла
	filename = file_path.stem  # без расширения
	match = re.match(r'^(\d+)\s+(.+)$', filename)
	if not match:
		print('Error parsing file', file_path)
	number = int(match.group(1))
	name = match.group(2)

	# Разделяем содержимое на части по маркерам
	query_text = ""
	answers = []

	# Находим позицию {query_text}
	query_start = content.find('{query_text}')
	if query_start != -1:
		# Находим начало текста вопроса (после {query_text} и переводов строк)
		query_content_start = content.find('\n', query_start) + 1
		# Находим первый блок {answer_text}
		first_answer_pos = content.find('{answer_text}', query_content_start)

		if first_answer_pos != -1:
			# Текст вопроса - от начала до первого ответа
			query_text = content[query_content_start:first_answer_pos].strip()
		else:
			# Если нет ответов, берем весь текст после {query_text}
			query_text = content[query_content_start:].strip()

	# Находим все блоки ответов
	answer_pattern = r'\{answer_text\}\{(\d+)\}\{(.+?)\}'

	for match in re.finditer(answer_pattern, content):
		answer_number = match.group(1)
		source = match.group(2)
		answer_start = match.end()

		# Находим конец текущего ответа (начало следующего или конец файла)
		next_answer_pos = content.find('{answer_text}', answer_start)
		if next_answer_pos != -1:
			answer_text = content[answer_start:next_answer_pos].strip()
		else:
			answer_text = content[answer_start:].strip()

		answers.append({
			"number": answer_number,
			"source": source,
			"answer_text": answer_text
		})

	return {
		"number": number,
		"name": name,
		"query_text": query_text,
		"answers": answers
	}


router = APIRouter(
	tags=["HTML site"]
)


@router.get("/")
async def root(request: Request):
	courses = []
	courses_dir = Path(BASE_DIR) / "courses"

	if courses_dir.exists():
		for course_dir in courses_dir.iterdir():
			if course_dir.is_dir():
				course_info_path = course_dir / "course_info.json"
				if course_info_path.exists():
					with open(course_info_path, 'r', encoding='utf-8') as f:
						course_info = json.load(f)
						courses.append(course_info)

	return templates.TemplateResponse('/site/index.html', {'request': request, 'courses': courses})


def parse_answer_file(file_path: Path) -> dict:
	"""Парсит файл ответа и возвращает словарь с данными."""
	# Извлекаем номер и автора из имени файла
	filename = file_path.stem  # без расширения
	match = re.match(r'^answer\s+(\d+)\s+(.+)$', filename)
	if not match:
		# Попробуем альтернативный формат без автора
		match = re.match(r'^answer\s+(\d+)$', filename)
		if match:
			number = match.group(1)
			author = ""
		else:
			print(f'Error parsing answer file: {file_path}')
			return None
	else:
		number = match.group(1)
		author = match.group(2)

	# Читаем содержимое файла
	with open(file_path, 'r', encoding='utf-8') as f:
		answer_text = f.read().strip()

	return {
		"number": number,
		"author": author,
		"answer_text": answer_text
	}


def get_course_data(course_id: int) -> dict | None:
	courses_dir = Path(BASE_DIR) / "courses"

	# Находим все папку курса
	course_dir = None
	for d in courses_dir.iterdir():
		if d.is_dir() and d.name.startswith(f"course {course_id} "):
			course_dir = d
			break
	if not course_dir:
		return None

	course_info_path = course_dir / "course_info.json"

	data = {
		"course_info": None,
		"queries": {}
	}

	# Читаем course_info.json
	with open(course_info_path, 'r', encoding='utf-8') as f:
		course_info = json.load(f)
		data["course_info"] = course_info

	# Находим все папки, начинающиеся с "query"
	query_dirs = sorted(
		[d for d in course_dir.iterdir() if d.is_dir() and d.name.startswith("query")],
		key=lambda x: x.name
	)

	for query_dir in query_dirs:
		# Извлекаем номер и название из имени папки
		filename = query_dir.name
		match = re.match(r'^query\s+(\d+)\s+(.+)$', filename)
		if not match:
			print(f'Error parsing query directory: {query_dir}')
			continue

		query_id = match.group(1)
		query_name = match.group(2)

		# Читаем текст вопроса из query.md
		query_file = query_dir / "query.md"
		query_text = ""
		with open(query_file, 'r', encoding='utf-8') as f:
			query_text = f.read().strip()

		# Парсим текстовые ответы
		text_answers = {}
		text_answers_dir = query_dir / "text_answers"
		if text_answers_dir.exists() and text_answers_dir.is_dir():
			answer_files = sorted(
				[f for f in text_answers_dir.iterdir() if f.is_file() and f.suffix == '.md'],
				key=lambda x: x.name
			)
			for answer_file in answer_files:
				answer_data = parse_answer_file(answer_file)
				if answer_data:
					# Используем номер ответа как ключ (строковый)
					answer_number = answer_data["number"]
					# Сохраняем только author и answer_text, без number
					text_answers[answer_number] = {
						"author": answer_data["author"],
						"answer_text": answer_data["answer_text"]
					}

		# Парсим видео ответы
		video_answers = {}
		video_answers_dir = query_dir / "video_answers"
		if video_answers_dir.exists() and video_answers_dir.is_dir():
			answer_files = sorted(
				[f for f in video_answers_dir.iterdir() if f.is_file() and f.suffix == '.md'],
				key=lambda x: x.name
			)
			for answer_file in answer_files:
				answer_data = parse_answer_file(answer_file)
				if answer_data:
					# Используем номер ответа как ключ (строковый)
					answer_number = answer_data["number"]
					# Сохраняем только author и answer_text, без number
					video_answers[answer_number] = {
						"author": answer_data["author"],
						"answer_text": answer_data["answer_text"]
					}

		# Формируем данные запроса
		query_data = {
			"id": int(query_id),
			"name": query_name,
			"text": query_text,
			"text_answers": text_answers,
			"video_answers": video_answers
		}

		# Используем строковый ID как ключ в словаре queries
		data["queries"][query_id] = query_data
	return data


@router.get("/courses/{course_id}/start")
async def course(request: Request, course_id: int):
	course = get_course_data(course_id)

	# Находим индекс первого элемента
	query_id_first = next(iter(course['queries']), None)

	data = {
		'request': request,
		'course': course,
		'course_id': course_id,
		'query_id_first': query_id_first,
	}
	return templates.TemplateResponse('/service/course_start.html', data)

@router.get("/courses/{course_id}/finish")
async def course(request: Request, course_id: int):
	course = get_course_data(course_id)

	data = {
		'request': request,
		'course': course,
		'course_id': course_id,
	}
	return templates.TemplateResponse('/service/course_finish.html', data)


@router.get("/courses/{course_id}/queries/{query_id}")
async def query(request: Request, course_id: int, query_id: int):
	course = get_course_data(course_id)
	if not course:
		raise HTTPException(status_code=404, detail="Course not found")

	query_id_str = str(query_id)
	if query_id_str not in course["queries"]:
		raise HTTPException(status_code=404, detail="Query not found")

	len_queries = len(course["queries"])
	query = course["queries"][query_id_str]

	# Преобразуем словарь в список для навигации
	queries_list = list(course["queries"].items())

	# Находим индекс текущего элемента
	current_index = None
	for i, (k, v) in enumerate(queries_list):
		if str(k) == query_id_str:
			current_index = i
			break

	# Получаем следующий и предыдущий элементы
	query_next = None
	query_prev = None

	if current_index is not None:
		# Следующий элемент
		if current_index + 1 < len(queries_list):
			next_key, next_value = queries_list[current_index + 1]
			query_next = {"id": next_key, **next_value}

		# Предыдущий элемент
		if current_index > 0:
			prev_key, prev_value = queries_list[current_index - 1]
			query_prev = {"id": prev_key, **prev_value}

	text_answers = course['queries'][str(query_id)]['text_answers']
	video_answers = course['queries'][str(query_id)]['video_answers']

	if query_next:
		url_next = f'/courses/{course_id}/queries/{query_next["id"]}'
	else:
		url_next = f'/courses/{course_id}/finish'

	if query_prev:
		url_prev = f'/courses/{course_id}/queries/{query_prev["id"]}'
	else:
		url_prev = f'/courses/{course_id}/start'

	print(url_next)
	print(url_prev)

	count_answers = len(text_answers) + len(video_answers)

	return templates.TemplateResponse(
		'/service/query.html',
		{
			'request': request,
			'course_id': course_id,
			'query_id': query_id,
			'course': course,
			'query': query,
			'current_index': current_index,
			'len_queries': len_queries,
			'query_next': query_next,
			'query_prev': query_prev,
			'url_next': url_next,
			'url_prev': url_prev,
			'text_answers': text_answers,
			'video_answers': video_answers,
			'count_answers': count_answers,
		}
	)
