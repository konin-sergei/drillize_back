'use strict';

let data;
let data_generate_story;
let data_generate_audio;

let FILTER_VIEW = '';
let FILTER_SORT = '';
let FILTER_PROGRESS = '';
let SETWORD_ACTIVE_ID = '';
let SWITCH_MOBILE_VERSION = '';

function logDate(info) {
    let date = new Date();
    console.log(date, info);
}

function addAudioFiles(setword_audio_files, id_audio_container) {
    if (setword_audio_files === undefined || setword_audio_files === "") {
        return;
    }
    setword_audio_files.forEach(function (line) {
        addAudioFile(line.file_name, line.type, line.info, line.id, id_audio_container)
    });
}

// Add audio file for set word
function addAudioFile(file_name, type, info, id, id_audio_container) {
    let template = $('#tmpl-audio-fle').html()

    if (file_name === undefined || file_name === "") {
        return;
    }

    template = template.replaceAll("{info}", info);
    template = template.replaceAll("{file_name}", file_name);
    template = template.replaceAll("{id}", `${type}-${id}`);

    let container = document.getElementById(id_audio_container);
    container.insertAdjacentHTML('beforeend', template);

    let element = document.querySelector('.col-lg-9');
    let width = element.offsetWidth - 80;
    width = width + 'px';
    //width = 150 + 'px';
    let idAudio = `audio-item-${type}-${id}`;

    if (videojs.players[idAudio]) {
        videojs.players[idAudio].dispose();
    }
    console.log('idAudio', idAudio);
    let player = videojs(idAudio,
        {
            controls: true,
            width: width,
            height: "30",
            playbackRates: [0.5, 0.7, 1, 1.5],
            controlBar: {
                fullscreenToggle: false,
                volumePanel: false,
                currentTimeDisplay: true,
                timeDivider: true,
                durationDisplay: true,
                progressControl: true,
                remainingTimeDisplay: true,
            }
        },
    );
}

document.addEventListener('DOMContentLoaded', function () {

    FILTER_VIEW = document.getElementById('filter_view').value;
    FILTER_SORT = document.getElementById('filter_sort').value;
    FILTER_PROGRESS = document.getElementById('filter_progress').value;
    SETWORD_ACTIVE_ID = document.getElementById('setword_active_id').value;
    SWITCH_MOBILE_VERSION = document.getElementById('switch_mobile_version').value;

    data = JSON.parse(document.getElementById('data_main').textContent);

    data_generate_story = JSON.parse(document.getElementById('data_generate_story').textContent);
    data_generate_audio = JSON.parse(document.getElementById('data_generate_audio').textContent);

    // Add player for audio file
    let setword_audio_files = JSON.parse(document.getElementById('data_setword_audio_files').textContent);

    addAudioFiles(setword_audio_files, 'group-audio-description');
    addAudioFiles(data_generate_audio, 'group-audio-generate-audio');

    setGenerateStoryContent(0);

    initMobileView();

    feather.replace();
});

