# Extract ppt(pdf) from lecture videos

1. 서론


“Extract PDF from lecture videos”는 강의 영상으로부터 PDF를 자동으로 추출해주는 서비스이다. 많은 대학생들이 학교 수업에서 사용된 PPT 자료를 제공받지 못하고 있는 현실에서, 강의 영상으로부터 PPT 자료를 자동으로 추출할 수 있으면 좋을 것 같다는 생각에 ‘Extract PDF from lecture videos’ 라는 주제를 생각하게 되었다.
기존에 존재하는 소프트웨어(slid)가 있어, 이번 캡스톤 프로젝트만의 차별성을 만들고자 했다. 첫째로,  slid는 수동으로 슬라이드를 고르는 방식이었는데, 이번 캡스톤에서는 알고리즘이 자동으로 강의 화면으로부터 필기 프레임을 골라서 PDF를 추출하는 방식을 채택했다. 두번째로, slid는 실시간(zoom 같은)이 아닌 환경에서 실행되는데, 이번 프로젝트는 실시간 강의에 활용할 수 있도록 했다. ‘Extract PDF from lecture video’는 학생들에게 수업에서 사용된 PPT 자료가 제공되지 않는 경우 또는 교수자의 필기가 포함된 자료를 보면서 공부하고 싶은 경우에 도움이 될 뿐만 아니라, 교수자가 직접 PPT 자료를 올려야 하는 번거로움을 줄일 수 있다.
이를 구현하기 위해 크게 두 부분으로 프로젝트를 나누었다. 사용자가 직접 사용할 수 있는 파이썬 프로그램(로컬)과 실시간 강의 스트리밍 환경을 구현한 서버가 이에 해당한다. 사용자에게 하나의 방식을 강요하는 것이 아니라, 강의 영상에 알고리즘을 적용하여 자동으로 PDF를 추출하는 다양한 방안을 제공하고 사용자가 원하는 방식을 취사 선택하여 사용하는 것이 ‘Extract pdf from lecture videos’가 추구하는 최종 목표이다.

2. 기존 연구 현황
- Slid (구글 확장 플러그인) : 캡처 버튼을 통해 강의 화면을 직접 노트에 추가하고 필기를 덧붙일 수 있다.

- FFMPEG과 같은 video encoder에서 keyframe을 사용하여 슬라이드를 영상으로부터 추출할 수 있다. (다만 매우 낮은 정확도를 보인다. - 강의 슬라이드에 비해 터무니 없이 많은 장수의 슬라이드 추출 결과를 보인다.)

3. 역할 분담
본 프로젝트 수행 시 역할분담은 다음과 같다.
•	공통 : PDF 추출 알고리즘 개발
•	박상엽 : 파이썬 프로그램
•	이동현 : 실시간 서버 백엔드
•	한경빈 : 실시간 서버 프론트엔드
4. 필기본 PDF 추출 알고리즘 설명
인접 프레임 비교 알고리즘으로, 자주 사용되는 이미지 비교 알고리즘에는 SSIM (Structural Similarity), MSE (Mean Squared Error) 중 MSE 방식을 선택하여 사용하였다. 이미지의 명암, 질감 등의 구조적 유사성을 비교하는 SSIM 방식의 경우 MSE와 비교했을 때 연산량이 큰 편에 속하고, MSE 방식을 사용하더라도 프레임 감지에는 문제가 없을 정도의 정확도가 확인되었다. 그 이유는 강의 영상 프레임을 구분하는데 명암과 질감이 크게 필요없기 때문이다. 따라서, 인접 프레임 비교에는 비용이 비교적 저렴한 MSE를 사용하게 되었다. 또한, MSE를 바로 사용하는 것이 아니라, 강의 영상의 특성을 고려하여 이미지를 16등분한 후 각 이미지에 MSE 방식을 적용하고, 그 결과를 토대로 프레임을 판단하였다. 이를 통해 많은 이점을 얻을 수 있었는데, 예시로 강의 화면에 웹 카메라가 구석에 있는 경우 MSE 방식을 이미지 등분 없이 사용하면 카메라에 많은 변화가 있을 때 다른 슬라이드로 잘못 판단할 여지가 생기지만, 이미지를 등분하여 사용할 경우 웹 카메라 부분의 이미지 한 조각만 다른 부분으로 판단되기 때문에 알고리즘의 오작동을 예방할 수 있다.
예외처리로는 앞 슬라이드 전환, 지워짐 감지를 구현했다. 먼저, 앞 슬라이드 전환에 대해서 말하자면, 알고리즘이 새로운 슬라이드를 감지하면 따로 저장(새슬라이드의 원본)하고, 필기 화면을 저장할 때 원본 슬라이드 번호를 같이 저장하여 중복 프레임 저장(앞으로 돌아갈 때)을 방지하였다. 
다음으로, 필기가 지워지는 경우에 대한 설명이다. 슬라이드 원본 프레임과 전 프레임을 비교하여 필기되어 있는 조각을 임시 저장한 후 (ㄱ) 에, 원본 슬라이드 프레임과 현 프레임을 비교하여  차이를 감지(ㄴ)하여 (ㄱ) 필기 부분이 (ㄴ) 에서는 필기부분으로 감지 되지 않으면 필기가 지워졌다고 판단했다.
또한 알고리즘이 미처 잡아 내지 못한 오류가 존재하더라도, 사용자가 원하는 슬라이드만 저장하게 하면 이를 해결할 수 있을 것으로 기대한다.

