import streamlit as st
import base64
import requests
import json
from groq import Groq

# ==========================================
# 🌐 다국어 텍스트 사전 (UI Localization)
# ==========================================
ui_text = {
    "한국어": {
        "sidebar_title": "⚙️ 에밀리 설정 패널",
        "api_setting": "🔑 API 연동 (Bring Your Own Key)",
        "groq_key": "Groq API Key (필수)",
        "notion_token": "Notion 시크릿 토큰",
        "notion_db": "Notion 데이터베이스 ID",
        # notion_col 입력란 삭제! AI가 알아서 찾음.
        "brain_setting": "🧠 에이전트 두뇌 설정",
        "select_model": "모델 선택",
        "temp_slider": "창의성 레벨 (Temperature)",
        "bg_custom": "🎨 배경화면 커스텀",
        "bg_upload": "로컬 이미지 선택",
        "bg_color": "배경색 지정",
        "pm_setting": "📊 프로젝트 관리 (PM) 기법",
        "main_title": "🚀 AI PM 에이전트: 에밀리 v5.2",
        "current_brain": "현재 두뇌",
        "current_pm": "관리 기법",
        "idea_label": "💡 진행할 프로젝트 아이디어나 목표를 적어주세요.",
        "idea_placeholder": "예: AI 기반 다이어트 앱 기획 및 런칭",
        "need_code": "💻 핵심 기능 개발 코드 작성 (FE/BE)",
        "need_sns": "📱 X(트위터) / LinkedIn 홍보글 자동 생성",
        "start_btn": "✨ 에밀리 PM 가동 시작!",
        "warning_idea": "프로젝트 내용을 입력해야 시작할 수 있어요!",
        "warning_api": "사이드바에 Groq API Key를 먼저 입력해주세요!",
        "notion_status": "📝 Notion 칸반 보드 자동 생성",
        "sns_status": "🚀 텍스트 기반 소셜 미디어 포스팅",
        "success_msg": "모든 프로젝트 세팅을 완료했습니다!"
    },
    "English": {
        "sidebar_title": "⚙️ Emily Settings Panel",
        "api_setting": "🔑 API Integration (BYOK)",
        "groq_key": "Groq API Key (Required)",
        "notion_token": "Notion Secret Token",
        "notion_db": "Notion Database ID",
        "brain_setting": "🧠 Agent Brain Settings",
        "select_model": "Select Model",
        "temp_slider": "Creativity Level (Temperature)",
        "bg_custom": "🎨 Background Customization",
        "bg_upload": "Upload Local Image",
        "bg_color": "Select Background Color",
        "pm_setting": "📊 Project Management Method",
        "main_title": "🚀 AI PM Agent: Emily v5.2",
        "current_brain": "Current Brain",
        "current_pm": "PM Method",
        "idea_label": "💡 Describe your project idea or goal.",
        "idea_placeholder": "e.g., Plan and launch an AI diet app",
        "need_code": "💻 Generate Core Feature Code (FE/BE)",
        "need_sns": "📱 Generate X/LinkedIn Promo Posts",
        "start_btn": "✨ Start Emily PM!",
        "warning_idea": "Please enter a project idea to start!",
        "warning_api": "Please enter your Groq API Key in the sidebar first!",
        "notion_status": "📝 Notion Kanban Board Auto-Creation",
        "sns_status": "🚀 Text-based Social Media Posts",
        "success_msg": "Project setup successfully completed using"
    }
}

st.set_page_config(page_title="Emily AI: PM Agent", layout="wide")
lang = st.sidebar.selectbox("🌐 언어 / Language", ["한국어", "English"])
t = ui_text[lang]

