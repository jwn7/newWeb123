# 사용할 기본 이미지 지정 (Python 3.9의 가벼운 버전)
# 게시판 프로젝트이므로 필요한 파이썬 버전이 설치된 이미지를 사용합니다.
FROM python:3.9-slim

# 컨테이너 내부에서 작업할 디렉토리를 /app으로 설정
WORKDIR /app

# 호스트(로컬)의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사
# 게시판 프로젝트에서 사용하는 Flask 외 다른 라이브러리 (DB 드라이버 등) 목록이
# 이 파일에 정확히 담겨 있어야 합니다.
COPY requirements.txt .

# requirements.txt에 명시된 파이썬 패키지 설치
# 이 단계에서 게시판 운영에 필요한 모든 라이브러리 (Flask, DB 라이브러리, WTForms 등)가 설치됩니다.
RUN pip install --no-cache-dir -r requirements.txt

# 호스트(로컬)의 모든 파일/폴더를 컨테이너의 현재 작업 디렉토리(/app)로 복사
# 여기에는 플라스크 앱 코드, 템플릿 파일, 정적 파일 등 게시판 프로젝트의 모든 소스 코드가 포함됩니다.
COPY . .

# Flask 애플리케이션이 사용할 포트(기본 5000)를 외부에 노출하도록 설정
EXPOSE 5000

# 컨테이너가 시작될 때 실행될 명령어 설정 (Gunicorn을 사용하여 앱 실행)
# 'your_app_file_name' 부분은 Flask 앱 객체가 정의된 .py 파일 이름으로 변경하세요.
# 'app' 부분은 Flask 앱 객체의 변수 이름으로 변경하세요.
# 게시판 프로젝트의 메인 진입점(entry point)에 맞게 수정해야 합니다.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

# 만약 개발 서버로 실행하려면 (프로덕션에서는 사용하지 마세요!):
# CMD ["python", "your_app_file_name.py"]