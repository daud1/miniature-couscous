import os

import streamlit as st
from dotenv import load_dotenv

from src.config.settings import settings
from src.generator.question_generator import QuestionGenerator
from src.utils.helpers import QuizManager, rerun

load_dotenv()


def main():
    st.set_page_config(page_title="studdy Buddy", page_icon="🧑🏾‍🏫")

    if "quiz_manager" not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if "quiz_generated" not in st.session_state:
        st.session_state.quiz_generated = False

    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    if "rerun_trigger" not in st.session_state:
        st.session_state.rerun_trigger = False

    available_providers = settings.get_available_providers()

    if not available_providers:
        st.error(
            "No API keys configured. Please set at least one provider API key in your environment variables."
        )
        st.stop()

    if "provider" not in st.session_state:
        st.session_state.provider = available_providers[0]

    if "model" not in st.session_state:
        st.session_state.model = settings.PROVIDER_MODELS[st.session_state.provider][0]

    if st.session_state.provider not in available_providers:
        st.session_state.provider = available_providers[0]
        st.session_state.model = settings.PROVIDER_MODELS[st.session_state.provider][0]

    st.title("Study Buddy")

    if not st.session_state.quiz_generated:
        st.markdown(
            """
            Welcome to Study Buddy! Generate personalized quiz questions to test your knowledge on any topic.
            
            **How to use:**
            1. Select your question type (Multiple Choice or Fill in the Blank)
            2. Enter a topic you want to study
            3. Choose difficulty level and AI model
            4. Click "Generate Quiz" to create your questions
            5. Answer the questions and submit to see your results
            
            Get started by configuring your quiz settings in the sidebar!
            """
        )

    st.sidebar.header("Quiz Settings")

    question_type = st.sidebar.selectbox(
        "Select Question Type", ["Multiple Choice", "Fill in the Blank"], index=0
    )

    topic = st.sidebar.text_input("Enter Topic", placeholder="Indian History, geography")

    difficulty = st.sidebar.selectbox("Dificulty Level", ["Easy", "Medium", "Hard"], index=1)

    provider_index = 0
    if st.session_state.provider in available_providers:
        provider_index = available_providers.index(st.session_state.provider)

    provider = st.sidebar.selectbox("Select Provider", available_providers, index=provider_index)

    if provider != st.session_state.provider:
        st.session_state.provider = provider
        st.session_state.model = settings.PROVIDER_MODELS[provider][0]

    available_models = settings.PROVIDER_MODELS[provider]
    model_index = 0
    if st.session_state.model in available_models:
        model_index = available_models.index(st.session_state.model)

    model = st.sidebar.selectbox("Select Model", available_models, index=model_index)
    st.session_state.model = model

    num_questions = st.sidebar.number_input(
        "Number of Questions", min_value=1, max_value=10, value=5
    )

    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False

        with st.spinner(
            f"Generating {num_questions} {question_type.lower()} question(s) about {topic}..."
        ):
            generator = QuestionGenerator(provider=provider, model=model)
            succces = st.session_state.quiz_manager.generate_questions(
                generator, topic, question_type, difficulty, num_questions
            )

        st.session_state.quiz_generated = succces
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("Quiz")
        
        # Download button for questions and answers - only visible when questions exist
        doc_content, filename = st.session_state.quiz_manager.generate_questions_answers_document()
        if doc_content and filename:
            st.download_button(
                label="📥 Download Questions & Answers",
                data=doc_content,
                file_name=filename,
                mime="text/plain",
            )
        
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()

    if st.session_state.quiz_submitted:
        st.header("Quiz Results")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = results_df["is_correct"].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100
            st.write(f"Score : {score_percentage}")

            for _, result in results_df.iterrows():
                question_num = result["question_number"]
                if result["is_correct"]:
                    st.success(f"✅ Question {question_num} : {result['question']}")
                else:
                    st.error(f"❌ Question {question_num} : {result['question']}")
                    st.write(f"Your answer : {result['user_answer']}")
                    st.write(f"Correct answer : {result['correct_answer']}")

                st.markdown("-------")

            if st.button("Save Results"):
                saved_file = st.session_state.quiz_manager.save_to_csv()
                if saved_file:
                    with open(saved_file, "rb") as f:
                        st.download_button(
                            label="Downlaod Results",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime="text/csv",
                        )
                else:
                    st.warning("No results avialble")


if __name__ == "__main__":
    main()
