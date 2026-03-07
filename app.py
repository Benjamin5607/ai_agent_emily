import streamlit as st
import base64
from groq import Groq

# 1. 페이지 설정 (넓은 화면 사용)
st.set_page_config(page_title="Emily AI: PM & Marketer", layout="wide")

# ==========================================
# 기능 1 & 2: 사이드바 (개인화 및 API 설정)
# ==========================================
with st.sidebar:
    st.title("⚙️ 에밀리 개인화 & 설정")
    
    # [기능 2] 배경화면 설정 (로컬 파일 업로드)
    st.header("🎨 배경화면 설정")
    bg_upload = st.file_uploader("로컬 이미지 선택 (PNG, JPG)", type=['png', 'jpg', 'jpeg'])
    if bg_upload is not None:
        # 이미지를 Base64로 변환하여 CSS로 배경 적용
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
            /* 가독성을 위해 메인 콘텐츠 영역에 반투명 배경 추가 */
            .main {{ background-color: rgba(255, 255, 255, 0.85); padding: 20px; border-radius: 10px; }}
            </style>
            """, unsafe_allow_html=True
        )
    else:
        # 배경색 지정 로직 (기본)
        bg_color = st.color_picker("배경색 선택 (이미지 없을 시)", "#F0F2F6")
        st.markdown(f"<style>.stApp {{ background-color: {bg_color}; }}</style>", unsafe_allow_html=True)
        
    st.divider()

    # [기능 1] 소셜 미디어 API 로컬 캐시 (Session State 활용)
    st.header("🔑 소셜 미디어 API 연동")
    st.caption("※ 세션 유지 동안만 로컬에 캐시됩니다.")
    if "sns_keys" not in st.session_state:
        st.session_state.sns_keys = {"instagram": "", "linkedin": ""}
    
    st.session_state.sns_keys["instagram"] = st.text_input("Instagram Graph API Key", type="password", value=st.session_state.sns_keys["instagram"])
    st.session_state.sns_keys["linkedin"] = st.text_input("LinkedIn API Key", type="password", value=st.session_state.sns_keys["linkedin"])
    
    st.divider()

    # [기능 3] 프로젝트 관리 기법 선택
    st.header("📊 프로젝트 관리 (PM) 기법")
    pm_method = st.selectbox("에밀리가 사용할 PM 방법론", ["Agile (애자일)", "Scrum (스크럼)", "Kanban (칸반)", "Waterfall (워터폴)"])

# ==========================================
# Groq 클라이언트 초기화
# ==========================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API 키가 없습니다. Streamlit Secrets에 GROQ_API_KEY를 설정하세요.")
    st.stop()

# ==========================================
# 메인 화면 UI
# ==========================================
st.title("🚀 AI PM 에이전트: 에밀리 v3.0")
st.markdown(f"선택된 PM 기법: **{pm_method}** | 배경 & SNS 자동 포스팅 지원")

idea = st.text_area("💡 진행할 프로젝트 아이디어나 목표를 적어주세요.", 
                    placeholder="예: AI 기반 영어 회화 앱 런칭 프로젝트",
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
            model="llama3-70b-8192", # 가장 똑똑한 모델 고정 혹은 사이드바에서 선택 가능
            messages=[
                {"role": "system", "content": f"당신은 최고 수준의 {role}입니다. 마크다운을 적극 활용하고 가독성을 높이세요."},
                {"role": "user", "content": f"전체 문맥: {context}\n\n현재 할 일: {task}"}
            ],
            temperature=0.7,
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
        
        # 1. PM 기법에 맞춘 플래닝 지시
        pm_prompt = f"이 프로젝트를 '{pm_method}' 방법론에 맞춰서 완벽하게 기획해줘. "
        if "Kanban" in pm_method:
            pm_prompt += "반드시 [To Do], [In Progress], [Done] 형식의 칸반 보드 텍스트 UI를 그려줘."
        elif "Scrum" in pm_method:
            pm_prompt += "Sprint 1, Sprint 2 형식으로 백로그(Backlog)와 태스크를 나누어줘."
        elif "Agile" in pm_method:
            pm_prompt += "사용자 스토리(User Story)와 에픽(Epic) 단위로 빠르게 이터레이션(Iteration)할 수 있는 계획을 짜줘."
        else: # Waterfall
            pm_prompt += "요구사항 분석 -> 설계 -> 구현 -> 테스트 -> 유지보수의 엄격한 폭포수 단계별로 일정을 짜줘."

        steps = [
            ("📊 프로젝트 매니저 (PM)", pm_prompt),
            ("🏗️ 시스템 아키텍트", "위 계획을 바탕으로 서비스의 기술 스택과 데이터베이스 스키마를 설계해줘.")
        ]
        
        if need_code:
            steps.append(("💻 리드 소프트웨어 엔지니어", "핵심 기능을 보여줄 수 있는 핵심 프론트엔드/백엔드 코드를 작성해줘."))
        if need_sns:
            steps.append(("📱 그로스 마케터", "출시 홍보를 위한 인스타그램, 링크드인 포스팅 문구와 해시태그를 작성해줘."))

        # 단계별 실행
        for i, (step_name, task) in enumerate(steps):
            with st.expander(f"🟢 {step_name} 작업 완료", expanded=True):
                with st.spinner("작업 중..."):
                    result = run_agent_step(step_name, task, full_context)
                    st.markdown(result)
                    full_context += f"\n\n[{step_name}]\n{result}"
            
            progress_bar.progress((i + 1) / len(steps))

        # [기능 1] SNS 자동 포스팅 시뮬레이션
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
        st.success("✅ 선택한 PM 기법에 맞춘 모든 프로젝트 세팅이 완료되었습니다!")