// Play audio
function setEventOnButtonPlay() {
    document.querySelectorAll(".button-play").forEach(function (item) {
        item.addEventListener("click", function () {
            let audioFile = item.getAttribute('data-audio-file');
            let typeText = item.getAttribute('data-type-text');
            let wordId = item.getAttribute('data-word-id');
            let position = 0;
            playAudio(audioFile, typeText, wordId, position = '0');
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    //Close dropdown menu
    let dropdownItems = document.querySelectorAll(".dropdown-menu .dropdown-item");
    dropdownItems.forEach(function (item) {
        item.addEventListener("click", function () {
            let dropdownMenu = this.closest(".dropdown-menu");
            if (dropdownMenu.classList.contains('show')) {
                dropdownMenu.classList.remove('show');
            }
        });
    });

    // View checkboxes
    let checkboxItems = document.querySelectorAll(".view-checkbox");
    checkboxItems.forEach(function (item) {
        item.addEventListener("change", function () {
            changeCheckboxView();
        });
    });


    setEventOnButtonPlay();


    // Btn nav word content
    document.querySelectorAll(".btn-nav-word-content").forEach(function (item) {
        item.addEventListener("click", function () {
            let dataDirection = item.getAttribute('data-direction');
            let wordId = item.getAttribute('data-word-id');
            navWordContent(dataDirection, wordId);
        });
    });

    // Btn nav story content
    document.querySelectorAll(".btn-nav-story-content").forEach(function (item) {
        item.addEventListener("click", function () {
            let dataDirection = item.getAttribute('data-direction');
            let storyId = item.getAttribute('data-story-id');
            navStoryContent(dataDirection, storyId);
        });
    });

    // El word text
    document.querySelectorAll(".el-word").forEach(function (item) {
        item.addEventListener("click", function () {
            let wordId = item.getAttribute('data-word-id');
            clickWord(wordId);
        });
    });


    // El content text
    document.querySelectorAll(".el-content").forEach(function (item) {
        item.addEventListener("click", function () {
            let wordId = item.getAttribute('data-word-id');
            clickContext(wordId);
        });
    });

    // Btn clear user text
    document.querySelectorAll(".btn-clear-user-text").forEach(function (item) {
        item.addEventListener("click", function () {
            let wordId = item.getAttribute('data-word-id');
            clearUserText(wordId);
        });
    });

    // Btn enter user text
    document.querySelectorAll(".btn-enter-user-text").forEach(function (item) {
        item.addEventListener("click", function () {
            let wordId = item.getAttribute('data-word-id');
            enterUserText(wordId);
        });
    });

    // El input text
    document.querySelectorAll(".el-input-text").forEach(function (item) {
        item.addEventListener("click", function () {
            let wordId = item.getAttribute('data-word-id');
            inputText(wordId);
        });
    });

    // Btn set learned
    document.querySelectorAll(".btn-set-learned").forEach(function (item) {
        item.addEventListener("click", function () {
            let wordId = item.getAttribute('data-word-id');
            setLearned(wordId);
        });
    });


});

/*
Async get data
document.addEventListener('DOMContentLoaded', function () {
    let url = `/student/ajax/setword/{{ setword_active.id }}/word/?filter_sort={{ filter_sort }}&filter_progress={{ filter_progress }}&filter_view={{ filter_view }}&filter_transcription={{filter_transcription}}&filter_generate_context={{ filter_generate_context }}&filter_hide_first_example={{ filter_hide_first_example }}&filter_definition={{ filter_definition }}`;
    fetch(url)
        .then(function (response) {
            console.log('get data');
            return response.json();
        })
        .then(res => {
            data = res;
            console.log('parse data', res.length);
        })
        .catch(error => {
            console.error('Error fetching the data:', error);
        });

});
*/

//Change checkbox view
function changeCheckboxView() {
    let filter_transcription = "No";
    let filter_picture = "No";
    let filter_generate_context = "No";
    let filter_hide_first_example = "No";
    let filter_definition = "No";

    let checkbox_transcription = document.getElementById("checkbox_transcription");
    if (checkbox_transcription.checked) {
        filter_transcription = "Show";
    }
    let checkbox_picture = document.getElementById("checkbox_picture");
    if (checkbox_picture.checked) {
        filter_picture = "Show";
    }
    let checkbox_generate_context = document.getElementById("checkbox_generate_context");
    if (checkbox_generate_context.checked) {
        filter_generate_context = "Show";
    }
    let checkbox_hide_first_example = document.getElementById("checkbox_hide_first_example");
    if (checkbox_hide_first_example.checked) {
        filter_hide_first_example = "Show";
    }
    let checkbox_definition = document.getElementById("checkbox_definition");
    if (checkbox_definition.checked) {
        filter_definition = "Show";
    }

    let url = `/student/setword/${SETWORD_ACTIVE_ID}/word/?filter_sort=${FILTER_SORT}&filter_progress=${FILTER_PROGRESS}&filter_view=${FILTER_VIEW}&filter_transcription=${filter_transcription}&filter_picture=${filter_picture}&filter_generate_context=${filter_generate_context}&filter_hide_first_example=${filter_hide_first_example}&filter_definition=${filter_definition}`;
    goTo(url)
}


function playAudio(audioFile, typeText, wordId, position = '0') {
    wordId = parseInt(wordId);

    if (audioFile === "") {
        let text = '';
        const item = data.find(element => element.id === wordId);

        let content = item.contexts[item.position];
        if (content === undefined || content === "") {
            return;
        }

        if (typeText === 'word_text') {
            text = item.text;
        } else if (typeText === "definition_text") {
            text = item.definition_text;
        } else if (typeText === "context_text") {
            text = content.text;
        }
        if (text !== '') {
            speakTextBrowser(text, 'en');
        }
        return;
    }
    let audioSource = document.getElementById("word-audio-source");
    audioSource.src = audioFile;

    let audioElement = document.getElementById("word-audio");
    audioElement.load();

    let wordAudio = document.getElementById('word-audio');
    wordAudio.play();
}

function navWordContentApi(direction, wordId) {
    data['contexts'] = contexts;
    const json = JSON.stringify(data);
    const request = new Request(
        `/student/ajax/word/${setwordId}/word/save/`,
        {
            method: 'POST',
            mode: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: json
        }
    );

    fetch(request)
        .then(response => response.json())
        .then(data => {
            window.location.href = `/student/setword/${setwordId}/word`;
        })
        .catch(error => console.error(error));
}

function navWordContent(direction, wordId) {
    wordId = parseInt(wordId);
    const item = data.find(element => element.id === wordId);

    if (item.contexts.length === 0) {
        return;
    }

    if (direction === 'right') {
        document.getElementById(`word-${wordId}-button-left`).classList.add('page-link-active');
        document.getElementById(`word-${wordId}-button-left`).classList.remove('page-link-inactive');
        if (item.contexts.length - 2 === item.position) {
            document.getElementById(`word-${wordId}-button-right`).classList.remove('page-link-active');
            document.getElementById(`word-${wordId}-button-right`).classList.add('page-link-inactive');
        }
        if (item.position < item.contexts.length - 1) {
            item.position = item.position + 1;
        }
        playContext(wordId, item);
    } else if (direction === 'left') {
        document.getElementById(`word-${wordId}-button-right`).classList.add('page-link-active');
        document.getElementById(`word-${wordId}-button-right`).classList.remove('page-link-inactive');
        if (item.position > 0) {
            item.position = item.position - 1;
        }
        if (item.position === 0) {
            document.getElementById(`word-${wordId}-button-left`).classList.remove('page-link-active');
            document.getElementById(`word-${wordId}-button-left`).classList.add('page-link-inactive');
        }
        playContext(wordId, item);
    }

    function playContext(wordId, item) {
        if (FILTER_VIEW === 'Audio') {
            changeClassList(`#word-${wordId}-content-text`, 'add', 'font-color-transparent');
            changeClassList(`#word-${wordId}-content-translate`, 'add', 'font-color-transparent');
            changeClassList(`#word-${wordId}-text`, 'add', 'font-color-transparent');
            changeClassList(`#word-${wordId}-translate`, 'add', 'font-color-transparent');
            playAudio(item.contexts[item.position].text_audio, 'context_text', item.id, item.position);
        }
    }

    let content = item.contexts[item.position];

    document.getElementById(`word-${wordId}-content-text`).innerText = content.text;
    document.getElementById(`word-${wordId}-content-translate`).innerText = content.translate;

    const buttonPlay = document.getElementById(`word-${wordId}-button-play-context`);
    buttonPlay.setAttribute('data-audio-file', content.text_audio);
    buttonPlay.setAttribute('data-context-position', item.position);

    const buttonPlayTextareaInput = document.getElementById(`word-${wordId}-button-play-context-textarea-input`);
    buttonPlayTextareaInput.setAttribute('data-audio-file', content.text_audio);
    buttonPlayTextareaInput.setAttribute('data-context-position', item.position);

    document.getElementById(`word-${wordId}-content-translate`).classList.add('d-none');
    document.getElementById(`word-${wordId}-content-text`).classList.remove('d-none');

}

function navStoryContent(direction, storyId) {

    storyId = parseInt(storyId);

    if (data_generate_story.length === 0) {
        return;
    }

    if (direction === 'right') {
        document.getElementById(`story-${storyId}-button-left`).classList.add('page-link-active');
        document.getElementById(`story-${storyId}-button-left`).classList.remove('page-link-inactive');
        if (data_generate_story.stories.length - 2 === data_generate_story.position) {
            document.getElementById(`story-${storyId}-button-right`).classList.remove('page-link-active');
            document.getElementById(`story-${storyId}-button-right`).classList.add('page-link-inactive');
        }
        if (data_generate_story.position < data_generate_story.stories.length - 1) {

            data_generate_story.position = data_generate_story.position + 1;
        }


    } else if (direction === 'left') {
        document.getElementById(`story-${storyId}-button-right`).classList.add('page-link-active');
        document.getElementById(`story-${storyId}-button-right`).classList.remove('page-link-inactive');
        if (data_generate_story.position > 0) {
            data_generate_story.position = data_generate_story.position - 1;
        }
        if (data_generate_story.position === 0) {
            document.getElementById(`story-${storyId}-button-left`).classList.remove('page-link-active');
            document.getElementById(`story-${storyId}-button-left`).classList.add('page-link-inactive');
        }

    }

    setGenerateStoryContent(data_generate_story.position);

}

function setGenerateStoryContent(position) {

    if (data_generate_story === undefined || data_generate_story === "" || data_generate_story.stories === "" || data_generate_story.stories.length === 0) {
        return;
    }

    let line = data_generate_story.stories[position];
    document.getElementById(`story-content-text`).innerHTML = line.text;
    let storyInfo = 'Story';
    if (data_generate_story.stories.length > 1) {
        storyInfo = `Story ${position + 1}/${data_generate_story.stories.length}`;
    }
    document.getElementById(`generate-story-info`).innerText = storyInfo;
    document.getElementById('group-audio-generate-story').innerHTML = '';
    addAudioFile(line.file_name, line.type, line.info_text, line.id, 'group-audio-generate-story');
    addAudioFile(line.file_name_translate_text, line.type, line.info_translate_text, line.id+1, 'group-audio-generate-story');
    addAudioFile(line.file_name_text_translate, line.type, line.info_text_translate, line.id+2, 'group-audio-generate-story');

}

/*
function editFolder(action, folderId, folderName, folderIdActive) {
    let modal = new bootstrap.Modal(document.getElementById('folder-edit-modal-lg'), {});

    document.getElementById("folder-edit-modal-button-delete").classList.add('d-none');

    if (action === "add") {
        document.getElementById("folder-edit-modal-action").setAttribute("action", "/student/setword/add/");
    } else if (action === "edit") {
        document.getElementById("folder-edit-modal-action").setAttribute("action", "/student/setword/add/");
        document.querySelector('input[name="folder_name"]').value = folderName;
        document.querySelector('input[name="setword_id"]').value = folderId;
        document.querySelector('input[name="setword_id_active"]').value = folderIdActive;

        document.getElementById("folder-edit-modal-action").setAttribute("action", `/student/setword/${folderId}/`);
        document.getElementById("folder-edit-modal-button-delete").classList.remove('d-none');
        document.getElementById("folder-edit-modal-button-delete").setAttribute("href", `/student/setword/${folderId}/delete/?setword_id_active=${folderIdActive}`);
    }

    modal.show();
}
*/

function clickWord(wordId) {
    wordId = parseInt(wordId);
    let hasFontColorTransparentWordText = document.getElementById(`word-${wordId}-text`).classList.contains('font-color-transparent');
    if (hasFontColorTransparentWordText === true) {
        document.getElementById(`word-${wordId}-text`).classList.remove('font-color-transparent')
        document.getElementById(`word-${wordId}-translate`).classList.remove('font-color-transparent')
        return;
    }
    let show = document.getElementById(`word-${wordId}-translate`).classList.contains('d-none');
    if (show === true) {
        document.getElementById(`word-${wordId}-translate`).classList.remove('d-none');
        document.getElementById(`word-${wordId}-text`).classList.add('d-none');
    } else {
        document.getElementById(`word-${wordId}-translate`).classList.add('d-none');
        document.getElementById(`word-${wordId}-text`).classList.remove('d-none');
    }
}

function clickContext(wordId) {
    wordId = parseInt(wordId);
    let showTranslate = false;
    const item = data.find(element => element.id === wordId);
    if (item.contexts.length > 0) {
        let content = item.contexts[item.position];
        if (content.translate !== "") {
            showTranslate = true;
        }
    }

    if (showTranslate === false) {
        return;
    }

    let hasFontColorTransparent = document.getElementById(`word-${wordId}-content-text`).classList.contains('font-color-transparent');
    if (hasFontColorTransparent === true) {
        document.getElementById(`word-${wordId}-content-text`).classList.remove('font-color-transparent')
        document.getElementById(`word-${wordId}-content-translate`).classList.remove('font-color-transparent')
        return;
    }

    let show = document.getElementById(`word-${wordId}-content-translate`).classList.contains('d-none');
    if (show === true) {
        document.getElementById(`word-${wordId}-content-translate`).classList.remove('d-none');
        document.getElementById(`word-${wordId}-content-text`).classList.add('d-none');
    } else {
        document.getElementById(`word-${wordId}-content-translate`).classList.add('d-none');
        document.getElementById(`word-${wordId}-content-text`).classList.remove('d-none');
    }
}

function setLearned(wordId) {
    const csrftoken = getCookie('csrftoken');
    const data = {};
    data['word_id'] = wordId;
    const json = JSON.stringify(data);
    const request = new Request(
        `/student/ajax/word/${wordId}/set_learned/`,
        {
            method: 'POST',
            mode: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: json
        }
    );

    fetch(request)
        .then(response => response.json())
        .then(data => {
            if (data['learned'] !== null) {
                document.getElementById(`word-${wordId}-group-item`).classList.add('bg-gray-200');
            } else {
                document.getElementById(`word-${wordId}-group-item`).classList.remove('bg-gray-200');
            }
        })
        .catch(error => console.error(error));
}


function goTo(url) {
    window.location.href = url;
}

function inputText(wordId) {

    // changeClassList(`#word-${wordId}-textarea-value-group`, 'add', 'd-none');
    // changeClassList(`#word-${wordId}-text`, 'add', 'font-color-transparent');
    // changeClassList(`#word-${wordId}-translate`, 'add', 'font-color-transparent');
    //
    // changeClassList(`#word-${wordId}-content-text`, 'add', 'd-none');
    // changeClassList(`#word-${wordId}-content-translate`, 'add', 'd-none');
    //
    // changeClassList(`#word-${wordId}-col-button`, 'add', 'd-none');
    // changeClassList(`#row-word-${wordId}-transcription`, 'add', 'd-none');

    changeClassList(`#word-${wordId}-container`, 'remove', 'd-flex');
    changeClassList(`#word-${wordId}-container`, 'add', 'd-none');

    changeClassList(`#word-${wordId}-textarea`, 'remove', 'd-none');
    changeClassList(`#word-${wordId}-textarea-group`, 'remove', 'd-none');

    document.getElementById(`word-${wordId}-textarea`).focus();


}

function enterUserText(wordId) {

    let wordTextarea = document.getElementById(`word-${wordId}-textarea`).value;
    if (wordTextarea === '') {
        document.getElementById(`word-${wordId}-textarea-value-group`).classList.add('d-none');
    } else {
        document.getElementById(`word-${wordId}-textarea-value-group`).classList.remove('d-none');
    }
    document.getElementById(`word-${wordId}-textarea-value`).textContent = document.getElementById(`word-${wordId}-textarea`).value;

    document.getElementById(`word-${wordId}-textarea`).classList.add('d-none');
    document.getElementById(`word-${wordId}-textarea-group`).classList.add('d-none');

    changeClassList(`#word-${wordId}-container`, 'add', 'd-flex');
    changeClassList(`#word-${wordId}-container`, 'remove', 'd-none');

    // changeClassList(`#word-${wordId}-text`, 'remove', 'font-color-transparent')
    // changeClassList(`#word-${wordId}-translate`, 'remove', 'font-color-transparent')
    //
    // changeClassList(`#word-${wordId}-text`, 'remove', 'd-none')
    // changeClassList(`#word-${wordId}-translate`, 'add', 'd-none')
    //
    // changeClassList(`#word-${wordId}-content-translate`, 'remove', 'font-color-transparent')
    // changeClassList(`#word-${wordId}-content-text`, 'remove', 'd-none');
    // changeClassList(`#word-${wordId}-content-text`, 'remove', 'font-color-transparent');
    // changeClassList(`#word-${wordId}-col-button`, 'remove', 'd-none');
    // changeClassList(`#row-word-${wordId}-transcription`, 'remove', 'd-none');
    //
    // changeClassList(`#word-${wordId}-content-translate`, 'add', 'd-none')
}

function clearUserText(wordId) {
    document.getElementById(`word-${wordId}-textarea`).value = "";
    document.getElementById(`word-${wordId}-textarea`).focus();
}

window.addEventListener("load", function () {
    initFunction();
});

function initFunction() {
    let elements = document.getElementsByClassName('user-textarea-input');
    for (let i = 0; i < elements.length; i++) {
        elements[i].addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                let wordId = event.target.dataset.word_id;
                enterUserText(wordId);
            }
        });
    }
}


