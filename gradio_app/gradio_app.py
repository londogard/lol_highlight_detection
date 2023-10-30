import gradio
import gradio as gr

def greet(name: str):
    return "Hello " + name + "!"

with gradio.Blocks() as demo:
    a = gr.Dropdown(["Lol", "Hey!"])
    out = gr.Textbox()
    a.change(lambda x: x, inputs=a, outputs=out)


demo.launch(share=True)
