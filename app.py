import streamlit as st
import json
import os
import random

# --- データの読み込み ---
@st.cache_data
def load_all_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'question.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

all_questions = load_all_questions()

# --- セッション状態（記憶）の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
# ★間違えた問題を記録するリストを追加
if 'mistakes' not in st.session_state:
    st.session_state.mistakes = []

# --- 画面の表示 ---

# 【1. ホーム画面】
if st.session_state.page == 'home':
    st.title("📖 英語問題集")
    st.write("始めるコースを選択してください")
    
    if st.button("基礎のみ"):
        st.session_state.questions = [q for q in all_questions if q.get('type') == '基礎']
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.page = 'quiz'
        st.rerun()

    if st.button("応用のみ"):
        st.session_state.questions = [q for q in all_questions if q.get('type') == '応用']
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.page = 'quiz'
        st.rerun()
        
    st.divider()
    st.subheader("復習")
    
    # ★間違えた問題ボタン（0問の時は無効化される）
    mistakes_count = len(st.session_state.mistakes)
    if st.button(f"間違えた問題をやり直す ({mistakes_count}問)", disabled=(mistakes_count == 0)):
        # 間違えた問題のリストをクイズのキューにセット
        st.session_state.questions = st.session_state.mistakes.copy()
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        # やり直しを開始したら、一度記録をリセットする（再度間違えたらまた追加される）
        st.session_state.mistakes = []
        st.session_state.page = 'quiz'
        st.rerun()

# 【2. クイズ画面】
elif st.session_state.page == 'quiz':
    total = len(st.session_state.questions)
    current = st.session_state.current_index
    
    if current >= total:
        st.success("🎉 全ての問題が終了しました！")
        if st.button("ホームに戻る"):
            st.session_state.page = 'home'
            st.rerun()
    else:
        q = st.session_state.questions[current]
        
        st.progress((current) / total)
        st.write(f"**第 {current + 1} 問 / {total} 問**")
        st.subheader(q['question'])

        # ★判定処理（正解・不正解時の動きをまとめました）
        def check_answer(is_correct):
            if is_correct:
                st.success("⭕ 正解！")
            else:
                st.error(f"❌ 不正解... 正解は: {q['answer']}")
                # 不正解だった場合、間違いリストに追加（重複防止つき）
                if q not in st.session_state.mistakes:
                    st.session_state.mistakes.append(q)
            
            st.session_state.current_index += 1
            import time
            time.sleep(1.2) # 少し結果を見せてから次へ
            st.rerun()

        # 選択肢がある場合
        if "options" in q:
            user_choice = st.radio("選択してください:", q['options'], index=None)
            if st.button("回答する", disabled=(user_choice is None)):
                check_answer(user_choice == q['answer'])
        # 記述式の場合
        else:
            user_text = st.text_input("答えを入力してください:")
            if st.button("回答する", disabled=(user_text == "")):
                check_answer(user_text.strip().lower() == q['answer'].lower())
        
        st.divider()
        if st.button("中断してホームに戻る"):
            st.session_state.page = 'home'
            st.rerun()