function initMobileView() {
    let md = new MobileDetect(window.navigator.userAgent);
    if (md.mobile() !== null) {

        /*
        document.getElementById('head-button-sort-span').classList.add("d-none");
        document.getElementById('head-button-view-span').classList.add("d-none");
        document.getElementById('head-button-add-span').classList.add("d-none");
        document.getElementById('head-button-progress-span').classList.add("d-none");
        */

        document.getElementsByClassName('col-tree')[0].classList.add("col-mobile");
        document.getElementsByClassName('col-words')[0].classList.add("col-mobile");

        changeClassList('#head-button-sort-span', 'add', 'd-none')
        changeClassList('#head-button-view-span', 'add', 'd-none')
        changeClassList('#head-button-add-span', 'add', 'd-none')
        changeClassList('#head-button-progress-span', 'add', 'd-none')

        changeClassList('.col-word', 'add', 'pl-2')
        changeClassList('.col-word', 'add', 'pr-3')
        changeClassList('.col-word', 'add', 'pr-3')

        changeClassList('.button-input-text', 'add', 'd-none')

        if (FILTER_VIEW === 'Translate' || FILTER_VIEW === 'Word' || FILTER_VIEW === 'Word/Example' || FILTER_VIEW === 'Word/Example' || FILTER_VIEW === 'Audio') {
            changeClassList('.button-input-text', 'add', 'd-none')
        }

        changeClassList('.form-control-study', 'change', 'form-control-study-big')

        if (SWITCH_MOBILE_VERSION === 'True') {
            let elements = document.querySelectorAll('.font_tag');
            elements.forEach(element => {
                element.classList.remove("h4", "h5");
                element.classList.add("h3");
            });
        }
    }
}

