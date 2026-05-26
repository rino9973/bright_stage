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
if 'mistakes' not in st.session_state:
    st.session_state.mistakes = []
    
# ★追加：回答フェーズか、結果確認フェーズかを判定する記憶
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False

# --- 画面の表示 ---

# 【1. ホーム画面】
if st.session_state.page == 'home':
    st.title("📖 英語問題集")
    st.write("始めるコースを選択してください")
    
    if st.button("基礎のみ"):
        st.session_state.questions = [q for q in all_questions if q.get('type') == '基礎']
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.answered = False # クイズ開始時に状態をリセット
        st.session_state.page = 'quiz'
        st.rerun()

    if st.button("応用のみ"):
        st.session_state.questions = [q for q in all_questions if q.get('type') == '応用']
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.answered = False # クイズ開始時に状態をリセット
        st.session_state.page = 'quiz'
        st.rerun()
        
    st.divider()
    st.subheader("復習")
    
    mistakes_count = len(st.session_state.mistakes)
    if mistakes_count > 0:
        mistake_ids = [f"問題{q['id']}" for q in st.session_state.mistakes]
        st.info(f"📝 現在間違えている問題: {', '.join(mistake_ids)}")
    
    if st.button(f"間違えた問題をやり直す ({mistakes_count}問)", disabled=(mistakes_count == 0)):
        st.session_state.questions = st.session_state.mistakes.copy()
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.answered = False # クイズ開始時に状態をリセット
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

        # パターンA：まだ回答していない時の画面
        if not st.session_state.answered:
            if "options" in q:
                user_choice = st.radio("選択してください:", q['options'], index=None)
                if st.button("回答する", disabled=(user_choice is None)):
                    st.session_state.answered = True # 回答済みにする
                    st.session_state.is_correct = (user_choice == q['answer'])
                    st.rerun() # 画面をリロード
            else:
                user_text = st.text_input("答えを入力してください:")
                if st.button("回答する", disabled=(user_text == "")):
                    st.session_state.answered = True # 回答済みにする
                    st.session_state.is_correct = (user_text.strip().lower() == q['answer'].lower())
                    st.rerun() # 画面をリロード

        # パターンB：回答した後の画面（結果と「次へ」ボタンを表示）
        else:
            if st.session_state.is_correct:
                st.success("⭕ 正解！")
            else:
                st.error(f"❌ 不正解... 正解は: {q['answer']} （問題{q['id']}）")
                if q not in st.session_state.mistakes:
                    st.session_state.mistakes.append(q)

            # ★エラーの原因になっていた部分（コロンを追加しています）
            if st.button("次へ", type="primary"):
                st.session_state.answered = False # 状態を「未回答」に戻す
                st.session_state.current_index += 1 # 次の問題へ
                st.rerun()
        
        st.divider()
        if st.button("中断してホームに戻る"):
            st.session_state.page = 'home'
            st.rerun()