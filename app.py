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

# --- ★拡張：URLと記憶の同期（自動セーブ・ロード機能） ---
# 1. アプリ起動時にURLから「間違えた問題」と「現在の進捗」を復元する
if 'mistakes' not in st.session_state:
    url_mistakes = st.query_params.get("mistakes", "")
    if url_mistakes:
        mistake_ids = [int(x) for x in url_mistakes.split(",")]
        st.session_state.mistakes = [q for q in all_questions if q['id'] in mistake_ids]
    else:
        st.session_state.mistakes = []

if 'questions' not in st.session_state:
    url_q_ids = st.query_params.get("q_ids", "")
    url_idx = st.query_params.get("idx", "0")
    
    if url_q_ids:
        # URLに保存されている問題IDの並び順（シャッフルされた状態）をそのまま復元
        q_ids = [int(x) for x in url_q_ids.split(",")]
        id_to_q = {q['id']: q for q in all_questions}
        st.session_state.questions = [id_to_q[qid] for qid in q_ids if qid in id_to_q]
        st.session_state.current_index = int(url_idx)
    else:
        st.session_state.questions = []
        st.session_state.current_index = 0

# 2. 状態が変わるたびにURLを書き換えるセーブ関数
def save_to_url():
    # 間違えた問題の保存
    if st.session_state.mistakes:
        m_ids = [str(q['id']) for q in st.session_state.mistakes]
        st.query_params["mistakes"] = ",".join(m_ids)
    else:
        if "mistakes" in st.query_params:
            del st.query_params["mistakes"]
            
    # 解いている途中の問題リストと、何問目かのインデックスを保存
    if st.session_state.questions and st.session_state.current_index < len(st.session_state.questions):
        q_ids = [str(q['id']) for q in st.session_state.questions]
        st.query_params["q_ids"] = ",".join(q_ids)
        st.query_params["idx"] = str(st.session_state.current_index)
    else:
        # 全問解き終わっているか、まだ始めていない時はURLを綺麗にする
        if "q_ids" in st.query_params:
            del st.query_params["q_ids"]
        if "idx" in st.query_params:
            del st.query_params["idx"]

# --- セッション状態（記憶）の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False

# --- 画面の表示 ---

# 【1. ホーム画面】
if st.session_state.page == 'home':
    st.title("📖 英語問題集")
    
    # ★追加：途中の進捗が残っている場合、一番上に目立つ「再開ボタン」を自動表示
    has_progress = len(st.session_state.questions) > 0 and st.session_state.current_index < len(st.session_state.questions)
    if has_progress:
        current_num = st.session_state.current_index + 1
        total_num = len(st.session_state.questions)
        if st.button(f"⏯️ 前回の続きから再開する (第 {current_num} 問から / 全 {total_num} 問)", type="primary", use_container_width=True):
            st.session_state.page = 'quiz'
            st.rerun()
        st.divider()
    
    st.write("新しくコースを選択して始める場合はこちら:")
    
    if st.button("基礎のみ", use_container_width=True):
        st.session_state.questions = [q for q in all_questions if q.get('type') == '基礎']
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.answered = False
        save_to_url() # 新しい問題セットをURLにセーブ
        st.session_state.page = 'quiz'
        st.rerun()

    if st.button("応用のみ", use_container_width=True):
        st.session_state.questions = [q for q in all_questions if q.get('type') == '応用']
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.answered = False
        save_to_url() # 新しい問題セットをURLにセーブ
        st.session_state.page = 'quiz'
        st.rerun()
        
    st.divider()
    st.subheader("復習")
    
    mistakes_count = len(st.session_state.mistakes)
    if mistakes_count > 0:
        mistake_ids = [f"問題{q['id']}" for q in st.session_state.mistakes]
        st.info(f"📝 現在間違えている問題: {', '.join(mistake_ids)}")
    
    if st.button(f"間違えた問題をやり直す ({mistakes_count}問)", disabled=(mistakes_count == 0), use_container_width=True):
        st.session_state.questions = st.session_state.mistakes.copy()
        random.shuffle(st.session_state.questions)
        st.session_state.current_index = 0
        st.session_state.answered = False
        st.session_state.mistakes = []
        save_to_url() # やり直し開始時にURLを上書き
        st.session_state.page = 'quiz'
        st.rerun()

# 【2. クイズ画面】
elif st.session_state.page == 'quiz':
    total = len(st.session_state.questions)
    current = st.session_state.current_index
    
    if current >= total:
        st.success("🎉 全ての問題が終了しました！")
        if st.button("ホームに戻る", use_container_width=True):
            st.session_state.questions = []
            st.session_state.current_index = 0
            save_to_url() # 終了したのでURLから進捗を削除
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
                    st.session_state.answered = True
                    st.session_state.is_correct = (user_choice == q['answer'])
                    st.rerun()
            else:
                user_text = st.text_input("答えを入力してください:")
                if st.button("回答する", disabled=(user_text == "")):
                    st.session_state.answered = True
                    st.session_state.is_correct = (user_text.strip().lower() == q['answer'].lower())
                    st.rerun()

        # パターンB：回答した後の画面
        else:
            if st.session_state.is_correct:
                st.success("⭕ 正解！")
            else:
                st.error(f"❌ 不正解... 正解は: {q['answer']} （問題{q['id']}）")
                if q not in st.session_state.mistakes:
                    st.session_state.mistakes.append(q)
                    save_to_url() # 間違えたら即座にURLに保存

            if st.button("次へ", type="primary"):
                st.session_state.answered = False
                st.session_state.current_index += 1
                save_to_url() # 次の問題に進んだらURLを更新！
                st.rerun()
        
        st.divider()
        if st.button("中断してホームに戻る", use_container_width=True):
            save_to_url() # 中断時の位置を確実にURLに保存
            st.session_state.page = 'home'
            st.rerun()
