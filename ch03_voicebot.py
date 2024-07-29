# FFmpeg.zip 파일 설치 후 python path에 경로 추가 작업 진행함 ! #



##### 기본 정보 입력 #####
import streamlit as st
# audiorecorder 패키지 추가
from audiorecorder import audiorecorder
# OpenAI 패키지 추가
import openai
# 파일 삭제를 위한 패키지 추가
import os
# 시간 정보를 위한 패키지 추가
from datetime import datetime
# TTS 패키기 추가
from gtts import gTTS
# 음원 파일 재생을 위한 패키지 추가
import base64
# 오디오 파일의 처리를 위한 패키지 추가
from pydub import AudioSegment   

#### 기능 구현 함수 ####

# 음성 파일 입력받아 텍스트로 변환하는 함수
def STT(audio, apikey):
    # 파일 저장
    filename = 'input.wav' # format = "wav"
    audio.export(filename, format="wav")  # Whisper 모델은 '파일 형태'의 음원 입력받음 / 
    
    # 오디오 파일 열기
    with open(filename, "rb") as audio_file:
        # Whisper 모델을 활용해 텍스트 얻기
        client = openai.OpenAI(api_key=apikey)
        response = client.audio.transcriptions.create(model="whisper-1", file=audio_file)  # Whisper-1 모델 사용
    
    # 파일 삭제
    os.remove(filename)
    
    # Transcription 객체에서 텍스트 추출
    # response는 Transcription 객체로 가정
    try:
        transcription_text = response.text  # 음성 파일을 텍스트로 변환
    except AttributeError:
        transcription_text = "Transcription text not found."
    
    return transcription_text

# ChatGPT API 활용하여 답변 구하는 함수
def ask_gpt(prompt, model,apikey):
    client = openai.OpenAI(api_key=apikey)
     
    # ChatCompletion API 호출
    response = client.chat.completions.create(model=model, messages=prompt)
    
     # 'choices' 리스트에서 첫 번째 항목의 'message' 속성에서 'content'를 추출
    try:
         # response.choices[0].message는 객체이며 서브스크립트 방식으로 접근할 수 없음
        gptResponse = response.choices[0].message.content   # GPT의 답변 중 첫번째로 선택된 것을 저장 
    except (IndexError, KeyError) as e:
        gptResponse = f"Error retrieving response: {str(e)}"
    
    return gptResponse

# gTTS로 텍스트 답변을 음성파일로 변환하여 재생하는 함수
def TTS(response):
    # gTTS 를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response,lang="ko")
    tts.save(filename)

    # ChatGPT 답변으로 생성한 음원 파일을 자동 재생하도록 구현
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()   # 음원파일 인코딩 및 디코딩 
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio mp3"> 
            </audio>
            """  #gTTS는 mp3 포맷으로만 음성 파일 저장 가능.
        st.markdown(md,unsafe_allow_html=True,)
    # 파일 삭제
    os.remove(filename)

##### 기본 설명 영역 #####
  #### 메인 함수 ####
def main():
    # 기본 설정
    st.set_page_config(
        page_title="음성 비서 프로그램",
        layout="wide"
    )

    # session_state 없을 시 초기화
    if "chat" not in st.session_state:     # "chat" 키 : 사용자와 음성비서의 대화 내용 저장, 채팅창에 표시
        st.session_state["chat"] = []

    if "messages" not in st.session_state:      # "message" 카 : GPT API에 전달할 프롬프트 양식 
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_reset" not in st.session_state:       # "check_reset" 키 사용자가 리셋 버튼을 클릭한 상태를 나타내는 플래그 
        st.session_state["check_reset"] = False

    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""  # 기본값을 빈 문자열로 설정

    # 제목
    st.header("음성 비서 프로그램")
    st.markdown("---")

    # 기본 설명
    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
        """     
        - 음성비서 프로그램의 UI는 스트림릿을 활용했습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용했습니다. 
        - 답변은 OpenAI의 GPT 모델을 활용했습니다. 
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용했습니다.
        """
        )
        st.markdown("")

    # 사이드바 생성
    with st.sidebar:
        # Open AI API 키 입력받기
        st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value=st.session_state["OPENAI_API"], type="password")

        st.markdown("---")

        # GPT 모델 선택을 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        # 리셋 버튼 생성
        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True
            
    # 기능 구현 영역
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")  # 녹음하기 버튼 '클릭 전','클릭 후' 문구
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # 음원 재생
            st.audio(audio.export().read())
            # 음원파일에서 텍스트 추출
            question = STT(audio, st.session_state["OPENAI_API"])
            
            # 채팅 시각화 위해 질문 내용 저장 
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            # GPT 모델에 넣을 프롬프트 위한 질문 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]

    with col2:
        st.subheader("질문/답변")
        # 리셋 조건 아닐 경우, 응답 생성
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # GPT에게 답변 반환받아 변수에 저장
            response = ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])
             # Chat GPT에 전달한 프로프트를 위해 질문 내용을 "messages"키에 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]

            # 채팅 시각화를 위한 질문 내용을 "chat" 키에 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # 채팅 형식으로 시각화하기
            for sender, time, message in st.session_state["chat"]:   # "chat"키에 저장된 내용을 '대화주체','대화생성시각','대화내용' 변수로 각각 받기
                if sender == "user":  # 대화주체가 'user(사용자)' -> 파란 배경
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:    # 아닐 경우 -> 회색 배경
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")

    # gTTS 활용하여 음성 파일 생성 및 재생
            TTS(response)
        else:
            st.session_state["check_reset"] = False

if __name__ == "__main__":
    main()
