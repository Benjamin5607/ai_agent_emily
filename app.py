import streamlit as st
import base64
import requests
import json
import datetime
from groq import Groq

# ==========================================
# 🌐 다국어 텍스트 사전 (UI는 그대로 다국어 지원!)
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
        "main_title": "🚀 AI PM 에이전트: 에밀리 v5.7 (Global Edition)",
        "current_brain": "현재 두뇌",
        "current_pm": "관리 기법",
        "idea_label": "💡 진행할 프로젝트 아이디어나 목표를 적어주세요. (한국어로 적어도 영어로 세팅됩니다!)",
        "idea_placeholder": "예: AI 기반 다이어트 앱 기획 및 런칭",
        "need_code": "💻 핵심 기능 개발 코드 작성 (FE/BE)",
        "need_sns": "📱 X(트위터) / LinkedIn 홍보글 자동 생성",
        "start_btn": "✨ 에밀리 PM 가동 시작!",
        "warning_idea": "프로젝트 내용을 입력해야 시작할 수 있어요!",
        "warning_api": "사이드바에 Groq API Key를 먼저 입력해주세요!",
        "notion_status": "📝 Notion 워크스페이스 구축 중 (English Only)...",
        "sns_status": "🚀 텍스트 기반 소셜 미디어 포스팅",
        "success_msg": "글로벌 프로젝트 세팅을 완료했습니다!"
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
        "main_title": "🚀 AI PM Agent: Emily v5.7 (Global Edition)",
        "current_brain": "Current Brain",
        "current_pm": "PM Method",
        "idea_label": "💡 Describe your project idea or goal.",
        "idea_placeholder": "e.g., Plan and launch an AI diet app",
        "need_code": "💻 Generate Core Feature Code (FE/BE)",
        "need_sns": "📱 Generate X/LinkedIn Promo Posts",
        "start_btn": "✨ Start Emily PM!",
        "warning_idea": "Please enter a project idea to start!",
        "warning_api": "Please enter your Groq API Key in the sidebar first!",
        "notion_status": "📝 Notion Workspace Auto-Creation (English)...",
        "sns_status": "🚀 Text-based Social Media Posts",
        "success_msg": "Global Project setup successfully completed using"
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
                title = title_arr[0].get("plain_text", "Untitled DB") if title_arr else "Untitled DB"
                db_dict[f"🎯 {title}"] = db["id"]
            return db_dict
        return None
    except: return None

with st.sidebar:
    st.title(t["sidebar_title"])
    st.header(t["api_setting"])
    
    if "groq_key" not in st.session_state: st.session_state.groq_key = ""
    if "notion_token" not in st.session_state: st.session_state.notion_token = ""
            
    st.session_state.groq_key = st.text_input(t["groq_key"], type="password", value=st.session_state.groq_key)
    st.session_state.notion_token = st.text_input(t["notion_token"], type="password", value=st.session_state.notion_token)
    
    selected_db_id = None
    if st.session_state.notion_token:
        with st.spinner("Searching Notion DB..."):
            db_list = get_notion_databases(st.session_state.notion_token)
            if db_list is None: st.error("❌ Invalid Token.")
            elif len(db_list) == 0: st.warning("⚠️ No accessible DB found. Invite Emily to your Notion page!")
            else:
                selected_db_name = st.selectbox("📌 Select Notion DB", list(db_list.keys()))
                selected_db_id = db_list[selected_db_name]
                st.success("✅ DB Ready!")
    st.divider()

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

