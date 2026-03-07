import streamlit as st
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="Emily AI: Full-Stack Agent", layout="centered")

# --- UI 커스터마이징 (Personalization) ---
# 사이드바에서 선택한 색상을 앱 전체 배경에 적용하는 CSS 인젝션
with st.sidebar:
    st.title("🎨 에밀리 개인화 설정")
    bg_color = st.color_picker("앱 배경색 선택", "#F0F2F6")
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {bg_color};
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.header("⚙️ 에이전트 두뇌 설정")
    # 언어 선택 기능 추가
    language = st.selectbox("🌐 출력 언어 (Language)", ["한국어", "English", "Bahasa Melayu", "Tiếng Việt"])
    
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

@st.cache_data(ttl=3600)
def get_groq_models():
    try:
        models = client.models.list()
        return [m.id for m in models.data if "whisper" not in m.id and "preview" not in m.id]
    except:
        return ["llama3-70b-8192", "llama3-8b-8192"]

with st.sidebar:
    selected_model = st.selectbox("두뇌(모델) 선택", get_groq_models(), index=0)
    temp = st.slider("창의성 레벨", 0.0, 1.0, 0.7, step=0.1)
    
    st.divider()
    st.caption("Emily v2.0 | Full-Stack & Marketer")

# 2. 메인 화면 UI
st.title("🚀 AI 에이전트: 에밀리 v2.0")
st.markdown("아이디어 기획, **코드 작성**, **소셜 미디어 관리**까지 한 번에!")

idea = st.text_area("💡 아이디어 또는 요청사항을 적어주세요", 
                    placeholder="예: 커피 농장 리뷰 앱을 플러터로 만들고 싶어. UI 구성이랑 홍보 포스팅도 짜줘.",
                    height=120)

# 옵션 선택 (코드 생성, SNS 관리 포함 여부)
col1, col2 = st.columns(2)
with col1:
    need_code = st.checkbox("💻 개발 코드 포함 (프론트/백엔드)")
with col2:
    need_sns = st.checkbox("📱 소셜 미디어 포스팅 자동 생성")

# 3. 에이전트 실행 로직
def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": f"당신은 최고 수준의 {role}입니다. 모든 답변은 반드시 '{language}'로 작성하세요. 모바일 가독성을 위해 마크다운과 코드 블록을 적극 활용하세요."},
                {"role": "user", "content": f"전체 문맥: {context}\n\n현재 할 일: {task}"}
            ],
            temperature=temp,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"에러 발생: {str(e)}"

if st.button("✨ 에밀리 통합 워크플로우 시작", use_container_width=True):
    if not idea:
        st.warning("내용을 입력해야 시작할 수 있어요!")
    else:
        # 기본 기획 스텝
        steps = [
            ("🏗️ 서비스 아키텍처", "이 아이디어의 시스템 구조와 핵심 기능 명세서를 작성해줘."),
            ("📅 프로젝트 플래닝", "이 프로젝트를 완성하기 위한 단계별 로드맵을 짜줘.")
        ]
        
        # 유저 선택에 따라 동적으로 스텝 추가!
        if need_code:
            steps.append(("💻 풀스택 리드 개발자", "이 서비스를 구현하기 위한 핵심 코드 구조(예: 플러터 UI 위젯 뼈대, 데이터베이스 스키마)를 작성해줘."))
        if need_sns:
            steps.append(("📱 소셜 미디어 매니저", "이 서비스(또는 브랜드)를 홍보하기 위한 인스타그램, 링크드인용 게시글 초안과 타겟 해시태그를 생성해줘."))
            
        progress_bar = st.progress(0)
        full_context = f"사용자 요청: {idea}"
        
        for i, (step_name, task) in enumerate(steps):
            with st.status(f"에밀리가 {step_name} 작업 중...", expanded=True):
                result = run_agent_step(step_name, task, full_context)
                st.markdown(result)
                full_context += f"\n\n[{step_name}]\n{result}"
            
            progress_bar.progress((i + 1) / len(steps))
            
        st.balloons()
        st.success("✅ 에밀리가 모든 실무 및 개발, 마케팅 준비를 마쳤습니다!")
