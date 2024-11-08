# Technical Writer Ray의 개발 일지..

이 저장소는 Ray Kim이 취미 또는 TW 업무상 필요해서 짬짬이 개발한 간단한 도구들을 소개하기 위해 임시로 만든 공용 저장소입니다.

대부부 Python 코드 또는 Windows Powershell 스크립트이며, 지금은 사용하지 않는 아주 개발새발 작성한 Node.js 코드도 있습니다.

공개를 위해 Private 저장소에서 Public 저장소로 급하게 전환하다 보니, 아직 코드 정리가 되지 않은 곳이 매우 많습니다. 추후 리팩토링 등으로 개선해나갈 예정입니다.

## UnityReleaseToNativeRelease

개발자 가이드 Unity 엔진 릴리즈 노트를 파싱하여 자동으로 Android Native 릴리즈 노트와 iOS Native 릴리즈 노트를 생성하는 코드입니다. 지금은 사용하지 않습니다.

## broken-link-checker/V9

개발자 가이드에 있는 모든 상대 링크, 절대 링크를 체크하여 잘 작동하는지 보고서를 작성하는 코드입니다. 네임드 앵커 연결까지 체크합니다. 지금은 Material for MkDocs 내장 링크 체커를 사용하므로 이 코드는 사용하지 않습니다.

## change-heading-style

개발자 가이드 헤딩 스타일을 변경하기 위해 만든 코드입니다. 지금은 사용하지 않습니다.

## common

문서 수정, Git과 Gitlab 컨트롤을 위한 유틸리티 함수들입니다.

## concordance_search

번역 도구에서 제공하는 Concordance Search를 직접 만들어본 코드입니다. TMX 파일 형식의 번역 메모리를 읽어들인 후, 역 색인(inverted index)을 생성, Concordance Search UI로 역 색인에서 검색을 수행하고 결과를 리턴합니다. 지금은 사용하지 않습니다.

## files-include-a-term

특정 단어를 포함하고 있는 문서 파일들이 담긴 디렉토리 목차를 추출하는 코드입니다. 루트 디렉토리를 입력하면 하위 디렉토리에서도 재귀적으로 탐색을 진행합니다. 탐색하고 싶지 않은 디렉토리 목록(excluded_directories)을 넘겨주면 이들을 검색 범위에서 제외하고 찾을 수도 있습니다.

## html-to-md

워드프레스 레거시 형식이 섞여있는 HTML 문서를 Python Markdown 문서로 변환하는 코드입니다. GUI를 지원합니다.

## llm/unified

LLM API를 호출해 문서를 다국어로 자동 번역하는 코드입니다. 현재 지속적으로 개발중입니다.

### v1 GUI/GUI_Realtime

source 콘텐츠를 복사해 붙여넣고, API 플랫폼과 모델을 선택하고, 번역 버튼을 누르면 LLM API를 호출해 해당 다국어로 번역한 텍스트를 리턴하는 코드입니다. GUI 방식이며 GUI는 파일 단위 번역, GUI_Realtime은 실시간 번역입니다. 

### v6-common

일반적으로 사용할 수 있는 영한 번역기를 구현한 코드입니다. GUI는 없으며 현재 LLaMA 3.1 70b 모델만 지원합니다.

### v9

GPT4-O-mini API를 사용한 번역 도구입니다.

#### `translate.py`

파일 단위 번역을 하는 코드입니다.

#### `translate_md.py`
  
파일에서 변경 사항만을 추적하여, 변경된 내용만 번역하는 코드입니다. LLM 번역 오류를 줄이고, API 호출 비용 등을 줄이기 위해 작성했습니다.

1. Merge Request에 있는 commit들을 추출해 변경 사항들을 알아냅니다.
2. commit들을 사용해 변경 전 국문 파일과 변경 후 국문 파일을 추출합니다.
3. 변경 전 국문 파일, 변경 후 국문 파일, 변경 전 다국어 파일 이렇게 3개 파일을 Custom Parser로 파싱하여 구조화합니다.
4. 변경 전 국문 파일과 변경 후 국문 파일 구조 사이에 차이점을 분석합니다.
5. 그 차이점들만을 골라 번역 API를 호출해 번역합니다.
6. 번역된 차이점들을 변경 전 다국어 파일에 적용해, 변경 후 다국어 파일을 생성합니다.
7. 변경 후 다국어 파일을 역 구조화하여 원래 마크다운 파일로 복원합니다.
8. 마크다운 파일을 디렉토리에 저장합니다.

### powershell/deploy-docs/v7

 Gitlab 기반 환경에서 문서를 자동으로 빌드하는 Windows Powershell 스크립트입니다.

 1. deploy-doc: 국문 또는 영문 문서를 상용 배포합니다.
 2. deploy-doc-tr: 국, 영문 외 다국어를 상용 배포합니다.
 3. deploy-preview: 국문 또는 영문 문서 프리뷰를 배포합니다.
 4. remove-preview: 배포한 프리뷰를 삭제합니다.
 5. checkout-to-last-tag: 특정 단어를 포함한 모든 tag를 검색한 후, 그 중 가장 최신 tag를 반환하고, 이 tag를 기준으로 새 브랜치로 checkout 합니다.

### process-html, process-markdown

각각 HTML과 마크다운 파일에 내가 원하는 처리를 하고 저장하기 위한 코드입니다.

### skip-translations/python/v7

특정 영문 단어들을 다국어(중국어 등)로 번역하지 않기 위한 처리 코드입니다.

1. 국문 문서를 파싱하여 국문 내 영문 단어들만을 추출합니다.
    1. 국문 파일별로 영문 고유 명사 단어 리스트를 생성, 저장합니다. (`createSkipListV7.py`)
