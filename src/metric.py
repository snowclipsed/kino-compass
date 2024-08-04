import llama_cpp
import llama_cpp.llama_tokenizer
from groq import Groq
from typing import List, Union, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json

class Slang(BaseModel):
    is_internet_slang: bool

class Word(BaseModel):
    x_aspect: str
    x_positive: str
    x_negative: str
    y_aspect: str
    y_positive: str
    y_negative: str


class Rating(BaseModel):
    x_value: int
    y_value: int

class Model:
    def __init__(self):
        self.model: Optional[Union[llama_cpp.Llama, Groq, None]] = None
        self.provider: Optional[str] = None

    def load_model(self) -> Union[llama_cpp.Llama, Groq, None]:
        if self.provider is None:
            raise ValueError("Provider must be set before loading the model")

        model_options = {
            "llama_cpp": self._load_llama_cpp,
            "groq": self._load_groq,
        }

        model_loader = model_options.get(self.provider)
        if model_loader is None:
            raise ValueError(f"Unsupported provider: {self.provider}")

        self.model = model_loader()
        return self.model

    def _load_llama_cpp(self):
        return llama_cpp.Llama.from_pretrained(
            repo_id="bartowski/Llama-3-Instruct-8B-SPPO-Iter3-GGUF",
            filename="Llama-3-Instruct-8B-SPPO-Iter3-Q4_K_M.gguf",
            tokenizer=llama_cpp.llama_tokenizer.LlamaHFTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct"),
            n_ctx=4096,
            n_gpu_layers=-1,
            verbose=False,
            temperature=0.2
        )

    def _load_groq(self):
        load_dotenv()
        return Groq(api_key=os.getenv("API_KEY"), max_retries=5)

    def unload_model(self):
        self.model = None
        self.provider = None

    def chunk_text(self, text: str, max_chars: int = 12000, overlap: int = 100):
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_chars and current_chunk:
                chunks.append(' '.join(current_chunk))
                overlap_words = current_chunk[-overlap:]
                current_chunk = overlap_words
                current_length = sum(len(w) + 1 for w in overlap_words) - 1

            current_chunk.append(word)
            current_length += len(word) + 1

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def is_slang(self, word: str):
        if self.provider == 'llama_cpp' and isinstance(self.model, llama_cpp.Llama):
            response = self.model.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": f"""Here is a {word}. Provide if it is an internet slang or not in the provided JSON schema. Here is the JSON schema:
                        """
                    }
                ],
                response_format={
                    "type": "json_object",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "is_internet_slang": {"type": "boolean"},
                        },
                        "required": ["is_internet_slang"],
                    }
                },
                stream=False,
            )
            return json.loads(response["choices"][0]["message"]["content"])["is_internet_slang"]

        elif self.provider == 'groq' and isinstance(self.model, Groq):
            response = self.model.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a slang detector. You will be given a word and your job is to give a JSON output.\n"
                        f" The JSON object must use the schema: {json.dumps(Slang.model_json_schema(), indent=2)}",
                    },
                    {
                        "role": "user",
                        "content": f"Is this word {word} slang or not?",
                    },
                ],
                model="llama3-8b-8192",
                temperature=0,
                stream=False,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)["properties"]["is_internet_slang"]
        else:
            raise ValueError(f"Model undefined : {type(self.model)}")

    def word_meaning(self, word: str):
        prompt = "You are a professional in language and culture. Define the given word in context of a person in a single line only. The word could be of pop culture origin or internet slang."
        if self.provider == 'llama_cpp' and isinstance(self.model, llama_cpp.Llama):
            response = self.model(
                prompt=prompt + "Here is the word: " + word,
                max_tokens=100,
                stream=False,
            )
            return response["choices"][0]["text"]
        if self.provider == 'groq' and isinstance(self.model, Groq):
            response = self.model.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": "I have a word and you must give me its meaning. Here is the word: " + word
                    }
                ],
                model="llama3-8b-8192",
                stream=False,
                max_tokens=120
            )
            return response.choices[0].message.content

    def give_context(self, base_word: str, x_positive: str, x_negative: str, y_positive: str, y_negative: str):
        if isinstance(self.model, llama_cpp.Llama): 

            response = self.model.create_chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": f"""Provide very short context for the word {base_word}
                        different aspects of the word lie on the cartesian axis
                        where {x_positive} and {x_negative} are on the x-axis and {y_positive} and {y_negative} are on the y-axis."""
                    }
                ],
                response_format={
                    "type": "string",
                },
            )
            return response
        if isinstance(self.model, Groq):
            response = self.model.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional in language and culture. 
                        You will be provided with a word which will be related to a topic, individual, internet culture or slang, and you must define 4 different aspects of the word, such that you can put it on a cartesian plane. 
                        The x-axis and y-axis must be defined in the context of the word.
                        The x-axis must have two aspects, one positive and one negative, and the same for the y-axis.
                        The positive and negative aspects must be opposites of each other.
                        """,
                    },
                    {
                        "role": "user",
                        "content": f"""Provide very short context for the word {base_word}
                        different aspects of the word lie on the cartesian axis
                        where {x_positive} and {x_negative} are on the x-axis and {y_positive} and {y_negative} are on the y-axis."""

                    }
                ],
                model="llama3-8b-8192",
                stream=False
            )
            return response

      

    def create_words(self, word: str):

        prompt = f"""You are given the word {word}. You must define the aspects of the word that can be put on a cartesian plane. Return the output in JSON format.
                         """
        messages = [
                    {
                        "role": "system",
                        "content": """You are a professional in internet culture. You will be provided with a word which will be related to an individual, internet culture or twitter slang. You must define 2 words which are aspects of the given word that can be put on the x and y axis of a cartesian plane. Both x and y aspect words must have a positive and negative factor words called x_positive and x_negative, y_positive and y_negative. 2 factors words will be on the x-axis and the other 2 factors words will be on the y-axis. For example if the given word is "cracked", it will have the aspect x as chadness, and y as skill level. The factor words "gigachad" and "simp" will belong to the x-axis, and "gamer" and "noob" on the y-axis. You must provide answer in JSON format."""
                        f"The JSON object must use the schema: {json.dumps(Word.model_json_schema(), indent=1)}",
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
        response_format={"type": "json_object"}
        if isinstance(self.model, llama_cpp.Llama):
            response = self.model.create_chat_completion(
                messages = messages,
                response_format=response_format,
                stream=False,
            )
            
            return json.loads(response["choices"][0]["message"]["content"])['properties']
        elif isinstance(self.model, Groq):
            response = self.model.chat.completions.create(
                messages = messages,
                model="llama3-8b-8192",
                temperature=0.2,
                stream=False,
                response_format=response_format,
            )
            return json.loads(response.choices[0].message.content)['properties']
        else:
            raise ValueError(f"Model undefined : {type(self.model)}")
            

    @staticmethod
    def normalize_value(value, old_min, old_max, new_min, new_max):
        """Normalize a value from one range to another."""
        old_range = old_max - old_min
        new_range = new_max - new_min
        return (((value - old_min) * new_range) / old_range) + new_min

    def give_rating(self, text: str, word: str, x_aspect: str, x_positive: str, x_negative: str, y_aspect: str, y_positive: str, y_negative: str) -> List[int]:
        """
        Give a rating for the compiled tweets based on provided aspects and their positive and negative directions.
        """
        min_value = -10
        max_value = 10
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        if not isinstance(word, str) or not isinstance(x_aspect, str) or not isinstance(x_positive, str) or not isinstance(x_negative, str) or not isinstance(y_aspect, str) or not isinstance(y_positive, str) or not isinstance(y_negative, str):
            raise ValueError("word, x_aspect, x_positive, x_negative, y_aspect, y_positive, and y_negative must be strings")

        prompt = f"""You are a social media analyst. You are provided with a compiled list of tweets from a user and a cartesian plane and where each axis corresponds to an aspect of the main factor {word}.
        The X aspect is "{x_aspect}" and the positive X axis is the factor {x_positive}, and the negative X axis is the factor {x_negative}
        The Y aspect is "{y_aspect}" and the positive Y axis is the factor {y_positive}, and the negative Y axis is the factor {y_negative}.
        Your job is to provide a coordinate for the combined tweets on the cartesian plane based on the factors provided.
        Be creative with your ratings and be genuine. Provide the rating in JSON format.
        Here are the tweets:
        """
        system = {
                    "role": "system",
                    "content": """You are a social media analyst. You are provided with a compiled list of tweets from a user and a cartesian plane on which the tweets are to be ranked based on some defined factors.
                    Each axis corresponds to an aspect of the tweet, and has two types of factors, positive and negative.
                    Hence there is the x-axis with the factors x_positive and x_negative and the y-axis with the factors y_positive and y_negative.
                    Your job is to provide a rating of the collected tweets, which will be a coordinate for the combined tweets on the cartesian plane.
                    You will do this by evaluating the tweets and providing a rating for the bunch of tweets based on the factors provided.
                    If a tweet is more positive towards the x_positive factor, you will rate it higher on the x-axis, and if it is more negative towards the x_negative factor, you will rate it lower on the x-axis.
                    The X score is called x_value and the Y score is called y_value.
                    The same goes for the y-axis.
                    Each tweet is separated by a new line.
                    The range for the X and Y axis is from -10 to 10. Please provide a value for the text based on what you feel about the text.
                    Provide your answer in JSON format.
                    """
                    f"The JSON object must use the schema: {json.dumps(Rating.model_json_schema(), indent=2)}",
                }

        if isinstance(self.model, llama_cpp.Llama):
            max_chars = 12000
        else:
            max_chars = 20000
        chunks = self.chunk_text(text, max_chars=max_chars)

        x_values = []
        y_values = []

        for chunk in chunks:
            retry_count = 0
            chunk_processed = False
            while retry_count < 2:  # Try up to 2 times (initial attempt + 1 retry)
                try:
                    if isinstance(self.model, llama_cpp.Llama):
                        response = self.model.create_chat_completion(
                            messages=[
                                system,
                                {
                                    "role": "user",
                                    "content": prompt + chunk
                                },
                            ],
                            response_format={
                                "type": "json_object"
                            },
                            stream=False,
                        )
                        values_str = response["choices"][0]["message"]["content"]
                    elif isinstance(self.model, Groq):
                        response = self.model.chat.completions.create(
                            messages=[
                                system,
                                {
                                    "role": "user",
                                    "content": prompt + chunk
                                },
                            ],
                            model="llama3-8b-8192",
                            max_tokens=8000,
                            temperature=0.2,
                            stream=False,
                            response_format={
                                "type": "json_object",
                            },
                        )
                        values_str = response.choices[0].message.content
                    
                    values = json.loads(values_str)
                    if not isinstance(values, dict) or 'x_value' not in values or 'y_value' not in values:
                        raise ValueError("Invalid response format from model")
                    
                    x_value = values["x_value"]
                    y_value = values["y_value"]
                    if not (min_value <= x_value <= max_value) or not (min_value <= y_value <= max_value):
                        raise ValueError(f"x_value and y_value must be within the range of {min_value} to {max_value}")
                    
                    x_values.append(x_value)
                    y_values.append(y_value)
                    chunk_processed = True
                    break  # Successfully processed the chunk, exit the retry loop
                
                except json.JSONDecodeError:
                    print(f"Error decoding JSON for chunk. Attempt {retry_count + 1}")
                    retry_count += 1
                except Exception as e:
                    print(f"Error processing model response: {e}")
                    retry_count += 1

            if not chunk_processed:
                print(f"Failed to process chunk after retry. Appending 0 for this chunk.")
                x_values.append(0)
                y_values.append(0)

        if not x_values or not y_values:
            raise ValueError("No ratings could be obtained from any chunk")

        x_sum = sum(x_values)
        y_sum = sum(y_values)

        x_normalized = self.normalize_value(x_sum, min(x_sum, min_value), max(x_sum, max_value), min_value, max_value)
        y_normalized = self.normalize_value(y_sum, min(y_sum, -5), max(y_sum, max_value), min_value, max_value)

        return [round(x_normalized), round(y_normalized)]
