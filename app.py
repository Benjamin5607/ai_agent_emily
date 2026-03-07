import streamlit as st
import base64
from groq import Groq

# ==========================================
# 🌐 다국어 텍스트 사전 (UI Localization)
# ==========================================
ui_text = {
    "한국어": {
        "sidebar_title": "⚙️ 에밀리 설정 패널",
        "brain_setting": "🧠 에이전트 두뇌 설정",
        "select_model": "모델 선택",
        "temp_slider": "창의성 레벨 (Temperature)",
        "bg_custom": "🎨 배경화면 커스텀",
        "bg_upload": "로컬 이미지 선택 (PNG, JPG)",
        "bg_color": "배경색 지정 (이미지 없을 시)",
        "api_setting": "🔑 소셜 미디어 API (로컬 캐시)",
        "pm_setting": "📊 프로젝트 관리 (PM) 기법",
        "main_title": "🚀 AI PM 에이전트: 에밀리 v4.0",
        "current_brain": "현재 두뇌",
        "current_pm": "관리 기법",
        "idea_label": "💡 진행할 프로젝트 아이디어나 목표를 적어주세요.",
        "idea_placeholder": "예: AI 기반 다이어트 앱 기획 및 런칭",
        "need_code": "💻 핵심 기능 개발 코드 작성 (FE/BE)",
        "need_sns": "📱 소셜 미디어 포스팅 자동 생성 및 배포 시뮬레이션",
        "start_btn": "✨ 에밀리 PM 가동 시작!",
        "warning_idea": "프로젝트 내용을 입력해야 시작할 수 있어요!",
        "sns_status": "🚀 소셜 미디어 자동 배포 상태",
        "success_msg": "모델을 활용해 모든 프로젝트 세팅을 완료했습니다!"
    },
    "English": {
        "sidebar_title": "⚙️ Emily Settings Panel",
        "brain_setting": "🧠 Agent Brain Settings",
        "select_model": "Select Model",
        "temp_slider": "Creativity Level (Temperature)",
        "bg_custom": "🎨 Background Customization",
        "bg_upload": "Upload Local Image (PNG, JPG)",
        "bg_color": "Select Background Color",
        "api_setting": "🔑 Social Media API (Local Cache)",
        "pm_setting": "📊 Project Management Method",
        "main_title": "🚀 AI PM Agent: Emily v4.0",
        "current_brain": "Current Brain",
        "current_pm": "PM Method",
        "idea_label": "💡 Describe your project idea or goal.",
        "idea_placeholder": "e.g., Plan and launch an AI diet app",
        "need_code": "💻 Generate Core Feature Code (FE/BE)",
        "need_sns": "📱 Auto-Generate & Simulate SNS Posts",
        "start_btn": "✨ Start Emily PM!",
        "warning_idea": "Please enter a project idea to start!",
        "sns_status": "🚀 Social Media Auto-Deployment Status",
        "success_msg": "Project setup successfully completed using"
    }
}

# 1. 페이지 설정
st.set_page_config(page_title="Emily AI: PM & Marketer", layout="wide")

# ==========================================
# 사이드바 1: 언어 선택 (가장 먼저 위치)
# ==========================================
lang = st.sidebar.selectbox("🌐 인터페이스 언어 / Language", ["한국어", "English"])
t = ui_text[lang] # 선택된 언어의 텍스트 사전 로드

# ==========================================
# Groq 클라이언트 초기화 및 모델 로드
# ==========================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Error: Please check Streamlit Secrets for GROQ_API_KEY.")
    st.stop()

@st.cache_data(ttl=3600)
def get_groq_models():
    try:
        models = client.models.list()
        return [m.id for m in models.data if "whisper" not in m.id and "preview" not in m.id]
    except:
        return ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]

