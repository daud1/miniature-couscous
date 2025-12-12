from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.common.custom_exception import CustomException
from src.common.logger import get_logger
from src.config.settings import settings
from src.llm.llm_factory import get_llm
from src.models.question_schemas import FillBlankQuestion, MCQQuestion
from src.prompts.templates import (
    fill_blank_prompt_template,
    mcq_prompt_template,
)


class QuestionGenerator:
    def __init__(self, provider: str = "Groq", model: str = "llama-3.1-8b-instant"):
        self.llm = get_llm(provider, model)
        self.provider = provider
        self.model = model
        self.logger = get_logger(self.__class__.__name__)

    def _format_previous_questions_context(self, previous_questions):
        if not previous_questions:
            return ""

        context = "Previously generated questions (DO NOT duplicate or rephrase these):\n"
        for i, q in enumerate(previous_questions, 1):
            context += f"{i}. {q.get('question', '')}\n"
        context += "\n"
        return context

    def _is_duplicate(self, new_question, previous_questions):
        if not previous_questions:
            return False

        new_q_lower = new_question.lower().strip()

        for prev_q in previous_questions:
            prev_q_text = prev_q.get("question", "").lower().strip()

            if new_q_lower == prev_q_text:
                return True

            words_new = set(new_q_lower.split())
            words_prev = set(prev_q_text.split())

            if len(words_new) > 0 and len(words_prev) > 0:
                overlap_ratio = len(words_new.intersection(words_prev)) / len(
                    words_new.union(words_prev)
                )
                if overlap_ratio > 0.7:
                    return True

        return False

    def _retry_and_parse(self, prompt, parser, topic, difficulty, previous_questions=None):
        if previous_questions is None:
            previous_questions = []

        previous_context = self._format_previous_questions_context(previous_questions)

        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(
                    f"Generating question for topic {topic} with difficulty {difficulty} using {self.provider}/{self.model}"
                )

                formatted_prompt = prompt.format(
                    topic=topic,
                    difficulty=difficulty,
                    previous_questions_context=previous_context,
                )

                response = self.llm.invoke([HumanMessage(content=formatted_prompt)])

                parsed = parser.parse(response.content)

                question_text = parsed.question if hasattr(parsed, "question") else str(parsed)

                if self._is_duplicate(question_text, previous_questions):
                    self.logger.warning(
                        f"Detected duplicate question, retrying... (attempt {attempt + 1})"
                    )
                    if attempt < settings.MAX_RETRIES - 1:
                        continue
                    else:
                        raise ValueError("Unable to generate unique question after retries")

                self.logger.info("Successfully parsed the question")

                return parsed

            except Exception as e:
                self.logger.error(f"Error coming : {str(e)}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(
                        f"Generation failed after {settings.MAX_RETRIES} attempts", e
                    )

    def generate_mcq(
        self, topic: str, difficulty: str = "medium", previous_questions=None
    ) -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)

            question = self._retry_and_parse(
                mcq_prompt_template, parser, topic, difficulty, previous_questions
            )

            if len(question.options) != 4 or question.correct_answer not in question.options:
                raise ValueError("Invalid MCQ Structure")

            self.logger.info("Generated a valid MCQ Question")
            return question

        except Exception as e:
            self.logger.error(f"Failed to generate MCQ : {str(e)}")
            raise CustomException("MCQ generation failed", e)

    def generate_fill_blank(
        self, topic: str, difficulty: str = "medium", previous_questions=None
    ) -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(
                fill_blank_prompt_template, parser, topic, difficulty, previous_questions
            )

            if "___" not in question.question:
                raise ValueError("Fill in blanks should contain '___'")

            self.logger.info("Generated a valid Fill in Blanks Question")
            return question

        except Exception as e:
            self.logger.error(f"Failed to generate fillups : {str(e)}")
            raise CustomException("Fill in blanks generation failed", e)