# ==========================================
# 사이드바 1: API 키 입력
# ==========================================
with st.sidebar:
    st.title(t["sidebar_title"])
    st.header(t["api_setting"])
    
    for key in ["groq_key", "notion_token", "notion_db"]:
        if key not in st.session_state:
            st.session_state[key] = ""
            
    st.session_state.groq_key = st.text_input(t["groq_key"], type="password", value=st.session_state.groq_key)
    st.session_state.notion_token = st.text_input(t["notion_token"], type="password", value=st.session_state.notion_token)
    st.session_state.notion_db = st.text_input(t["notion_db"], type="password", value=st.session_state.notion_db)
    st.divider()

# ==========================================
# Groq 클라이언트 및 모델 로드
# ==========================================
@st.cache_data(ttl=3600)
def get_groq_models(api_key):
    try:
        temp_client = Groq(api_key=api_key)
        models = temp_client.models.list()
        return [m.id for m in models.data if "whisper" not in m.id and "preview" not in m.id]
    except:
        return ["llama3-70b-8192", "llama3-8b-8192"]

if st.session_state.groq_key:
    client = Groq(api_key=st.session_state.groq_key)
    model_list = get_groq_models(st.session_state.groq_key)
else:
    client = None
    model_list = ["(API 키를 입력하세요)"]

# ==========================================
# 사이드바 2: 나머지 UI 설정
# ==========================================
with st.sidebar:
    st.header(t["brain_setting"])
    selected_model = st.selectbox(t["select_model"], model_list, index=0)
    temp = st.slider(t["temp_slider"], 0.0, 1.0, 0.7, step=0.1)
    st.divider()
    
    st.header(t["bg_custom"])
    bg_upload = st.file_uploader(t["bg_upload"], type=['png', 'jpg', 'jpeg'])
    if bg_upload is not None:
        base64_img = base64.b64encode(bg_upload.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{base64_img}"); background-size: cover; background-attachment: fixed; }} .main {{ background-color: rgba(255, 255, 255, 0.85); padding: 20px; border-radius: 10px; }}</style>""", unsafe_allow_html=True)
    else:
        bg_color = st.color_picker(t["bg_color"], "#F0F2F6")
        st.markdown(f"<style>.stApp {{ background-color: {bg_color}; }}</style>", unsafe_allow_html=True)
    st.divider()

    st.header(t["pm_setting"])
    pm_method = st.selectbox("Method", ["Agile", "Scrum", "Kanban", "Waterfall"], label_visibility="collapsed")

# ==========================================
# 메인 화면 UI 및 실행 로직
# ==========================================
st.title(t["main_title"])
st.markdown(f"**{t['current_brain']}:** `{selected_model}` | **{t['current_pm']}:** `{pm_method}`")

idea = st.text_area(t["idea_label"], placeholder=t["idea_placeholder"], height=120)

col1, col2 = st.columns(2)
with col1:
    need_code = st.checkbox(t["need_code"])
with col2:
    need_sns = st.checkbox(t["need_sns"], value=True)