# ==========================================
# 사이드바 2: 나머지 설정들 (다국어 적용)
# ==========================================
with st.sidebar:
    st.title(t["sidebar_title"])
    
    st.header(t["brain_setting"])
    selected_model = st.selectbox(t["select_model"], get_groq_models(), index=0)
    temp = st.slider(t["temp_slider"], 0.0, 1.0, 0.7, step=0.1)
    
    st.divider()
    
    st.header(t["bg_custom"])
    bg_upload = st.file_uploader(t["bg_upload"], type=['png', 'jpg', 'jpeg'])
    if bg_upload is not None:
        base64_img = base64.b64encode(bg_upload.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{ background-image: url("data:image/png;base64,{base64_img}"); background-size: cover; background-attachment: fixed; }}
            .main {{ background-color: rgba(255, 255, 255, 0.85); padding: 20px; border-radius: 10px; }}
            </style>
            """, unsafe_allow_html=True
        )
    else:
        bg_color = st.color_picker(t["bg_color"], "#F0F2F6")
        st.markdown(f"<style>.stApp {{ background-color: {bg_color}; }}</style>", unsafe_allow_html=True)
        
    st.divider()

    st.header(t["api_setting"])
    if "sns_keys" not in st.session_state:
        st.session_state.sns_keys = {"instagram": "", "linkedin": ""}
    st.session_state.sns_keys["instagram"] = st.text_input("Instagram API Key", type="password", value=st.session_state.sns_keys["instagram"])
    st.session_state.sns_keys["linkedin"] = st.text_input("LinkedIn API Key", type="password", value=st.session_state.sns_keys["linkedin"])
    
    st.divider()

    st.header(t["pm_setting"])
    pm_method = st.selectbox("Method", ["Agile", "Scrum", "Kanban", "Waterfall"], label_visibility="collapsed")

# ==========================================
# 메인 화면 UI (다국어 적용)
# ==========================================
st.title(t["main_title"])
st.markdown(f"**{t['current_brain']}:** `{selected_model}` | **{t['current_pm']}:** `{pm_method}`")

idea = st.text_area(t["idea_label"], placeholder=t["idea_placeholder"], height=120)

col1, col2 = st.columns(2)
with col1:
    need_code = st.checkbox(t["need_code"])
with col2:
    need_sns = st.checkbox(t["need_sns"])

# ==========================================
# 에이전트 실행 로직
# ==========================================
def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                # 시스템 프롬프트에도 유저가 선택한 언어로 답변하도록 지시!
                {"role": "system", "content": f"You are a top-tier {role}. You MUST answer in {lang}. Use markdown actively for readability."},
                {"role": "user", "content": f"Context: {context}\n\nCurrent Task: {task}"}
            ],
            temperature=temp,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if st.button(t["start_btn"], use_container_width=True):
    if not idea:
        st.warning(t["warning_idea"])
    else:
        st.write("---")
        progress_bar = st.progress(0)
        full_context = f"Project Idea: {idea}\nPM Method: {pm_method}"
        
        pm_prompt = f"Plan this project perfectly using the '{pm_method}' methodology. "
        if pm_method == "Kanban":
            pm_prompt += "Draw a text-based Kanban board with [To Do], [In Progress], [Done] columns."
        elif pm_method == "Scrum":
            pm_prompt += "Divide the backlog and tasks into Sprint 1, Sprint 2, etc."
        elif pm_method == "Agile":
            pm_prompt += "Create a plan for rapid iteration using User Stories and Epics."
        else:
            pm_prompt += "Create a strict timeline following Requirements -> Design -> Implementation -> Testing -> Maintenance."

        steps = [
            ("Project Manager (PM)", pm_prompt),
            ("System Architect", "Based on the plan, design the tech stack and database schema.")
        ]
        
        if need_code:
            steps.append(("Lead Software Engineer", "Write core frontend/backend code snippets to demonstrate the main features."))
        if need_sns:
            steps.append(("Growth Marketer", "Write promotional Instagram and LinkedIn post copies and hashtags."))

        for i, (step_name, task) in enumerate(steps):
            with st.expander(f"🟢 {step_name} Done", expanded=True):
                with st.spinner(f"[{selected_model}] is working..."):
                    result = run_agent_step(step_name, task, full_context)
                    st.markdown(result)
                    full_context += f"\n\n[{step_name}]\n{result}"
            
            progress_bar.progress((i + 1) / len(steps))

        if need_sns:
            st.write("---")
            st.subheader(t["sns_status"])
            if st.session_state.sns_keys["instagram"]:
                st.success("✅ Instagram API Key Found -> Auto-upload simulated successfully!")
            else:
                st.warning("⚠️ No Instagram API Key. Only post text generated.")
                
            if st.session_state.sns_keys["linkedin"]:
                st.success("✅ LinkedIn API Key Found -> Auto-upload simulated successfully!")
            else:
                st.warning("⚠️ No LinkedIn API Key. Only post text generated.")

        st.balloons()
        st.success(f"✅ ✅ {t['success_msg']} `{selected_model}`!")
