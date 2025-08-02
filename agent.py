import re
import spacy
import textstat
from collections import Counter
import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import numpy as np
import math
import logging

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

logger.info("Loaded Modules...")
#nltk.download('punkt') # This has to be only run once
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

logger.info("Initializing Tools...")

class StyleAnalyzer:
    def __init__(self, use_weights=True):
        self.use_weights = use_weights

        # Custom sets for stylistic markers
        self.informal_words = set([
            "yo", "gonna", "wanna", "dude", "bro", "lol", "bruh", "nah", "yeah", "lmao", "omg", "wassup", "howdya", "mate", "doug", "chillin", "kinda", "yikes", "bummer", "outta","hella", "legit", "meh", "ugh"
        ])
        self.connectives = set([
            "however", "because", "therefore", "although", "but", "since", "so", "yet", "though", "thus"
        ])

        # Optional: manually define weights for each feature (same order as below)
        self.feature_names = [
            'connective_density', 'pronoun_density', 'lexical_overlap',
            'avg_sentence_length', 'clause_density', 'passive_voice_ratio',
            'avg_word_length', 'avg_syllables_per_word', 'type_token_ratio',
            'informal_word_density', 'flesch_kincaid', 'smog', 'gunning_fog',
            'noun_ratio', 'verb_ratio', 'adj_ratio', 'adv_ratio',
            'contraction_density', 'exclamation_density', 'question_density', 'emoji_density'
        ]
        self.weights = np.array([
            1, 1, 1,    # cohesion
            1.5, 1.4, 1.2,    # syntax
            1.1, 1.0, 1.0,    # lexical
            1.3, 1.5, 2.5, 2.5,  # readability
            1.1, 1.1, 1.0, 1.0,  # pos
            1.2, 1.0, 1.0, 1.0   # style markers
        ]) if self.use_weights else np.ones(21)
    
    def extract(self, text):
        doc = nlp(text)
        sentences = list(doc.sents)
        words = [token.text for token in doc if token.is_alpha]
        word_count = len(words)
        pos_counts = Counter([token.pos_ for token in doc])

        return {
            'connective_density': sum(w.lower_ in self.connectives for w in doc) / max(1, word_count),
            'pronoun_density': sum(t.pos_ == "PRON" for t in doc) / max(1, word_count),
            'lexical_overlap': len(set(w.lower() for w in words if len(w) > 3)) / max(1, len(words)),

            'avg_sentence_length': word_count / max(1, len(sentences)),
            'clause_density': sum(1 for token in doc if token.dep_ in ["ccomp", "advcl", "relcl"]) / max(1, len(sentences)),
            'passive_voice_ratio': sum(1 for token in doc if token.dep_ == "auxpass") / max(1, len(sentences)),

            'avg_word_length': sum(len(w) for w in words) / max(1, word_count),
            'avg_syllables_per_word': textstat.syllable_count(text) / max(1, word_count),
            'type_token_ratio': len(set(words)) / max(1, word_count),

            'informal_word_density': sum(w.lower() in self.informal_words for w in words) / max(1, word_count),

            'flesch_kincaid': textstat.flesch_kincaid_grade(text),
            'smog': textstat.smog_index(text),
            'gunning_fog': textstat.gunning_fog(text),

            'noun_ratio': pos_counts["NOUN"] / max(1, word_count),
            'verb_ratio': pos_counts["VERB"] / max(1, word_count),
            'adj_ratio': pos_counts["ADJ"] / max(1, word_count),
            'adv_ratio': pos_counts["ADV"] / max(1, word_count),

            'contraction_density': len(re.findall(r"\b\w+'\w+", text)) / max(1, word_count),
            'exclamation_density': text.count("!") / max(1, len(sentences)),
            'question_density': text.count("?") / max(1, len(sentences)),
            'emoji_density': len(re.findall(r"[^\w\s,.!?;:]", text)) / max(1, word_count),
        }

    def style_similarity(self, features1, features2):
        # Convert to arrays in fixed order
        vec1 = np.array([features1[k] for k in self.feature_names])
        vec2 = np.array([features2[k] for k in self.feature_names])

        # Apply feature weights
        diff = (vec1 - vec2) * self.weights
    
        # Compute normalized similarity (inverse of distance)
        distance = np.linalg.norm(diff)  # Euclidean
        similarity = 1 / (1 + distance)  # Bound between 0 and 1
    
        return similarity
    
    def get_qualitative_level(self, value, type="ratio"):
        """
        Provides a simplified qualitative description based on a numerical value.
        Note: The thresholds used here are general heuristics and may need
        domain-specific tuning for more precise interpretations.
    
        Args:
            value (float): The numerical value of the feature.
            type (str): The type of feature ('ratio', 'length', 'readability_grade', 'smog_index').
    
        Returns:
            str: A qualitative description (e.g., "low", "moderate", "easy to read").
        """
        if type == "ratio":
            if value < 0.02:
                return "very low"
            elif value < 0.05:
                return "low"
            elif value < 0.15:
                return "moderate"
            elif value < 0.3:
                return "high"
            else:
                return "very high"
        elif type == "length": # For average word/sentence length or syllables
            if value < 5:
                return "short"
            elif value < 10:
                return "moderate"
            else:
                return "long"
        elif type == "readability_grade": # For Flesch-Kincaid, Gunning-Fog
            if value < 6:
                return "very easy to read (suitable for early elementary grades)"
            elif value < 9:
                return "easy to read (suitable for middle school grades)"
            elif value < 12:
                return "moderately easy to read (suitable for high school grades)"
            elif value < 15:
                return "somewhat difficult to read (suitable for college level)"
            else:
                return "difficult to read (suitable for graduate level or specialized texts)"
        elif type == "smog_index":
            if value < 8:
                return "very easy to read"
            elif value < 10:
                return "easy to read"
            elif value < 12:
                return "moderately easy to read"
            elif value < 14:
                return "somewhat difficult to read"
            else:
                return "difficult to read"
        return ""

    def describe_text_features(self, features_dict):
        """
        Converts a dictionary of numerical text features into a list of descriptive sentences.

        Args:
            features_dict (dict): A dictionary containing numerical text features,
                                such as 'connective_density', 'flesch_kincaid', etc.

        Returns:
            list: A list of strings, where each string is a descriptive sentence
                for a corresponding feature, including its value and a qualitative interpretation.
        """
        descriptions = []

        # Helper for formatting percentages
        def format_percent(value):
            if math.isnan(value):
                return "N/A" # Handle cases where value might be NaN (e.g., division by zero)
            return f"{value * 100:.1f}%"

        for key, value in features_dict.items():
            # Ensure the value is a number before processing
            if not isinstance(value, (int, float)) or math.isinf(value):
                descriptions.append(f"'{key}' has an invalid or non-numeric value: {value}. Skipping description.")
                continue

            if key == 'connective_density':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Connective word usage is {format_percent(value)}, indicating a {level} presence of linking words."
                )
            elif key == 'pronoun_density':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Pronoun usage is {format_percent(value)}, which is considered {level}."
                )
            elif key == 'lexical_overlap':
                # For lexical overlap, a higher value might mean less diversity if it's about repeated words.
                # Assuming it's about unique words over a certain length, higher is better for diversity.
                # Re-interpreting as "lexical diversity" where higher is good.
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Lexical diversity (based on unique words longer than 3 characters) is {format_percent(value)}, suggesting a {level} variety in vocabulary."
                )
            elif key == 'avg_sentence_length':
                level = self.get_qualitative_level(value, type="length")
                descriptions.append(
                    f"The average sentence length is {value:.1f} words, which is considered {level}."
                )
            elif key == 'clause_density':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Clause density (indicating structural complexity from subordinate, adverbial, or relative clauses) is {format_percent(value)}, which is a {level} level."
                )
            elif key == 'passive_voice_ratio':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Passive voice usage is {format_percent(value)}, indicating a {level} preference for passive constructions."
                )
            elif key == 'avg_word_length':
                level = self.get_qualitative_level(value, type="length")
                descriptions.append(
                    f"The average word length is {value:.1f} characters, which is considered {level}."
                )
            elif key == 'avg_syllables_per_word':
                level = self.get_qualitative_level(value, type="length") # Reusing 'length' for general magnitude of complexity
                descriptions.append(
                    f"The average number of syllables per word is {value:.1f}, indicating {level} word complexity."
                )
            elif key == 'type_token_ratio':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"The Type-Token Ratio (vocabulary richness) is {format_percent(value)}, suggesting a {level} diversity in word choice."
                )
            elif key == 'informal_word_density':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Informal language usage is {format_percent(value)}, indicating a {level} presence of informal words."
                )
            elif key == 'flesch_kincaid':
                level = self.get_qualitative_level(value, type="readability_grade")
                descriptions.append(
                    f"The Flesch-Kincaid readability grade is {value:.1f}, meaning the text is {level}."
                )
            elif key == 'smog':
                level = self.get_qualitative_level(value, type="smog_index")
                descriptions.append(
                    f"The SMOG readability index is {value:.1f}, suggesting the text is {level}."
                )
            elif key == 'gunning_fog':
                level = self.get_qualitative_level(value, type="readability_grade")
                descriptions.append(
                    f"The Gunning-Fog readability score is {value:.1f}, indicating the text is {level}."
                )
            elif key == 'noun_ratio':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"The proportion of nouns is {format_percent(value)}, which is a {level} ratio of nouns in the text."
                )
            elif key == 'verb_ratio':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"The proportion of verbs is {format_percent(value)}, which is a {level} ratio of verbs in the text."
                )
            elif key == 'adj_ratio':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"The proportion of adjectives is {format_percent(value)}, which is a {level} ratio of adjectives in the text."
                )
            elif key == 'adv_ratio':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"The proportion of adverbs is {format_percent(value)}, which is a {level} ratio of adverbs in the text."
                )
            elif key == 'contraction_density':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Contraction usage is {format_percent(value)}, indicating a {level} presence of contractions."
                )
            elif key == 'exclamation_density':
                # Assuming this is density per sentence, not per word
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Exclamation mark usage is {format_percent(value)}, which is a {level} density per sentence."
                )
            elif key == 'question_density':
                # Assuming this is density per sentence, not per word
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Question mark usage is {format_percent(value)}, which is a {level} density per sentence."
                )
            elif key == 'emoji_density':
                level = self.get_qualitative_level(value)
                descriptions.append(
                    f"Emoji or special symbol usage is {format_percent(value)}, indicating a {level} presence of such characters."
                )
            else:
                descriptions.append(f"Unknown feature '{key}' with value: {value}. No specific description available.")
        return descriptions

    