def setup_notion_db_properties(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {"Authorization": f"Bearer {st.session_state.notion_token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    data = {"properties": {"RACI": {"rich_text": {}}, "Required Tool": {"multi_select": {}}, "Timeline": {"date": {}}}}
    requests.patch(url, headers=headers, json=data)

def create_notion_doc_card(title, markdown_content, db_id, title_col):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {st.session_state.notion_token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    paragraphs = markdown_content.split('\n\n')
    children_blocks = []
    
    for para in paragraphs:
        if not para.strip(): continue
        chunks = [para[i:i+1900] for i in range(0, len(para), 1900)]
        for chunk in chunks:
            children_blocks.append({"object": "block", "paragraph": {"rich_text": [{"text": {"content": chunk}}]}})
            
    data = {"parent": {"database_id": db_id}, "properties": {title_col: {"title": [{"text": {"content": title}}]}}, "children": children_blocks[:100]}
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200, res.text

def create_notion_task(task_name, description, checklists, raci, tools, start_date, end_date, db_id, title_col):
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {st.session_state.notion_token}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    props = {title_col: {"title": [{"text": {"content": task_name}}]}}
    if raci: props["RACI"] = {"rich_text": [{"text": {"content": raci}}]}
    valid_tools = [{"name": t.replace(",", " ")} for t in tools if t]
    if valid_tools: props["Required Tool"] = {"multi_select": valid_tools}
    if start_date and end_date: props["Timeline"] = {"date": {"start": start_date, "end": end_date}}
    
    # 💡 [글로벌 업데이트 1] 카드 내부 텍스트 완전 영문화
    children_blocks = [
        {"object": "block", "heading_2": {"rich_text": [{"text": {"content": "📝 Task Details (User Story)"}}]}},
        {"object": "block", "paragraph": {"rich_text": [{"text": {"content": description}}]}},
        {"object": "block", "divider": {}},
        {"object": "block", "heading_3": {"rich_text": [{"text": {"content": "✅ Sub-tasks (To-Do)"}}]}}
    ]
    for item in checklists:
        children_blocks.append({"object": "block", "to_do": {"rich_text": [{"text": {"content": item}}], "checked": False}})
        
    data = {"parent": {"database_id": db_id}, "properties": props, "children": children_blocks}
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200, res.text

# 💡 [글로벌 업데이트 2] 시스템 프롬프트 강력 통제: 무조건 '영어'로만 대답할 것!
def run_agent_step(role, task, context):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": f"You are a top-tier {role} in Silicon Valley. You MUST output all your plans, code, and documentation strictly in ENGLISH, regardless of the user's input language. Use markdown actively."}, 
                {"role": "user", "content": f"Context: {context}\n\nCurrent Task: {task}"}
            ],
            temperature=temp,
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {str(e)}"

if st.button(t["start_btn"], use_container_width=True):
    if not st.session_state.groq_key: st.error(t["warning_api"])
    elif not idea: st.warning(t["warning_idea"])
    else:
        st.write("---")
        progress_bar = st.progress(0)
        full_context = f"Project Idea: {idea}\nPM Method: {pm_method}"
        generated_docs = {}
        
        pm_prompt = f"Plan this project perfectly using the '{pm_method}' methodology. Divide into clear actionable tasks."
        steps = [("Project Manager (PM)", pm_prompt), ("System Architect", "Based on the plan, design the tech stack and database schema.")]
        if need_code: steps.append(("Lead Software Engineer", "Write core frontend/backend code snippets."))
            
        for i, (step_name, task) in enumerate(steps):
            with st.expander(f"🟢 {step_name} Done", expanded=True):
                with st.spinner(f"[{selected_model}] is working..."):
                    result = run_agent_step(step_name, task, full_context)
                    st.markdown(result)
                    generated_docs[step_name] = result
                    full_context += f"\n\n[{step_name}]\n{result}"
            progress_bar.progress((i + 1) / (len(steps) + 2))

        if need_sns:
            st.write("---")
            st.subheader(t["sns_status"])
            with st.spinner("Generating Social Media threads..."):
                sns_result = run_agent_step("Growth Marketer", "Write a highly engaging, text-based promotional thread for X (Twitter) and a professional post for LinkedIn about this project. Include relevant emojis and hashtags.", full_context)
                st.info(sns_result)
                generated_docs["Growth Marketer"] = sns_result
            progress_bar.progress((len(steps) + 1) / (len(steps) + 2))

        if st.session_state.notion_token and selected_db_id:
            st.write("---")
            st.subheader(t["notion_status"])
            with st.spinner("Building Workspace in Notion..."):
                detected_title_col = get_notion_title_col(selected_db_id)
                
                if not detected_title_col: st.error("❌ Cannot read the structure of the selected DB.")
                else:
                    setup_notion_db_properties(selected_db_id)
                    
                    st.write("**📚 Creating Document (Wiki) Cards...**")
                    # 💡 [글로벌 업데이트 3] 문서 카드 제목 영문화
                    doc_icons = {
                        "Project Manager (PM)": "📋 [Master Plan]", 
                        "System Architect": "🏗️ [Architecture & DB]", 
                        "Lead Software Engineer": "💻 [Core Code Snippets]", 
                        "Growth Marketer": "📱 [Marketing Drafts]"
                    }
                    
                    for doc_key, doc_content in generated_docs.items():
                        card_title = f"{doc_icons.get(doc_key, '📄 [Doc]')} Project Wiki"
                        success, msg = create_notion_doc_card(card_title, doc_content, selected_db_id, detected_title_col)
                        if success: st.write(f"✅ {card_title}")
                        else: st.error(f"❌ Failed: {card_title}")
                    
                    st.write("---")
                    st.write("**🛠️ Creating Task Cards (RACI/Timeline)...**")
                    
                    # 💡 [글로벌 업데이트 4] JSON 프롬프트와 예시를 완벽한 영어로 변경
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    json_prompt = f"""
                    Project: {idea}
                    PM Methodology: {pm_method}
                    Today's Date: {today_str}
                    
                    Extract 5 to 7 core actionable tasks for this project based on the chosen methodology.
                    Prefix the task name with the methodology phase (e.g., [Sprint 1], [Phase 2]).
                    You MUST write EVERYTHING in ENGLISH.
                    You MUST output ONLY a valid JSON array. Do not use commas inside the 'tools' array strings.
                    
                    Example Format:
                    [
                        {{
                            "task_name": "[Sprint 1] Implement Sign-up API",
                            "description": "Develop backend API to store user data and issue JWT token.",
                            "checklists": ["Design DB schema", "Password hashing", "Postman testing"],
                            "raci": "R: Backend Dev, A: PM",
                            "tools": ["Node.js", "PostgreSQL"],
                            "start_date": "2026-03-10",
                            "end_date": "2026-03-14"
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
                            raci = task.get("raci", "")
                            tools = task.get("tools", [])
                            start_date = task.get("start_date", "")
                            end_date = task.get("end_date", "")
                            
                            success, msg = create_notion_task(task['task_name'], task['description'], checklists, raci, tools, start_date, end_date, selected_db_id, detected_title_col)
                            if success: st.write(f"✅ {task['task_name']}")
                            else: st.error(f"❌ Failed: {task['task_name']} ({msg})")
                    except Exception as e:
                        st.error(f"JSON Parsing Error (Try a lighter model): {e}")
                        
        elif not st.session_state.notion_token:
            st.info("💡 Tip: Enter Notion API keys in the sidebar to auto-create Kanban boards!")
            
        progress_bar.progress(1.0)
        st.balloons()
        st.success(f"✅ ✅ {t['success_msg']} `{selected_model}`!")