# 💡 [핵심 업데이트] 1. 노션 데이터베이스에서 Title 컬럼명 자동 추출 함수
def get_notion_title_col():
    url = f"https://api.notion.com/v1/databases/{st.session_state.notion_db}"
    headers = {
        "Authorization": f"Bearer {st.session_state.notion_token}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        db_info = response.json()
        # 속성들 중에서 type이 'title'인 녀석의 진짜 이름을 찾아냄!
        for prop_name, prop_data in db_info.get("properties", {}).items():
            if prop_data.get("type") == "title":
                return prop_name
    return None

# 2. 노션 카드 생성 함수 (추출된 Title 컬럼명 사용)
def create_notion_task(task_name, description):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {st.session_state.notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": st.session_state.notion_db_id}, # 주의: v5.1 변수명에 맞춤
        "properties": {notion_title_col: {"title": [{"text": {"content": task_name}}]}},
        "children": [{"object": "block", "paragraph": {"rich_text": [{"text": {"content": description}}]}}]
    }
    response = requests.post(url, headers=headers, json=data)
    
    # 💡 성공 여부뿐만 아니라, 실패 시 노션이 보낸 '진짜 에러 원인'도 같이 반환하게 수정!
    return response.status_code == 200, response.text

def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": f"You are a top-tier {role}. You MUST answer in {lang}. Use markdown actively."},
                {"role": "user", "content": f"Context: {context}\n\nCurrent Task: {task}"}
            ],
            temperature=temp,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if st.button(t["start_btn"], use_container_width=True):
    if not st.session_state.groq_key:
        st.error(t["warning_api"])
    elif not idea:
        st.warning(t["warning_idea"])
    else:
        st.write("---")
        progress_bar = st.progress(0)
        full_context = f"Project Idea: {idea}\nPM Method: {pm_method}"
        
        # 1. 기획 단계
        pm_prompt = f"Plan this project perfectly using the '{pm_method}' methodology. Divide into clear actionable tasks."
        steps = [
            ("Project Manager (PM)", pm_prompt),
            ("System Architect", "Based on the plan, design the tech stack and database schema.")
        ]
        if need_code:
            steps.append(("Lead Software Engineer", "Write core frontend/backend code snippets."))
            
        for i, (step_name, task) in enumerate(steps):
            with st.expander(f"🟢 {step_name} Done", expanded=True):
                with st.spinner(f"[{selected_model}] is working..."):
                    result = run_agent_step(step_name, task, full_context)
                    st.markdown(result)
                    full_context += f"\n\n[{step_name}]\n{result}"
            progress_bar.progress((i + 1) / (len(steps) + 2))

        # 2. SNS 생성
        if need_sns:
            st.write("---")
            st.subheader(t["sns_status"])
            with st.spinner("Generating Social Media threads..."):
                sns_task = "Write a highly engaging, text-based promotional thread for X (Twitter) and a professional post for LinkedIn about this project. Include relevant emojis and hashtags."
                sns_result = run_agent_step("Growth Marketer", sns_task, full_context)
                st.info(sns_result)
            progress_bar.progress((len(steps) + 1) / (len(steps) + 2))

        # 3. 노션 연동 (자동 감지 로직 적용)
        if st.session_state.notion_token and st.session_state.notion_db:
            st.write("---")
            st.subheader(t["notion_status"])
            with st.spinner("노션 데이터베이스 분석 및 태스크 전송 중..."):
                
                # DB에서 Title 컬럼명 자동 찾기
                detected_title_col = get_notion_title_col()
                
                if not detected_title_col:
                    st.error("❌ Notion API 연결 실패: 토큰이나 DB ID가 잘못되었거나 접근 권한이 없습니다.")
                else:
                    st.info(f"💡 노션 타이틀 컬럼 자동 감지 성공: '{detected_title_col}'")
                    
                    json_prompt = f"Based on the PM plan above, extract 5 to 7 core tasks. You MUST return ONLY a valid JSON array like this: [{{\"task_name\": \"Task 1\", \"description\": \"Details\"}}]. Do not add any other text or markdown."
                    try:
                        json_res = client.chat.completions.create(
                            model=selected_model,
                            messages=[{"role": "user", "content": f"Plan Context: {full_context}\n\nTask: {json_prompt}"}],
                            temperature=0.2
                        )
                    clean_json = json_res.choices[0].message.content.replace("```json", "").replace("```", "").strip()
                    tasks = json.loads(clean_json)
                    
                    for task in tasks:
                        # 💡 msg 변수를 추가로 받아서 에러 화면에 뿌려줌!
                        success, msg = create_notion_task(task['task_name'], task['description'])
                        if success:
                            st.write(f"✅ {task['task_name']}")
                        else:
                            st.error(f"❌ 실패: {task['task_name']}\n\n🔍 노션의 답변: {msg}")
                    except Exception as e:
                        st.error(f"Notion task creation failed. JSON parsing error: {e}")
                        
        elif not st.session_state.notion_token:
            st.info("💡 Tip: Enter Notion API keys in the sidebar to auto-create Kanban boards!")
            
        progress_bar.progress(1.0)
        st.balloons()
        st.success(f"✅ ✅ {t['success_msg']} `{selected_model}`!")