analyzer = StyleAnalyzer(use_weights=True)

def get_style(text1: str) -> str:
    """
    Use this function to get the writing style of a text

    Args:
        text1 (str): text to get the writing style of

    Returns:
        str: Text describing the style of the text
    """
    f1 = analyzer.extract(text1)
    return analyzer.describe_text_features(f1)

def extract_questions_from_text(text: str) -> dict:
    """
    Extracts numbered questions from a model response like:
    {1: Some question}
    Returns a dictionary { "1": "Some question" }
    """
    question_pattern = re.findall(r"\{(\d+):\s*(.*?)\}", text)
    return {qid: question.strip() for qid, question in question_pattern}

def generate_email_reply(thread_summary: str, style_hint: str, additional_info:str) -> str:
    """
    Use this function to generate an email reply based on a thread summary, relevant messages, and a style hint.

    Args:
        thread_summary (str): A summary of the email thread. You may add parts from the relevant messages if you like.
        style_hint (str): A hint describing the desired style for the email reply

    Returns:
        str: The generated email reply.
    """
    system_prompt = """
You are an AI email assistant. Your task is to write an email reply using:
- The thread summary
- The user's writing style
- User Instructions provided using a question and answer format.


Respond ONLY like this:
FINAL ANSWER:
<the full reply>

DO NOT make assumptions. Only use the content provided.
DO NOT guess the user's response to requests or questions.

The user's writing style is already provided.
"""

    user_prompt = f"""
    Thread Summary:
    {thread_summary}

    User writing style: {style_hint}

    Additional info :{additional_info}
    Write the reply to the given thread:
    """

    chat_completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return chat_completion.choices[0].message.content

