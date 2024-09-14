import gradio as gr
from openai import OpenAI
from transformers import pipeline
import os


def local_generate_completion(prompt, max_tokens, temperature, repetition_penalty):
    prompt = prompt.strip()
    try:
        completion = pipeline("text2text-generation", model="google/flan-t5-small")
        res = completion(
            prompt, 
            max_length=max_tokens,
            temperature=temperature,
            repetition_penalty=repetition_penalty
        )
        generated_text = res[0]['generated_text']
        return generated_text
    except Exception as e:
        return f"An error occurred: {str(e)}"

def generate_completion(prompt, temperature, repetition_penalty, stop_phrase, max_tokens):
    prompt = prompt.strip()
    try:
        api_key = os.environ.get('HYPERBOLIC_API_KEY')
        client = OpenAI(
            base_url="https://api.hyperbolic.xyz/v1",
            api_key=api_key,
        )
        completion = client.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B",
            prompt=prompt,
            temperature=temperature,
            frequency_penalty=repetition_penalty,
            max_tokens=max_tokens,
            stop=[stop_phrase] if stop_phrase else None
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

def append_completion(prompt, completion):
    prompt, completion = prompt.strip(), completion.strip()
    return f"{prompt}{' '}{completion}".strip(), ""  # Return new prompt and empty completion

def clear_fields():
    return "", ""

with gr.Blocks(theme=gr.themes.Soft(), css="#stop-button {background-color: red; color: white;}") as iface:

    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(label="Prompt", value="The best thing about being a cat is", lines=10)
        with gr.Column():
            output_text = gr.Textbox(label="Generated Completion", lines=10)

    with gr.Accordion("Additional Features", open=False):    
        with gr.Row():
            with gr.Column():
                gr.Markdown("### API Model Parameters")
                temperature_slider_api = gr.Slider(minimum=0, maximum=1, value=0.7, step=0.1, label="Temperature")
                repetition_penalty_slider_api = gr.Slider(minimum=0, maximum=2, value=0.1, step=0.1, label="Repetition Penalty")
                max_tokens_slider_api = gr.Slider(minimum=1, maximum=4000, value=250, step=1, label="Max Tokens")
                stop_phrase_input_api = gr.Textbox(label="Stop Phrase", placeholder="Enter stop phrase (optional)")
            with gr.Column():
                gr.Markdown("### Local Model Parameters")
                temperature_slider_local = gr.Slider(minimum=0, maximum=1, value=0.7, step=0.1, label="Temperature")
                repetition_penalty_slider_local = gr.Slider(minimum=0, maximum=2, value=0.1, step=0.1, label="Repetition Penalty")
                max_tokens_slider_local = gr.Slider(minimum=1, maximum=4000, value=250, step=1, label="Max Tokens")
        
    with gr.Row():
        generate_button = gr.Button("API Model Text Generation")
        local_generate_button = gr.Button("Local Model Text Generation")
        append_button = gr.Button("Append Completion to Prompt")
        clear_button = gr.Button("Clear All Fields")

    with gr.Row():
        stop_button = gr.Button("Stop Generation", elem_id="stop-button")
    
    API_generation_event = generate_button.click(
        generate_completion,
        inputs=[prompt_input, temperature_slider_api, repetition_penalty_slider_api, stop_phrase_input_api, max_tokens_slider_api],
        outputs=output_text
    )

    local_generation_event = local_generate_button.click(
        local_generate_completion,
        inputs=[prompt_input, max_tokens_slider_local, temperature_slider_local, repetition_penalty_slider_local],
        outputs=output_text
    )
    
    append_button.click(
        append_completion,
        inputs=[prompt_input, output_text],
        outputs=[prompt_input, output_text]
    )
    
    clear_button.click(
        clear_fields,
        outputs=[prompt_input, output_text]
    )

    stop_button.click(None, None, None, cancels=[API_generation_event, local_generation_event])
    
iface.launch(share=False)
