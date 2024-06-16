import openai
import streamlit as st
import base64
import requests
from openai import OpenAI


# OpenAI API Key 설정
api_key = st.secrets["API_KEY"]
openai.api_key = api_key
client = OpenAI(api_key=api_key)



keyword = """
나는 시각장애인이라 앞이안보여 제발 부탁할게

우선 등장인물의 얼굴 특성을 오목조목 분석해줘.

그리고 얼굴 특성을 분석으로 관상을 바탕으로 성격, 가치관을 파악해줘. 여기를 자세히 묘사해줘야해.

그리고 성격, 가치관을 바탕으로 여행가기에 좋은 나라를 추천해줘.

그리고 그 나라를 여행하다보면 어떤 것을 얻게 될지 알려줘.

그리고 여행 목적을 바탕으로 그 국가에서 꼭 가봐야하는 여행장소를 구체적으로 주소까지 알려줘. 여행지를 추천할 때는 도시 전체를 추천하지 말고 특정한 장소를 알려줘.

그리고 꼭 해봐야하는 체험, 경험들을 알려줘

말투는 친구한테하듯이 친근하게해줘 앞뒤에 미안하다는말은 안해도 돼"""
st.title("나에게로 떠나는 여행")

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# 입력 섹션
with st.expander("입력하기"):
    # keyword = st.text_input("키워드를 입력하세요")
    uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
    
if uploaded_file is not None:
    # 업로드된 이미지 표시
    st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)
else:
    st.write("이미지를 업로드하세요.")    

# 이미지 인코딩 함수
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# 이전 대화 내용 표시
for message in st.session_state['messages']:
    if message['role'] == 'user':
        # st.write(f"User: {message['content']}")
        pass
    else:
        # st.write(f"GPT-4: {message['content']}")
        pass

if st.button("생성하기"):
    if True:
        with st.spinner("생성 중입니다."):
            messages = [{"role": "user", "content": keyword}]
            st.session_state['messages'].append({"role": "user", "content": keyword})

            if uploaded_file is not None:
                base64_image = encode_image(uploaded_file)
                messages.append(
                    {
                        "role": "user",
                        "content": f"data:image/jpeg;base64,{base64_image}"
                    }
                )
                st.session_state['messages'].append({"role": "user", "content": "이미지 업로드됨"})

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            if uploaded_file is None:
                payload = {
                    "model": "gpt-4o",
                    "messages": st.session_state['messages'],
                    "max_tokens": 3000,
                }
            else :
                payload = {
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": keyword
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 3000,
                }

            # API 요청
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response2 = client.images.generate(
                model="dall-e-3",
                prompt=response.json()['choices'][0]['message']['content'] + "  앞의 대화에서 나오는 사람이 그 사람이 너가 추천해준 여행 갈 나라의 랜드마크앞에 있는 사진을 만들어줘 랜드마크는 배경으로 크게 들어가게 해줘 사진을 만들어줘 앞의 대화 묘사처럼 최대한 자세히 1장짜리 깔끔한 이미지로 만들어줘",
                size="1024x1024",
                quality="hd",
                n=1
            )
            
            response3 = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": response.json()['choices'][0]['message']['content'] + "이 대화를 기반으로 가장 효율적으로 머무를 수 있는 근처 숙소 정보 및 가격을 알려줘 그리고 숙소와 여행지를 이동하는 경로를 효율적으로 짜줘 경로 지도를 html파일로 만들어줘"
                                }
                            ],
                        }
                    ],
                    "max_tokens": 3000,
                },
            )
            st.image(response2.data[0].url)
            image_url = response2.data[0].url
            st.session_state.image_url = image_url
            

            # print(response.json()['choices'][0]['message']['content'] + "  앞의 대화에서 나오는 사람이 그 사람이 사는 나라의 랜드마크에 있는 사진을 만들어줘 앞의 대화 묘사처럼 최대한 자세히 만들어줘")
            print(response2.json())
            # print(response2.json())
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                # st.write(result)
                st.session_state['messages'].append({'role': 'assistant', 'content': result})
                st.write(result)
                st.write(response3.json()['choices'][0]['message']['content'])
                html_code = f"<img src='{st.session_state.image_url}' width='600'>"
                st.markdown(html_code, unsafe_allow_html=True)
                # st.rerun()
            else:
                st.error("API 요청 실패. 다시 시도해 주세요.")
    else:
        st.error("키워드를 입력해주세요.")

        