window.speechSynthesis.onvoiceschanged = async function () {
    try {
        let voice = getVoice('en');

        await EasySpeech.init({maxTimeout: 5000, interval: 250});
        console.debug('load complete');

        await EasySpeech.speak({
            text: '',
            voice: voice,
            pitch: 1,
            rate: 1,
            volume: 1,
            boundary: e => console.debug('boundary reached')
        });

    } catch (e) {
        console.log('error speach');
    }
};


function getVoice(lang) {
    let findVoice = '';
    let voices = speechSynthesis.getVoices();
    let langCountry = '';

    if (lang === 'en') {
        langCountry = 'en_us';
    } else if (lang === 'ru') {
        langCountry = 'ru_ru';
    }

    for (let i = 0; i < voices.length; i++) {
        let voice = voices[i];
        let voiceLowerCase = voice.lang.trim().toLowerCase();
        let strVoiceUnderscore = voiceLowerCase.replace(/-/g, "_");
        if (strVoiceUnderscore === langCountry) {
            findVoice = voice;
            break;
        }
    }

    return findVoice;
}

async function speakTextBrowser(text, lang) {
    let voice = getVoice(lang);

    try {
        await EasySpeech.speak({
            text: text,
            voice: voice, // optional, will use a default or fallback
            pitch: 1,
            rate: 0.8,
            volume: 1,
            // there are more events, see the API for supported events
            boundary: e => console.debug('boundary reached')
        })
    } catch (e) {
        console.log('error speach');
    }


    /*
    let voice = getVoice(lang);
    speechSynthesis.cancel();
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    if (voice === "") {
        console.log('Error language');
    } else {
        utterance.voice = voice;
    }
    // utterance.lang = 'en_US';
    utterance.voice = voice;
    utterance.pitch = 1;
    utterance.rate = 1; // побыстрее
    synth.speak(utterance);

    let title = document.getElementById('title-page');
    title.innerText = `findVoice : ${voice.name} ${voice.lang}`;

     */
}

const saveScrollPos = false;
if (saveScrollPos) {
    document.addEventListener("DOMContentLoaded", function (event) {
        let scrollpos = localStorage.getItem('scrollpos');
        if (scrollpos) window.scrollTo(0, scrollpos);
    });
    window.onbeforeunload = function (e) {
        localStorage.setItem('scrollpos', window.scrollY);
    };
}


