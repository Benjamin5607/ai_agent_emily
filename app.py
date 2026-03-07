import streamlit as st
from groq import Groq

# 1. 초기 설정 (모바일 최적화 레이아웃)
st.set_page_config(page_title="Emily: AI Agent", layout="centered")
st.title("🚀 AI Agent Emily")
st.caption("아이디어 하나로 실무 전체를 설계합니다. (Powered by Groq)")

# 2. Groq 클라이언트 설정 (Secrets에서 API 키 가져오기)
# GitHub Secrets나 Streamlit Secrets에 GROQ_API_KEY를 저장하세요.
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def run_emily_agent(role, task, context=""):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": f"당신은 {role} 전문가 에밀리입니다. 모바일 가독성을 위해 불렛포인트와 표를 적극 사용하세요."},
            {"role": "user", "content": f"이전 단계 내용: {context}\n\n수행할 작업: {task}"}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

# 3. 사용자 입력
idea = st.text_input("💡 어떤 아이디어가 떠오르셨나요?", placeholder="예: 1인 가구를 위한 밀키트 구독 서비스")

if st.button("에밀리 가동! 🏃‍♀️"):
    if not idea:
        st.warning("아이디어를 입력해주세요!")
    else:
        # 에이전트 단계별 실행
        steps = [
            ("🏗️ 설계", "이 아이디어의 시스템 아키텍처와 핵심 기능을 설계해줘."),
            ("📊 데이터 분석", "시장성 분석과 가상의 타겟 유저 데이터를 생성해줘."),
            ("📅 프로젝트 플래닝", "런칭까지의 4주간의 WBS(업무 일정)를 짜줘."),
            ("⚙️ 운영 전략", "런칭 후 초기 운영 및 마케팅 전략을 세워줘."),
            ("📈 평가 및 지표", "성공 여부를 판단할 핵심 지표(KPI)와 리스크 관리 방안을 제안해줘.")
        ]
        
        full_context = f"아이디어: {idea}"
        
        for step_name, task in steps:
            with st.expander(step_name, expanded=True):
                with st.spinner(f"{step_name} 진행 중..."):
                    result = run_emily_agent(step_name, task, full_context)
                    st.markdown(result)
                    full_context += f"\n\n[{step_name}]\n{result}"
                    
        st.success("✅ 에밀리가 모든 실무 설계를 마쳤습니다!")
