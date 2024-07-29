import llama_cpp
import json
import llama_cpp.llama_tokenizer

def load_model(provider:str):
    model_options = {
        "llama_cpp" : llama_cpp.Llama.from_pretrained(
            repo_id="bartowski/Llama-3-Instruct-8B-SPPO-Iter3-GGUF",
            filename="Llama-3-Instruct-8B-SPPO-Iter3-Q4_K_M.gguf",
            tokenizer = llama_cpp.llama_tokenizer.LlamaHFTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct"),
            n_ctx = 4096,
            n_gpu_layers = -1,
            verbose= False,
            temperature=0.2
        ), 
        "groq": None, 
        "gpt4o":None,
    }
    model = model_options.get(provider, model_exception)
    return model

def model_exception():
    print("Wrong model")
    raise ValueError("Invalid choice of model! Model does not appear in model list.")



def chunk_text(text, max_chars=12000, overlap=100):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_chars and current_chunk:
            # Join the current chunk and add it to the list of chunks
            chunks.append(' '.join(current_chunk))
            # Keep the overlap
            overlap_words = current_chunk[-overlap:]
            current_chunk = overlap_words
            current_length = sum(len(w) + 1 for w in overlap_words) - 1

        current_chunk.append(word)
        current_length += len(word) + 1  # +1 for the space

    # Add the last chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def is_slang(model:llama_cpp.Llama, word:str)->bool:
            

            response = model.create_chat_completion(
            messages=[
                        {
                        "role": "user",
                        "content": f"""Here is a {word}. Provide if it is an internet slang or not."""
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
            stream= False,
            )
            
            return json.loads(response["choices"][0]["message"]["content"])["is_internet_slang"]

def word_meaning(model:llama_cpp.Llama, word:str):
            
            
            response = model(
                    prompt=f"Define the word {word} in context of a person, possibly in terms of internet slang.",
                    max_tokens=100,
                    stream=False,
                    )
            return response["choices"][0]["text"]

def give_context(model:llama_cpp.Llama, base_word:str, x_positive:str, x_negative:str, y_positive:str, y_negative:str):

            response = model.create_chat_completion(
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
            


def create_words(model:llama_cpp.Llama, word:str, is_slang:bool = False):


            if(is_slang):
                prompt = f"""Define 4 words to represent the word {word} on a cartesian compass, where each word will lie on the axis depending on a meaning.
                                    the given word  must be taken in context of internet slangs. the chosen words must be something you can describe a person against.
                                    be as creative as possible and use meme culture and internet slang to define the words.
                                    also define the meaning of the x and y axis. x and y axis should cover different aspects of the given word. 
                                    x and y axis must capture different aspects of the given word.
                                    positive x and negative x must be opposites, and the same for positive y and negative y.
                             """
            else:
                prompt = f"""Define 4 words to represent the word {word} on a cartesian compass, where each word will lie on the axis depending on a meaning.
                                    the chosen words must be something you can describe a person against.
                                    also define the meaning of the x and y axis. x and y axis should cover different aspects of the given word. 
                                    x and y axis must capture different aspects of the given word.
                                    positive x and negative x must be opposites, and the same for positive y and negative y.
                             """
            
            response = model.create_chat_completion(
            messages=[
                        {
                        "role": "user",
                        "content": prompt
                        }
            ],
            response_format={
                        "type": "json_object",
                        "schema": {
                        "type": "object",
                        "properties": {
                        "positive_x": {"type": "string"},
                        "negative_x": {"type": "string"},
                        "x_meaning": {"type": "string"},
                        "positive_y": {"type": "string"},
                        "negative_y": {"type": "string"},
                        "y_meaning": {"type": "string"},
                        },
                        "required": ["positive_x", "negative_x", "positive_y", "negative_y", "x_meaning", "y_meaning"],
                        }
            },
            stream= False,
            )
            return json.loads(response["choices"][0]["message"]["content"])


def normalize_value(value, old_min, old_max, new_min, new_max):
    """Normalize a value from one range to another."""
    old_range = old_max - old_min
    new_range = new_max - new_min
    return (((value - old_min) * new_range) / old_range) + new_min

def give_rating(text: str, model: llama_cpp.Llama, word: str, x_aspect: str, x_positive: str, x_negative: str, y_aspect: str, y_positive: str, y_negative: str) -> list:
    prompt = f"""You are provided with a compiled list of tweets from a user and a cartesian plane and where each axis corresponds to an aspect of the word {word}.
    The X aspect is "{x_aspect}" and the positive X axis is {x_positive}, and the negative X axis is {x_negative}
    The Y aspect is "{y_aspect}" and the positive X axis is {y_positive}, and the negative X axis is {y_negative}.
    Your job is to provide a coordinate for the combined tweets on the cartesian plane.
    Each tweet is separated by a new line.
    The range for the X and Y axis is from -5 to 5. Please provide a value for the text based on what you feel about the text.
    Strictly stay within the range of -5 to 5. Do not go over.
    If X is positive, it means the text is more {x_positive} and if X is negative, it means the text is more {x_negative}.
    If Y is positive, it means the text is more {y_positive} and if Y is negative, it means the text is more {y_negative}.
    Be creative with your ratings and be genuine.
    Here are the tweets:
    """
    chunks = chunk_text(text)
    
    x_values = []
    y_values = []

    for chunk in chunks:
        response = model.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt + chunk
                },
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "x_value": {"type": "integer"},
                        "y_value": {"type": "integer"}
                    },
                    "required": ["x_value", "y_value"],
                }
            },
            stream=False,
        )
        values_str = response["choices"][0]["message"]["content"]
        values = json.loads(values_str)
        x_values.append(values["x_value"])
        y_values.append(values["y_value"])

    # Calculate the sum of x and y values
    x_sum = sum(x_values)
    y_sum = sum(y_values)

    # Normalize the sums to be between -10 and 10
    x_normalized = normalize_value(x_sum, min(x_sum, -5), max(x_sum, 5), -5, 5)
    y_normalized = normalize_value(y_sum, min(y_sum, -5), max(y_sum, 5), -5, 5)

    return [round(x_normalized), round(y_normalized)]