2. 국문 내 영문 단어들은 영어 고유 명사로 취급해 다국어로 번역하지 않기로 합니다.
3. 각 영문 문서에서 해당 단어들을 찾아 `<span class="notransate">` 태그로 감쌉니다. (`applySkipListsFromDirV7.py`)
4. 이 기능을 GUI로 구현합니다 (`skipTranslationV7.py`)

### update-links

개발자 문서 전체에서 각 마크다운 페이지를 노드로, 다른 페이지로 이동하는 링크(상대 링크)를 엣지로 하여 그래프를 생성하는 코드입니다.

* 노드(페이지) 간 엣지(링크)가 여러 개 존재할 수 있습니다.
* 네임드 앵커가 다르면, 서로 다른 엣지로 취급합니다.

아직 개발중인 코드이며, 추후 다음 기능을 추가할 계획입니다.

1. 전체 개발자 가이드를 주기적으로 읽어들이면서 최신 그래프 유지
2. 개발자 가이드가 변경되면(=페이지 삭제, 추가, 네임드 앵커 이름 변경 등) 변경 사항을 추적하여 엣지(링크) 변동을 감지, 링크 변경을 그래프에서 자동으로 업데이트
3. 변경된 그래프를 가지고 개발자 가이드에 적용(상대 링크를 자동으로 수정)


# Development Journal of Technical Writer Ray

This repository is a temporary public repository created to introduce simple tools developed by Ray Kim for hobby or work-related needs.

Most of the code is written in Python or Windows PowerShell scripts, and there is also some rudimentary Node.js code that is no longer in use.

Due to a hasty transition from a private repository to a public one for disclosure, there are still many areas where the code is not organized. Improvements will be made through future refactoring.

## UnityReleaseToNativeRelease

This code automatically generates Android Native release notes and iOS Native release notes by parsing the developer guide Unity engine release notes. It is currently not in use.

## broken-link-checker/V9

This code checks all relative and absolute links in the developer guide and generates a report on their functionality. It also checks named anchor connections. Currently, this code is not used because the built-in link checker in Material for MkDocs is being utilized.

## change-heading-style

This code was created to change the heading style of the developer guide. It is currently not in use.

## common

Utility functions for document modification and Git/GitLab control.

## concordance_search

This code is an attempt to create a Concordance Search tool provided by translation tools. It reads translation memory in TMX file format, generates an inverted index, performs searches on the Concordance Search UI, and returns results. It is currently not in use.

## files-include-a-term

This code extracts a directory listing of document files containing a specific word. When the root directory is input, it recursively searches in subdirectories. You can also pass a list of directories to exclude from the search (excluded_directories).

## html-to-md

This code converts HTML documents mixed with WordPress legacy formats into Python Markdown documents. It supports a GUI.

## llm/unified

This code automatically translates documents into multiple languages by calling the LLM API. It is currently under continuous development.

### v1 GUI/GUI_Realtime

This code allows you to copy and paste source content, select the API platform and model, and click the translate button, which calls the LLM API to return the translated text in the selected language. It has a GUI for file-based translation, while GUI_Realtime provides real-time translation.

### v6-common

This code implements a general English-Korean translator. There is no GUI, and it currently only supports the LLaMA 3.1 70b model.

### v9

This is a translation tool using the GPT4-O-mini API.

#### `translate.py`

This code performs file-based translation.

#### `translate_md.py`

This code tracks only the changes in a file and translates only the modified content. It was created to reduce LLM translation errors and API call costs.

1. Extracts commits from the Merge Request to identify changes.
2. Uses the commits to extract the pre-change Korean file and the post-change Korean file.
3. Parses the pre-change Korean file, post-change Korean file, and pre-change multilingual file using a Custom Parser to structure them.
4. Analyzes the differences between the structures of the pre-change and post-change Korean files.
5. Calls the translation API to translate only the identified differences.
6. Applies the translated differences to the pre-change multilingual file to generate the post-change multilingual file.
7. Restructures the post-change multilingual file back into the original Markdown file.
8. Saves the Markdown file in the directory.

### powershell/deploy-docs/v7

This is a Windows PowerShell script that automatically builds documents in a GitLab-based environment.

1. deploy-doc: Deploys Korean or English documents for commercial distribution.
2. deploy-doc-tr: Deploys multilingual documents (other than Korean and English) for commercial distribution.
3. deploy-preview: Deploys previews of Korean or English documents.
4. remove-preview: Deletes the deployed preview.
5. checkout-to-last-tag: Searches for all tags containing a specific word, returns the latest tag among them, and checks out a new branch based on this tag.

### process-html, process-markdown

These are codes for processing and saving HTML and Markdown files according to my requirements.

### skip-translations/python/v7

This code is designed to handle specific English words so that they are not translated into other languages (like Chinese).

1. Parses the Korean document to extract only the English words.
   1. Creates and saves a list of English proper nouns for each Korean file. (`createSkipListV7.py`)
2. Treats the English words within the Korean text as proper nouns and decides not to translate them into other languages.
3. Finds these words in each English document and wraps them with the `<span class="notransate">` tag. (`applySkipListsFromDirV7.py`)
4. Implements this functionality in a GUI. (`skipTranslationV7.py`)

### update-links

This code generates a graph where each Markdown page is a node, and links (relative links) to other pages are the edges.

* There can be multiple edges between nodes (pages).
* Different named anchors are treated as distinct edges.

This code is still under development, and the following features are planned for future addition:

1. Periodically reads the entire developer guide to maintain an up-to-date graph.
2. Tracks changes in the developer guide (such as page deletions, additions, or named anchor renaming) to detect changes in edges (links) and automatically updates the graph.
3. Applies the modified graph to the developer guide (automatically modifies relative links).