5. 테스트
python-opencv를 활용하여 알고리즘을 구현했고, 영상의 해상도, 화질, 길이, 슬라이드 장수, 디자인, 애니메이션, 화면의 움직임 정도 등 다양한 기준을 바탕으로 여러 환경을 모두 충족시킬 수 있는 테스트 표본 영상 10개를 선정하여 정확도 테스트를 진행하였다. 각 표본 영상마다 사람이 직접 추출한 슬라이드와 알고리즘이 추출해준 PDF 자료를 비교 분석한 결과 정확도는 평균 93.18%, 표준편차는 10.48로 나타났고, 직접 추출한 슬라이드 장수와 추출된 PDF의 슬라이드 장수는 각각 평균 8.8장, 표준편차 4.58 및 평균 13.1장, 표준편차 7.3으로 나타났다. 아래는 표본 영상 8에 대한 PDF 추출 결과이다.
 
이렇게 개발한 알고리즘을 파이썬 프로그램과 실시간 강의 스트리밍 서버, 두 가지 방안에 각각 적용하여 사용자에게 더욱 편리한 서비스를 제공했다.

6. 파이썬 프로그램
사용자가 실시간 강의나 강의 영상 시청 시 직접 사용할 수 있는 프로그램이고, tkinter를 사용하여 UI를 간단하게 구성하였다. 사용자가 직접 화면 녹화 범위를 설정한 뒤 start 버튼을 누르면 모니터 화면을 실시간으로 녹화하며, 일정 주기마다 화면을 자동으로 캡처하여 알고리즘을 적용시키고, PDF에 넣어야 할 프레임인지 판별한다. stop버튼을 누르면 녹화가 종료되고, 사용자는 UI를 통해 PDF에서 제외할 슬라이드를 선택할 수 있다.


7. 실시간 강의 스트리밍 서버
실시간 비디오 교환을 구현하기 위해, webrtc를 사용했다. Signaling 작업(webrtc에서 실시간 비디오 교환을 위한 선행 작업이다.) 을 모두 마치고 연결된 학생과 교수는 실시간으로 비디오를 교환하게 된다. 이 때, 교수가 원할 때부터 녹화를 시작(recording start 버튼 클릭)하여 강의 영상 프레임을 서버에 전달하고, 필기본에 넣어야 할 프레임 인지는 서버가 판별한다. 이 때 , 모든 프레임을 서버에 전송하는 것은 아니며 n프레임(조절 가능) 당 1 개씩 서버에 보낸다. 즉, 서버는 프레임를 받고 전 프레임이나 저장된 프레임과 비교 하는 것으로 생각하면 된다.
	그다음, 교수가 recording stop 하면 프레임 전송이 중지 되고, 서버는 선별한 프레임(이미지)들을 pdf 파일 한 개로 변환 한다음, 학생에게 전달한다.(리다이렉트) 그렇게 되면, 학생은 필기본 pdf 파일을 받게 되는 것이다. 
 
8. 기대 효과
본 서비스는 수업 PPT 자료를 제공받지 못하는 대학생들을 대상으로 개발되었다. 강의 영상으로부터 PDF를 추출하거나 실시간 강의에 적용함으로써 수업 자료를 받기(혹은 제공하기) 위해 학생들이나 교수자들이 추가적인 노력을 들일 필요가 없다. 온라인 강의 업로드 시 서버에서 알고리즘을 적용하여 PDF 자료를 부가적으로 제공할 수도 있고, 더 이상 실시간 강의 화면을 하나하나 캡처할 필요가 없다. 무료로 본 서비스를 배포하고 앞으로 계속해서 발전시켜 나간다면, 많은 사람들이 PDF 추출 서비스를 이용할 수 있을 것으로 기대된다.


9. 결과물
1) 파이썬 프로그램
강의 영상 녹화
 ![image](https://user-images.githubusercontent.com/76900144/145259156-df808246-9455-41e1-8c3d-ef1b6cc4ba4f.png)

슬라이드 열람, 선택 및 PDF 저장
 ![image](https://user-images.githubusercontent.com/76900144/145259190-83b7541a-d95a-43d4-9221-1251914701bc.png)
![image](https://user-images.githubusercontent.com/76900144/145259221-263de139-fbf0-4c38-b7f7-ad72724913a0.png)


2) 실시간 스트리밍 서버
실시간 강의 스트리밍
 ![image](https://user-images.githubusercontent.com/76900144/145259257-bcb21238-4c03-4d47-947d-2f5407b4db8d.png)

실시간 강의 스트리밍 종료
 ![image](https://user-images.githubusercontent.com/76900144/145259283-9860fc60-7cb2-4baf-9d16-2e22a7853ca8.png)

 
PDF 추출 결과
![image](https://user-images.githubusercontent.com/76900144/145259306-eb4b1d45-939e-48d0-9f11-d372650271ee.png)

