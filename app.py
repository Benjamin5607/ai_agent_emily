import streamlit as st
import base64
import requests
import json
from groq import Groq

# ==========================================
# 🌐 다국어 텍스트 사전
# ==========================================
ui_text = {
    "한국어": {
        "sidebar_title": "⚙️ 에밀리 설정 패널",
        "api_setting": "🔑 API 연동 (BYOK)",
        "groq_key": "Groq API Key (필수)",
        "notion_token": "Notion 시크릿 토큰",
        "brain_setting": "🧠 에이전트 두뇌 설정",
        "select_model": "모델 선택",
        "temp_slider": "창의성 레벨 (Temperature)",
        "bg_custom": "🎨 배경화면 커스텀",
        "bg_upload": "로컬 이미지 선택",
        "bg_color": "배경색 지정",
        "pm_setting": "📊 프로젝트 관리 (PM) 기법",
        "main_title": "🚀 AI PM 에이전트: 에밀리 v5.5 (올인원 워크스페이스)",
        "current_brain": "현재 두뇌",
        "current_pm": "관리 기법",
        "idea_label": "💡 진행할 프로젝트 아이디어나 목표를 적어주세요.",
        "idea_placeholder": "예: AI 기반 다이어트 앱 기획 및 런칭",
        "need_code": "💻 핵심 기능 개발 코드 작성 (FE/BE)",
        "need_sns": "📱 X(트위터) / LinkedIn 홍보글 자동 생성",
        "start_btn": "✨ 에밀리 PM 가동 시작!",
        "warning_idea": "프로젝트 내용을 입력해야 시작할 수 있어요!",
        "warning_api": "사이드바에 Groq API Key를 먼저 입력해주세요!",
        "notion_status": "📝 Notion 워크스페이스 완벽 구축 중...",
        "sns_status": "🚀 텍스트 기반 소셜 미디어 포스팅",
        "success_msg": "모든 프로젝트 세팅을 완료했습니다!"
    },
    "English": {
        "sidebar_title": "⚙️ Emily Settings Panel",
        "api_setting": "🔑 API Integration (BYOK)",
        "groq_key": "Groq API Key (Required)",
        "notion_token": "Notion Secret Token",
        "brain_setting": "🧠 Agent Brain Settings",
        "select_model": "Select Model",
        "temp_slider": "Creativity Level (Temperature)",
        "bg_custom": "🎨 Background Customization",
        "bg_upload": "Upload Local Image",
        "bg_color": "Select Background Color",
        "pm_setting": "📊 Project Management Method",
        "main_title": "🚀 AI PM Agent: Emily v5.5 (All-in-One)",
        "current_brain": "Current Brain",
        "current_pm": "PM Method",
        "idea_label": "💡 Describe your project idea or goal.",
        "idea_placeholder": "e.g., Plan and launch an AI diet app",
        "need_code": "💻 Generate Core Feature Code (FE/BE)",
        "need_sns": "📱 Generate X/LinkedIn Promo Posts",
        "start_btn": "✨ Start Emily PM!",
        "warning_idea": "Please enter a project idea to start!",
        "warning_api": "Please enter your Groq API Key in the sidebar first!",
        "notion_status": "📝 Notion Workspace Auto-Creation",
        "sns_status": "🚀 Text-based Social Media Posts",
        "success_msg": "Project setup successfully completed using"
    }
}

st.set_page_config(page_title="Emily AI: PM Agent", layout="wide")
lang = st.sidebar.selectbox("🌐 언어 / Language", ["한국어", "English"])
t = ui_text[lang]

def get_notion_databases(token):
    url = "https://api.notion.com/v1/search"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    data = {"filter": {"value": "database", "property": "object"}}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json().get("results", [])
            db_dict = {}
            for db in results:
                title_arr = db.get("title", [])
                title = title_arr[0].get("plain_text", "제목 없는 DB") if title_arr else "제목 없는 DB"
                db_dict[f"🎯 {title}"] = db["id"]
            return db_dict
        return None
    except: return None

# ==========================================
# 사이드바 1: API 키 입력 및 DB 자동 선택
# ==========================================
with st.sidebar:
    st.title(t["sidebar_title"])
    st.header(t["api_setting"])
    
    if "groq_key" not in st.session_state: st.session_state.groq_key = ""
    if "notion_token" not in st.session_state: st.session_state.notion_token = ""
            
    st.session_state.groq_key = st.text_input(t["groq_key"], type="password", value=st.session_state.groq_key)
    st.session_state.notion_token = st.text_input(t["notion_token"], type="password", value=st.session_state.notion_token)
    
    selected_db_id = None
    if st.session_state.notion_token:
        with st.spinner("노션 DB 검색 중..."):
            db_list = get_notion_databases(st.session_state.notion_token)
            if db_list is None: st.error("❌ 토큰이 잘못되었습니다.")
            elif len(db_list) == 0: st.warning("⚠️ 접근 가능한 DB가 없습니다! 노션 페이지 우측 상단 `...` -> `연결 추가`에서 에밀리를 초대해주세요!")
            else:
                selected_db_name = st.selectbox("📌 연결할 노션 DB 선택", list(db_list.keys()))
                selected_db_id = db_list[selected_db_name]
                st.success("✅ DB 연결 준비 완료!")
    st.divider()

