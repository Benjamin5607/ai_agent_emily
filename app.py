import streamlit as st
from groq import Groq

# 1. 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="Emily AI Agent", layout="centered")

# 2. 클라이언트 초기화 (Streamlit Secrets에서 API 키 로드)
# 팁: Streamlit Cloud 설정(Settings) -> Secrets에 GROQ_API_KEY="내키" 입력 필수!
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

# 3. 모델 리스트 동적 로드 함수
@st.cache_data(ttl=3600) # 1시간마다 갱신
def get_groq_models():
    try:
        models = client.models.list()
        # 사용 가능한 주요 모델 필터링 (Llama3, Mixtral 등)
        return [m.id for m in models.data if "whisper" not in m.id and "preview" not in m.id]
    except:
        return ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]

# 4. 사이드바: 모델 및 설정 (모바일은 왼쪽 상단 '>' 클릭)
model_list = get_groq_models()
with st.sidebar:
    st.title("⚙️ 에밀리 설정")
    selected_model = st.selectbox("두뇌(모델) 선택", model_list, index=0)
    temp = st.slider("창의성 레벨", 0.0, 1.0, 0.7, step=0.1)
    st.divider()
    st.caption("Emily v1.0 | Powered by Groq LPU")

# 5. 메인 화면 UI
st.title("🚀 AI 에이전트: 에밀리")
st.markdown("아이디어를 던지면 **설계부터 평가까지** 실무를 대행합니다.")

idea = st.text_area("💡 당신의 아이디어를 적어주세요", 
                    placeholder="예: 반려동물 건강 상태를 분석해주는 AI 스마트 급식기 서비스",
                    height=150)

# 6. 에이전트 실행 로직
def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": f"당신은 전문 {role} 에밀리입니다. 모든 답변은 한국어로, 모바일 가독성을 위해 짧은 문장과 불렛포인트, 표를 활용하세요."},
                {"role": "user", "content": f"맥락: {context}\n\n작업: {task}"}
            ],
            temperature=temp,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"에러 발생: {str(e)}"

if st.button("✨ 에밀리 실무 프로세스 시작", use_container_width=True):
    if not idea:
        st.warning("아이디어를 입력해야 시작할 수 있어요!")
    else:
        # 단계별 태스크 정의
        steps = [
            ("🏗️ 서비스 설계", "이 아이디어의 핵심 아키텍처와 필수 기능 리스트를 짜줘."),
            ("📊 시장 및 데이터 분석", "타겟 고객 페르소나와 예상 수익 모델을 분석해줘."),
            ("📅 실행 플랜 (WBS)", "초기 구축부터 런칭까지 4주간의 타임라인을 표로 그려줘."),
            ("⚙️ 운영 및 마케팅", "초기 유저 확보를 위한 운영 전략과 마케팅 채널을 제안해줘."),
            ("📈 성과 평가", "이 프로젝트의 성공을 측정할 핵심 지표(KPI) 3가지를 정해줘.")
        ]
        
        progress_bar = st.progress(0)
        full_context = f"사용자 아이디어: {idea}"
        
        for i, (step_name, task) in enumerate(steps):
            with st.status(f"에밀리가 {step_name} 중...", expanded=True):
                result = run_agent_step(step_name, task, full_context)
                st.markdown(result)
                full_context += f"\n\n[{step_name}]\n{result}"
            
            # 진행률 업데이트
            progress_bar.progress((i + 1) / len(steps))
            
        st.balloons()
        st.success("✅ 모든 실무 기획이 완료되었습니다!")