def check_missing_info(thread_summary: str, recipient:str, additional_info:str) -> dict:
    """
    Ask the model if anything is unclear or missing before generating a reply.

    Returns:
        - {"status": "ok"} if everything is clear
        - {"status": "clarification", "questions": {id: question}} otherwise
    """
    
    system_prompt = """You are an assistant that ensures that all the necessary information is present in order to reply to a given
    mail thread. The email thread that you have been provided contains the main discussion points, open questions that need to be answered and the tone of the conversation 
    previously had. You are the recipient of the mail. You are also provided with answers to previous questions that you have asked if available.
    You have to ask questions in order to determine what the recipient would answer to the thread. If you have all the information required to 
    determine how the recipient would answer from the thread itself, you do not need to ask questions. If the user does not wish to provide information regarding certain facts
    consider those information to be answered and ignore them from your output.
    Use the exact format as mentioned in your reply. DO NOT answer in any other format.

STRICT RULES:
1. Your quesions should be in the following format only, no other output is permitted. You may ask multiple questions in this format.
{1: <your question>}

2. If you are certain that all the information that you require to reply as the recipient is present then respond ONLY like this:
FINAL ANSWER:
<Your summary of the missing information that you have gathered, If no information was missing just answer "NILL">

DO NOT ask too many questions as it would lead to disturbing the user
DO NOT make assumptions. Only use the content provided.
DO NOT guess the user's response to requests or questions.
Make sure you have all the details present to answer the mail from the perspective of the user.
"""
    precheck_prompt = f"""
    You are {recipient} the recipient.
Thread Summary:
{thread_summary}

Answers to previous questions: 
{additional_info}
"""
    #print("User prompt :", precheck_prompt, "\n\n")

    chat_completion = client.chat.completions.create (
        model= "meta-llama/llama-4-scout-17b-16e-instruct",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": precheck_prompt}
        ],
        temperature=0.0,
        max_tokens=300
    )

    response = chat_completion.choices[0].message.content.strip()
    
    #print("Response :", response)
    # Use your regex extractor from earlier
    questions = extract_questions_from_text(response)
    if questions:
        return {"status": "clarification", "questions": questions}
    
    return {"status": "unknown", "raw": response}

