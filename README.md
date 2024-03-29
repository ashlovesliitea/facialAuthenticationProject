[Face ID를 이용한 2-Step 보안 인증 시스템]<br>
Team Project
 1) Deep-learning Engineer : 조수민 @sm991105
 2) Back-End Engineer: 이지율 @ashlovesliitea
 3) Front-End Engineer: 신예빈 @syb0228
 
 => 관리자의 노트북/컴퓨터 등의 디바이스에 가상환경을 세팅하고 코드를 실행하면, 해당 디바이스가 서버 컴퓨터가 되고, 외부 도메인을 통해서 출입자가 외부에서도 접속하여 회원가입/ 1차 인증이 가능하며, 회원가입 시에 등록한 사진 8장을 통해 회원의 얼굴 정보를 추출하여 딥러닝한 데이터베이스를 바탕으로 2차인증을 진행하게 되는데, 1차 인증 후에 관리자의 노트북 카메라에 얼굴을 인식하면 관리자의 서버에 저장되어있는 얼굴 데이터베이스와 대조하여 face_recognition 모델을 이용한 2차 인증을 실행할 수 있는 프로그램이다. 따로 장비나 보안 시스템 설치 없이 관리자의 노트북 디바이스 하나면 시스템을 간편하게 이용할 수 있다.


[세팅 방법] 
1. 2차 인증을 진행할 컴퓨터에 가상환경을 세팅해야 한다. (windows 10 기준)

2. 원하는 곳에 프로젝트를 진행할 폴더를 생성한다. 해당 폴더의 주소를 복사해둔다. 

3. windows powershell을 open하고
   1) cd (프로젝트 폴더 주소)
   2) pip install virtualenv
   3) python -m pip install --upgrade pip
   4) virtualenv venv
   5) cd venv/bin
   6) .\activate => 가상환경 venv가 실행된다.

4. github에 있는 소스를 그대로 다운받아 해당 프로젝트 폴더에 압축을 풀어주고, face_recognition 모듈을 설치해줍니다.
   1) cd (프로젝트 폴더 주소)
   2) git clone 
   2) pip install cmake
   3) git clone https://github.com/ageitgey/face_recognition.git
   4) cd face_recognition
   5) python setup.py install
   => dlib, numpy, face_recognition 까지 설치가 끝납니다.

6. 마지막으로 필요한 모듈들을 모두 설치해 줍니다. 
   1) cd ..
   2) pip install --upgrade pip
   3) pip install -r requirements.txt

7. 메인 코드를 실행해줌으로써 서버 구동은 끝납니다. 
   1) python main.py => 서버 컴퓨터에서 컴퓨터가 실행됩니다.

8. 마지막으로 외부에서도 접속할 수 있도록 도메인을 만들어주기 위해 ngrok이라는 
프로그램을 다운받습니다.
   1) ngrok 다운로드 (https://ngrok.com/download)
   2) 명령 프롬프트 cmd로(powershell 아님) 들어갑니다.
   3) cd (ngrok파일 저장된 주소)
   4) ngrok http 9000
   => 9000번 포트를 열어준 다음에 할당된 외부 도메인 주소(https://(할당주소).ngrok.io)을 이용해 접속하면 완성.
   
<br><br>
[시연 동영상]
 : https://youtu.be/VDNqm0NoIQ8 에서 확인하실 수 있습니다.
 
 <br>
 [기술 요약서]
 인하대학교 IT 경진대회 동상 수상작: https://docs.google.com/document/d/1TYGcXFsMFMUevgaA9ockUKA0g8F1sEgu_uxlOxTzsv0/edit?userstoinvite=happydaram%40gmail.com
