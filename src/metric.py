import llama_cpp
import llama_cpp.llama_tokenizer


def create_words(word:str):
            model = llama_cpp.Llama.from_pretrained(
            repo_id="bartowski/Llama-3-Instruct-8B-SPPO-Iter3-GGUF",
            filename="Llama-3-Instruct-8B-SPPO-Iter3-Q4_K_M.gguf",
            tokenizer = llama_cpp.llama_tokenizer.LlamaHFTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct"),
            n_gpu_layers = -1,
            verbose= False,
            )
            
            response = model.create_chat_completion(
            messages=[
                        {
                        "role": "user",
                        "content": f"""Define 4 words to represent the word {word} on a cartersian compass, where each word will lie on the axis depending on a meaning.
                                    the given word  must be taken in context of internet slangs. the chosen words must be something you can describe a person against.
                                    be as creative as possible and use meme culture and internet slang to define the words.
                                    also define the meaning of the x and y axis. x and y axis should cover different aspects of the given word. 
                                    x and y axis must capture different aspects of the given word.
                                    positive x and negative x must be opposites, and the same for positive y and negative y.
                                    """
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


word = "simp"
response = create_words(word)
print(response)