def get_answers(questions:dict):
    answers = {}
    for i, question in questions.items():
        answers[question] = input(question)
    return answers

def summarize_threads(full_thread_text:str) -> str :

    """
    Use this function to summarize a given thread of mails.

    Args:
        full_thread_text (str): The thread of mails to summarize.

    Returns:
        str: Summarized text.

    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": 
                """Summarize the following email thread into 3-5 bullet points, capturing:
                - Main discussion points
                - Relevant and important information to keep in mind
                - Any open questions or pending actions
                - The tone of the conversation (formal/informal)

                Your output should be in the following manner:
                **Summary:**
                <Summary of the provided thread>
                """
            },
            {
                "role": "user",
                "content" : f"Email Thread: {full_thread_text}"
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )

    return chat_completion.choices[0].message.content

def run_email_assistant(thread_summary: str, style_hint: str, recipient: str, additional_info = "") -> str:
    """
    End-to-end email assistant.
    - Repeatedly asks questions until the model is satisfied.
    - Accumulates clarification answers.
    - Generates reply using all gathered info.
    """
    result = check_missing_info(thread_summary, recipient, additional_info)

    if result["status"] == "unknown":
        match = re.search(r"FINAL ANSWER:\s*(.*)", result.get("raw", ""), re.DOTALL)
        if match:
            logger.info("\Ready to generate final reply...\n")
            #reply = generate_email_reply(thread_summary, style_hint, additional_info)
            return "FINAL ANSWER" #Tells that the model is ready to print the final answer
        else:
            logger.warning("⚠️ Unrecognized output:\n", result.get("raw", ""))
            return "MODEL ERROR"

    if result["status"] == "clarification":
        return result["questions"] # return the questions the model wants to ask
        #continue


logger.info("Finished Initializing Tools ....\n\n")


#Test Material
user_style = """
Connective word usage is 4.0%, indicating a low presence of linking words.
Pronoun usage is 8.0%, which is considered moderate.
Lexical diversity (based on unique words longer than 3 characters) is 65.0%, suggesting a very high variety in vocabulary.
The average sentence length is 15.2 words, which is considered long.
Clause density (indicating structural complexity from subordinate, adverbial, or relative clauses) is 12.0%, which is a moderate level.
Passive voice usage is 3.0%, indicating a low preference for passive constructions.
The average word length is 4.8 characters, which is considered short.
The average number of syllables per word is 1.5, indicating short word complexity.
The Type-Token Ratio (vocabulary richness) is 55.0%, suggesting a very high diversity in word choice.
Informal language usage is 0.5%, indicating a very low presence of informal words.
The Flesch-Kincaid readability grade is 7.5, meaning the text is easy to read (suitable for middle school grades).
The SMOG readability index is 9.0, suggesting the text is easy to read.
The Gunning-Fog readability score is 9.8, indicating the text is moderately easy to read (suitable for high school grades).
The proportion of nouns is 22.0%, which is a high ratio of nouns in the text.
The proportion of verbs is 18.0%, which is a high ratio of verbs in the text.
The proportion of adjectives is 7.0%, which is a moderate ratio of adjectives in the text.
The proportion of adverbs is 5.0%, which is a moderate ratio of adverbs in the text.
Contraction usage is 1.0%, indicating a very low presence of contractions.
Contraction usage is 1.0%, indicating a very low presence of contractions.
Exclamation mark usage is 0.2%, which is a very low density per sentence.
Question mark usage is 0.8%, which is a very low density per sentence.
Emoji or special symbol usage is 0.0%, indicating a very low presence of such characters.
"""

email_thread = """
From: Rajiv Mehta (BizDev Lead)
Subject: Re: Strategic Partnership with Novatech

