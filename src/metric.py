import llama_cpp
import json
import llama_cpp.llama_tokenizer

def load_model():
    model = llama_cpp.Llama.from_pretrained(
        repo_id="bartowski/Llama-3-Instruct-8B-SPPO-Iter3-GGUF",
        filename="Llama-3-Instruct-8B-SPPO-Iter3-Q4_K_M.gguf",
        tokenizer = llama_cpp.llama_tokenizer.LlamaHFTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct"),
        n_gpu_layers = -1,
        verbose= False,
    )
    return model

def is_slang(model:llama_cpp.Llama, word:str):

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
            
            return response["choices"][0]["message"]["content"]

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
                                    be as creative as possible and use meme culture and internet slang to define the words.
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
            return response["choices"][0]["message"]["content"]

model = load_model()
word = "vibe"
#word_info = get_word_info(word)
#word_info = is_slang(word)
#word_info = word_meaning(word)
words = create_words(model, word, is_slang = True)
response = json.loads(words)
context = give_context(model, word, response["positive_x"], response["negative_x"], response["positive_y"], response["negative_y"])
print(context["choices"][0]["message"]["content"])
