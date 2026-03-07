import streamlit as st
import base64
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="Emily AI: PM & Marketer", layout="wide")

# ==========================================
# Groq 클라이언트 초기화 및 모델 로드
# ==========================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API 키가 없습니다. Streamlit Secrets에 GROQ_API_KEY를 설정하세요.")
    st.stop()

@st.cache_data(ttl=3600)
def get_groq_models():
    try:
        models = client.models.list()
        return [m.id for m in models.data if "whisper" not in m.id and "preview" not in m.id]
    except:
        return ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]

# ==========================================
# 사이드바 (개인화 & API & 모델 설정)
# ==========================================
with st.sidebar:
    st.title("⚙️ 에밀리 설정 패널")
    
    # [복구 완료!] 모델 선택 및 창의성 설정
    st.header("🧠 에이전트 두뇌 설정")
    selected_model = st.selectbox("모델 선택", get_groq_models(), index=0)
    temp = st.slider("창의성 레벨 (Temperature)", 0.0, 1.0, 0.7, step=0.1)
    
    st.divider()
    
    # 배경화면 설정
    st.header("🎨 배경화면 커스텀")
    bg_upload = st.file_uploader("로컬 이미지 선택 (PNG, JPG)", type=['png', 'jpg', 'jpeg'])
    if bg_upload is not None:
        base64_img = base64.b64encode(bg_upload.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{base64_img}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .main {{ background-color: rgba(255, 255, 255, 0.85); padding: 20px; border-radius: 10px; }}
            </style>
            """, unsafe_allow_html=True
        )
    else:
        bg_color = st.color_picker("배경색 지정 (이미지 없을 시)", "#F0F2F6")
        st.markdown(f"<style>.stApp {{ background-color: {bg_color}; }}</style>", unsafe_allow_html=True)
        
    st.divider()

    # 소셜 미디어 API
    st.header("🔑 소셜 미디어 API (로컬 캐시)")
    if "sns_keys" not in st.session_state:
        st.session_state.sns_keys = {"instagram": "", "linkedin": ""}
    
    st.session_state.sns_keys["instagram"] = st.text_input("Instagram API Key", type="password", value=st.session_state.sns_keys["instagram"])
    st.session_state.sns_keys["linkedin"] = st.text_input("LinkedIn API Key", type="password", value=st.session_state.sns_keys["linkedin"])
    
    st.divider()

    # PM 방법론 선택
    st.header("📊 프로젝트 관리 (PM) 기법")
    pm_method = st.selectbox("PM 방법론", ["Agile (애자일)", "Scrum (스크럼)", "Kanban (칸반)", "Waterfall (워터폴)"])

# ==========================================
# 메인 화면 UI
# ==========================================
st.title("🚀 AI PM 에이전트: 에밀리 v3.1")
st.markdown(f"**현재 두뇌:** `{selected_model}` | **관리 기법:** `{pm_method}`")

idea = st.text_area("💡 진행할 프로젝트 아이디어나 목표를 적어주세요.", 
                    placeholder="예: AI 기반 다이어트 앱 기획 및 런칭",
                    height=120)

col1, col2 = st.columns(2)
with col1:
    need_code = st.checkbox("💻 핵심 기능 개발 코드 작성 (FE/BE)")
with col2:
    need_sns = st.checkbox("📱 소셜 미디어 포스팅 자동 생성 및 배포 시뮬레이션")

# ==========================================
# 에이전트 실행 로직
# ==========================================
def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model, # 유저가 선택한 모델이 여기에 들어갑니다!
            messages=[
                {"role": "system", "content": f"당신은 최고 수준의 {role}입니다. 마크다운을 적극 활용하고 가독성을 높이세요."},
                {"role": "user", "content": f"전체 문맥: {context}\n\n현재 할 일: {task}"}
            ],
            temperature=temp, # 유저가 설정한 온도(창의성) 반영!
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"에러 발생: {str(e)}"

if st.button("✨ 에밀리 PM 가동 시작!", use_container_width=True):
    if not idea:
        st.warning("프로젝트 내용을 입력해야 시작할 수 있어요!")
    else:
        st.write("---")
        progress_bar = st.progress(0)
        full_context = f"사용자 프로젝트: {idea}\n관리 방법론: {pm_method}"
        
        pm_prompt = f"이 프로젝트를 '{pm_method}' 방법론에 맞춰서 완벽하게 기획해줘. "
        if "Kanban" in pm_method:
            pm_prompt += "반드시 [To Do], [In Progress], [Done] 형식의 칸반 보드 텍스트 UI를 그려줘."
        elif "Scrum" in pm_method:
            pm_prompt += "Sprint 1, Sprint 2 형식으로 백로그(Backlog)와 태스크를 나누어줘."
        elif "Agile" in pm_method:
            pm_prompt += "사용자 스토리(User Story)와 에픽(Epic) 단위로 빠르게 이터레이션(Iteration)할 수 있는 계획을 짜줘."
        else:
            pm_prompt += "요구사항 분석 -> 설계 -> 구현 -> 테스트 -> 유지보수의 엄격한 폭포수 단계별로 일정을 짜줘."

        steps = [
            ("📊 프로젝트 매니저 (PM)", pm_prompt),
            ("🏗️ 시스템 아키텍트", "위 계획을 바탕으로 서비스의 기술 스택과 데이터베이스 스키마를 설계해줘.")
        ]
        
        if need_code:
            steps.append(("💻 리드 소프트웨어 엔지니어", "핵심 기능을 보여줄 수 있는 핵심 프론트엔드/백엔드 코드를 작성해줘."))
        if need_sns:
            steps.append(("📱 그로스 마케터", "출시 홍보를 위한 인스타그램, 링크드인 포스팅 문구와 해시태그를 작성해줘."))

        for i, (step_name, task) in enumerate(steps):
            with st.expander(f"🟢 {step_name} 작업 완료", expanded=True):
                with st.spinner(f"[{selected_model}] 두뇌 풀가동 중..."):
                    result = run_agent_step(step_name, task, full_context)
                    st.markdown(result)
                    full_context += f"\n\n[{step_name}]\n{result}"
            
            progress_bar.progress((i + 1) / len(steps))

        if need_sns:
            st.write("---")
            st.subheader("🚀 소셜 미디어 자동 배포 상태")
            if st.session_state.sns_keys["instagram"]:
                st.success("✅ Instagram API 키 확인됨 -> 포스팅 자동 업로드 성공! (시뮬레이션)")
            else:
                st.warning("⚠️ Instagram API 키가 없습니다. 포스팅 문구만 생성되었습니다.")
                
            if st.session_state.sns_keys["linkedin"]:
                st.success("✅ LinkedIn API 키 확인됨 -> 포스팅 자동 업로드 성공! (시뮬레이션)")
            else:
                st.warning("⚠️ LinkedIn API 키가 없습니다. 포스팅 문구만 생성되었습니다.")

        st.balloons()
        st.success(f"✅ [{selected_model}] 모델을 활용해 모든 프로젝트 세팅을 완료했습니다!")