Hi team,

Following our call with Novatech, here’s where things stand:

They’re interested in integrating our analytics API into their retail dashboard.

They're proposing a co-branded feature launch by mid-September.

They’ve asked for access to our sandbox environment by next Monday (July 22).

Open questions:

Do we want to offer this under a revenue-share model or flat licensing fee?

Who can lead the integration on our side? I was thinking Aditi or Tanmay.

Legal wants a draft of the MOU by Friday – who can help own that?

Let me know your thoughts.

– Rajiv

From: Aditi Kapoor
Subject: Re: Strategic Partnership with Novatech

Hey Rajiv,

This is exciting! I can take the lead on the integration, but I’ll need support from backend for OAuth and data anonymization work.

@Tanmay – can you handle the data handling & sync logic?

Also, a flat licensing model might be cleaner for V1, especially with fixed usage limits. But let’s validate with finance.

Best,
Aditi

From: Tanmay Rao
Subject: Re: Strategic Partnership with Novatech

Sure, I’m in.

Quick question: what’s the estimated data volume we’re exposing? That affects how we handle caching and rate-limiting.

@Aditi – we may also need to revisit the data usage logging module. It’s still in alpha.

Also +1 on flat fee model to start. Revenue-share needs stronger tracking infra.

– Tanmay

From: Meera Joshi (Legal)
Subject: Re: Strategic Partnership with Novatech

Hi everyone,

I can help with the MOU draft — but I need:

Confirmation on pricing model

API usage limits

SLA commitment (uptime, support)

Please get these to me by Thursday EOD, latest.

Thanks,
Meera

From: Rajiv Mehta
Subject: Re: Strategic Partnership with Novatech

Thanks all.

Action items:

Aditi: Lead integration, coordinate backend needs.

Tanmay: Handle data sync logic, confirm logging status.

Meera: Draft MOU (once inputs confirmed).

Rajiv: Loop in finance for pricing feedback, and reply to Novatech by Monday.

Still pending:

Final call on pricing model

Projected data volume

SLA terms (uptime, response time, support tiers)

Let’s try to close all loose ends by Thursday noon so Meera can get started.

Best,
Rajiv


"""
email_thread2 = """
From: Rajiv Mehta
Subject: Partnership Discussion with Novatech

Hi Aditi,

Following up on our call with Novatech — they’re interested in using our analytics API in their dashboard and want to start integration by mid-September.

They've requested sandbox access by next Monday (July 22), and they’re asking if we prefer a flat licensing model or revenue-sharing.

Can you confirm if you’re available to lead the integration? Also, would you prefer we go with a flat fee for now?

Let me know your thoughts. I’ll loop in Legal once we finalize direction.

Best,  
Rajiv
vbnet
Copy
Edit
From: Aditi Kapoor
Subject: Re: Partnership Discussion with Novatech

Hi Rajiv,

I’d be happy to lead the integration. I’ll need some support from backend for OAuth and data access controls.

As for pricing, I’d lean toward a flat license for now — simpler to manage. We can revisit revenue-sharing once we see traction.

Let me know if you need me to sync with Tanmay on the technical side.

– Aditi"""
email_thread3 = """
From: Anil
Subject: Confirmation of the order placement

I have placed the order for the new data servers. Will talk to you about it later.

Regards
Anil
"""

#summary = summarize_threads(email_thread3).split("**Summary:**")[1]
#
#print("===============\nSummary :" , summary, "\n===============\n")
#
#run_email_assistant(summary, user_style, "Ravi")