# ==========================================
# Groq 클라이언트 로드 및 UI 설정
# ==========================================
@st.cache_data(ttl=3600)
def get_groq_models(api_key):
    try:
        temp_client = Groq(api_key=api_key)
        return [m.id for m in temp_client.models.list().data if "whisper" not in m.id and "preview" not in m.id]
    except: return ["llama3-70b-8192", "llama3-8b-8192"]

if st.session_state.groq_key:
    client = Groq(api_key=st.session_state.groq_key)
    model_list = get_groq_models(st.session_state.groq_key)
else:
    client = None
    model_list = ["(API 키를 입력하세요)"]

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
# 메인 로직 및 노션 연동 함수
# ==========================================
st.title(t["main_title"])
st.markdown(f"**{t['current_brain']}:** `{selected_model}` | **{t['current_pm']}:** `{pm_method}`")
idea = st.text_area(t["idea_label"], placeholder=t["idea_placeholder"], height=120)

col1, col2 = st.columns(2)
with col1: need_code = st.checkbox(t["need_code"])
with col2: need_sns = st.checkbox(t["need_sns"], value=True)

def get_notion_title_col(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {"Authorization": f"Bearer {st.session_state.notion_token}", "Notion-Version": "2022-06-28"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        for prop_name, prop_data in res.json().get("properties", {}).items():
            if prop_data.get("type") == "title": return prop_name
    return None

# 💡 [핵심 추가 1] 마크다운 문서를 통째로 노션 카드로 만들어주는 전용 함수
def create_notion_doc_card(title, markdown_content, db_id, title_col):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {st.session_state.notion_token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    # 노션 API의 블록 텍스트 한도(2000자)를 피하기 위해 문단 단위로 쪼개기
    paragraphs = markdown_content.split('\n\n')
    children_blocks = []
    
    for para in paragraphs:
        if not para.strip(): continue
        # 한 문단이 1900자를 넘어가면 강제 분할 (안전장치)
        chunks = [para[i:i+1900] for i in range(0, len(para), 1900)]
        for chunk in chunks:
            children_blocks.append({"object": "block", "paragraph": {"rich_text": [{"text": {"content": chunk}}]}})
            
    data = {
        "parent": {"database_id": db_id},
        "properties": {title_col: {"title": [{"text": {"content": title}}]}},
        "children": children_blocks[:100] # API 1회 호출 최대 블록 수 제한(100개)
    }
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200, res.text

# 💡 [기존 유지] Jira 스타일의 실무 태스크 카드 생성 함수
def create_notion_task(task_name, description, checklists, db_id, title_col):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {st.session_state.notion_token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    children_blocks = [
        {"object": "block", "heading_2": {"rich_text": [{"text": {"content": "📝 작업 상세 (User Story)"}}]}},
        {"object": "block", "paragraph": {"rich_text": [{"text": {"content": description}}]}},
        {"object": "block", "divider": {}},
        {"object": "block", "heading_3": {"rich_text": [{"text": {"content": "✅ 서브 태스크 (To-Do)"}}]}}
    ]
    for item in checklists:
        children_blocks.append({"object": "block", "to_do": {"rich_text": [{"text": {"content": item}}], "checked": False}})
        
    data = {"parent": {"database_id": db_id}, "properties": {title_col: {"title": [{"text": {"content": task_name}}]}}, "children": children_blocks}
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200, res.text

def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "system", "content": f"You are a top-tier {role}. You MUST answer in {lang}. Use markdown actively."}, {"role": "user", "content": f"Context: {context}\n\nCurrent Task: {task}"}],
            temperature=temp,
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

# ==========================================
# 실행 엔진
# ==========================================
if st.button(t["start_btn"], use_container_width=True):
    if not st.session_state.groq_key: st.error(t["warning_api"])
    elif not idea: st.warning(t["warning_idea"])
    else:
        st.write("---")
        progress_bar = st.progress(0)
        full_context = f"Project Idea: {idea}\nPM Method: {pm_method}"
        
        # 💡 생성된 문서들을 저장할 딕셔너리 준비
        generated_docs = {}
        
        pm_prompt = f"Plan this project perfectly using the '{pm_method}' methodology. Divide into clear actionable tasks."
        steps = [("Project Manager (PM)", pm_prompt), ("System Architect", "Based on the plan, design the tech stack and database schema.")]
        if need_code: steps.append(("Lead Software Engineer", "Write core frontend/backend code snippets."))
            
        for i, (step_name, task) in enumerate(steps):
            with st.expander(f"🟢 {step_name} Done", expanded=True):
                with st.spinner(f"[{selected_model}] is working..."):
                    result = run_agent_step(step_name, task, full_context)
                    st.markdown(result)
                    generated_docs[step_name] = result # 문서를 딕셔너리에 저장!
                    full_context += f"\n\n[{step_name}]\n{result}"
            progress_bar.progress((i + 1) / (len(steps) + 2))

        if need_sns:
            st.write("---")
            st.subheader(t["sns_status"])
            with st.spinner("Generating Social Media threads..."):
                sns_result = run_agent_step("Growth Marketer", "Write a highly engaging, text-based promotional thread for X (Twitter) and a professional post for LinkedIn about this project. Include relevant emojis and hashtags.", full_context)
                st.info(sns_result)
                generated_docs["Growth Marketer"] = sns_result # 마케팅 문서도 저장!
            progress_bar.progress((len(steps) + 1) / (len(steps) + 2))

        # 💡 노션 전송 시작
        if st.session_state.notion_token and selected_db_id:
            st.write("---")
            st.subheader(t["notion_status"])
            with st.spinner("노션에 전체 워크스페이스를 구축 중입니다..."):
                detected_title_col = get_notion_title_col(selected_db_id)
                
                if not detected_title_col: st.error("❌ 선택한 DB의 구조를 읽어올 수 없습니다.")
                else:
                    # 1️⃣ [마스터 문서 카드 생성] 생성된 기획서, 코드 등을 별도의 위키 카드로 저장!
                    st.write("**📚 프로젝트 문서(Wiki) 카드 생성 중...**")
                    doc_icons = {"Project Manager (PM)": "📋 [마스터 플랜]", "System Architect": "🏗️ [아키텍처 및 DB 설계]", "Lead Software Engineer": "💻 [핵심 코드 스니펫]", "Growth Marketer": "📱 [마케팅/SNS 포스팅 초안]"}
                    
                    for doc_key, doc_content in generated_docs.items():
                        card_title = f"{doc_icons.get(doc_key, '📄 [문서]')} {idea[:10]}..."
                        success, msg = create_notion_doc_card(card_title, doc_content, selected_db_id, detected_title_col)
                        if success: st.write(f"✅ {card_title}")
                        else: st.error(f"❌ {card_title} 생성 실패")
                    
                    st.write("---")
                    st.write("**🛠️ 실무 태스크 카드(Jira 스타일) 생성 중...**")
                    
                    # 2️⃣ [실무 태스크 카드 생성] PM 기법이 반영된 분류형 JSON 프롬프트!
                    json_prompt = f"""
                    프로젝트: {idea}
                    채택된 PM 방법론: {pm_method}
                    
                    위 방법론에 맞추어 실제 개발을 위한 태스크 5~7개를 도출하세요.
                    반드시 태스크 이름 앞에 방법론의 분류(예: [Sprint 1], [Phase 2], [Backlog], [Epic])를 붙여주세요.
                    결과는 반드시 아래 JSON 배열 형식으로만 출력하세요.
                    [
                        {{
                            "task_name": "[Sprint 1] 회원가입 API 구현",
                            "description": "사용자 정보를 DB에 저장하고 JWT 토큰을 발급하는 백엔드 API를 개발합니다.",
                            "checklists": ["DB 유저 테이블 스키마 작성", "비밀번호 해싱 로직 구현", "포스트맨 테스트 완료"]
                        }}
                    ]
                    """
                    try:
                        json_res = client.chat.completions.create(
                            model=selected_model,
                            messages=[{"role": "user", "content": json_prompt}],
                            temperature=0.2
                        )
                        clean_json = json_res.choices[0].message.content.replace("```json", "").replace("```", "").strip()
                        tasks = json.loads(clean_json)
                        
                        for task in tasks:
                            checklists = task.get("checklists", [])
                            success, msg = create_notion_task(task['task_name'], task['description'], checklists, selected_db_id, detected_title_col)
                            if success: st.write(f"✅ {task['task_name']}")
                            else: st.error(f"❌ 실패: {task['task_name']} ({msg})")
                    except Exception as e:
                        st.error(f"JSON 파싱 에러 (가벼운 모델로 변경 권장): {e}")
                        
        elif not st.session_state.notion_token:
            st.info("💡 Tip: 사이드바에 Notion 토큰을 입력하면 노션 칸반 보드가 자동 생성됩니다!")
            
        progress_bar.progress(1.0)
        st.balloons()
        st.success(f"✅ ✅ {t['success_msg']} `{selected_model}`!")
