import gradio as gr

import logging
import time

from prompts import *


def flip_input_ui(has_idea):
    if has_idea:
        return [gr.update(visible=False), gr.update(visible=True)]
    else:
        return [gr.update(visible=True), gr.update(visible=False)]


#def add_textbox(t):
#    b = gr.Textbox(label="Hey")
#    t.add_child(b)
#    b.render()

def myecho(message, history):
    return message

def app_markdown_banner(app_def):
    meta = app_def["meta"]
    template = """# {Name}
{Description}
"""
    return template.format(Name=meta["appName"], Description=meta["description"])

def deploy_app(app_def, *args):
    res = []
    myinputs = []
    #res.append(gr.updaye(visible=True, examples=app_def["examples"], inputs=))
    #fields = app_def["fields"]
    fields = app_def["ui"]
    remain_count = 10 - len(fields) - 1
    for i, field in enumerate(fields):
        datatype = field["datatype"]
        if datatype["type"] == "textfield":
            if datatype["variant"] == "long":
                numLines = 7
            else:
                numLines = 1
            res.append(gr.update(visible=True, interactive=True, label=field["desc"], lines=numLines))
            res.append(gr.update(visible=False))
            res.append(gr.update(visible=False))
            myinputs.append(args[3*i])
        elif datatype["type"] == "options" and datatype["variant"] == "dropdown-single":
            res.append(gr.update(visible=False))
            res.append(gr.update(visible=True, interactive=True, label=field["desc"], choices=datatype["options"]))
            res.append(gr.update(visible=False))
            myinputs.append(args[3*i + 1])
        elif datatype["type"] == "options" and datatype["variant"] == "dropdown-multiselect":
            res.append(gr.update(visible=False))
            res.append(gr.update(visible=False))
            res.append(gr.update(visible=True, interactive=True, label=field["desc"], choices=datatype["options"]))
            myinputs.append(args[3*i + 2])
        else:
            raise ValueError("Unknown type: {t}, {v}".format(t=datatype["type"], v=datatype["variant"]))
    # Hardcoded extra field
    res.append(gr.update(visible=True, interactive=True, label="(Optional) Additional Notes:", lines=7))
    res.append(gr.update(visible=False))
    res.append(gr.update(visible=False))
    for i in range(remain_count):
        res.append(gr.update(visible=False))
        res.append(gr.update(visible=False))
        res.append(gr.update(visible=False))
    #res.prepend(gr.update(examples=app_def["examples"], inputs=myinputs))
    res.insert(0, app_markdown_banner(app_def))
    res.insert(1, app_def["eg"])
    return res

def retry_assembly(debug_meta, debug_ui, debug_eg):
    meta = {}
    ui = []
    eg = []
    try:
        meta = json.loads(debug_meta)
        ui = json.loads(debug_ui)
        eg = json.loads(debug_eg)
    except ValueError as err:
      print(err)
    res = { "meta": meta, "ui": ui, "eg": eg }
    return [res, res]

def user_submit_form(app_def, *args):
    res = "User had input the following info:"
    for i, field in enumerate(app_def["ui"]):
        value = ""
        datatype = field["datatype"]
        if datatype["type"] == "textfield":
            value = args[3*i]
        elif datatype["type"] == "options" and datatype["variant"] == "dropdown-single":
            value = args[3*i + 1]
        elif datatype["type"] == "options" and datatype["variant"] == "dropdown-multiselect":
            value = args[3*i + 2]
        else:
            raise ValueError("Unknown type: {t}, {v}".format(t=datatype["type"], v=datatype["variant"]))
        res += "\n {d} - {f}".format(f=str(value), d=field["desc"])
    return res

def run_app_first(app_def, app_user_input):
    system_prompt = app_def["meta"]["prompt"]
    return instruct(system_prompt, [(app_user_input, None)])

def run_selected_eg(evt : gr.SelectData):
    #return "Value: {v}, Index: {i}, other={o}".format(v=evt.value, i=evt.index, o=evt.selected)
    return evt.index[0]

def dynamic_fill_eg_input(app_def, selected_eg):
    res = []
    remain_count = 10 - len(app_def["ui"]) - 1
    data = app_def["eg"][selected_eg]
    for i, field in enumerate(app_def["ui"]):
        value = ""
        datatype = field["datatype"]
        if datatype["type"] == "textfield":
            res.append(data[i])
            res.append(gr.update())
            res.append(gr.update())
        elif datatype["type"] == "options" and datatype["variant"] == "dropdown-single":
            res.append(gr.update())
            res.append(data[i])
            res.append(gr.update())
        elif datatype["type"] == "options" and datatype["variant"] == "dropdown-multiselect":
            res.append(gr.update())
            res.append(gr.update())
            res.append(data[i])
        else:
            raise ValueError("Unknown type: {t}, {v}".format(t=datatype["type"], v=datatype["variant"]))
    res.append(data[-1])
    res.append(gr.update())
    res.append(gr.update())
    for i in range(remain_count):
        res.append(gr.update(visible=False))
        res.append(gr.update(visible=False))
        res.append(gr.update(visible=False))
    return res

standard_app_domains = ["Entertainment", "Education", "Designs", "Health", "Medicine", "Career", "Religion"]
banner = """# Hello
This is a test
"""

css = """#demoexamples thead { display: none }
"""

with gr.Blocks(css=css) as demo:
    with gr.Tab("App Design"):
        with gr.Row():
            with gr.Group():
                has_idea = gr.Checkbox(value=True, label="Have an app idea?")
                app_domain = gr.Dropdown(choices=standard_app_domains, label="App Area/Domain", visible=False)
                app_topic = gr.Textbox(label="App Topic")
            app_remark = gr.Textbox(label="Additional Remark/Request", lines=3)
            btn_gen_app = gr.Button(value="Generate App!", variant="primary")
        with gr.Row():
            with gr.Column():
                app_prompt = gr.TextArea(label="Prompt", interactive=True, show_label=True, show_copy_button=True)
                example_input = gr.TextArea(label="Examples", interactive=True, show_label=True, show_copy_button=True)
                followup_question = gr.TextArea(label="Followup Questions", interactive=True, show_label=True, show_copy_button=True)
                #btn_temp = gr.Button(label="Temp test")
            with gr.Column():
                with gr.Accordion("For Internal Debug"):
                    debug_meta = gr.Code(language="json", label="Basic metainfo", interactive=True)
                    debug_ui = gr.Code(language="json", label="Extracted UI", interactive=True)
                    debug_examples = gr.Code(language="json", label="Extracted Examples", interactive=True)
                    debug_chain = gr.Code(language="json", label="Prompt Chaining", interactive=True)
                    btn_assemble = gr.Button(value="Try Assembly")
                app_def_display = gr.JSON(label="App Definition")
                app_def = gr.State({})
                btn_deploy = gr.Button(value="Deploy and Test run", variant="primary")
    with gr.Tab("Test Run") as t2:
        app_banner = gr.Markdown(banner)
        with gr.Row():
            with gr.Column():
                with gr.Group():
                    dynamic_inputs = []
                    for i in range(10):
                        dyn_textbox = gr.Textbox(visible=False)
                        dyn_dropdown = gr.Dropdown(visible=False, allow_custom_value=True)
                        dyn_multiselect = gr.Dropdown(visible=False, multiselect=True)
                        dynamic_inputs.append(dyn_textbox)
                        dynamic_inputs.append(dyn_dropdown)
                        dynamic_inputs.append(dyn_multiselect)
                #eg = gr.Examples(examples=[], inputs=[])
                #eg = gr.Dataset(components=[gr.Textbox(), gr.Textbox(), gr.Textbox()], samples=[["Foo", "Bar", 12], ["Test", "Bye", "23"]], type="index", label="Examples")
                eg = gr.Dataframe(value=[["Foo", "bar", 12], ["Test", "bye", 23]], label="Examples", headers=None, elem_id="demoexamples")
                selected_eg = gr.State()
                btn_run_app = gr.Button(value="Run", variant="primary")
                #statement = gr.Textbox()
                #statement2 = gr.Textbox()
            with gr.Column():
                app_user_input = gr.State("")
                app_first_response = gr.TextArea(label="First Response", interactive=True, show_label=True, show_copy_button=True)
                gr.ChatInterface(fn=myecho, title="Testing")
    has_idea.input(flip_input_ui, inputs=[has_idea], outputs=[app_domain, app_topic])
    btn_gen_app.click(gen_app_begin, inputs=[has_idea, app_domain, app_topic, app_remark], outputs=[app_prompt]) \
        .success(gen_app_extract_meta, inputs=[app_prompt], outputs=[debug_meta, app_def, app_def_display]) \
        .success(gen_app_extract_ui, inputs=[app_prompt, app_def], outputs=[debug_ui, app_def, app_def_display]) \
        .success(gen_app_examples, inputs=[has_idea, app_domain, app_topic, app_remark, app_prompt, debug_ui], outputs=[example_input]) \
        .success(gen_app_extract_examples, inputs=[debug_ui, example_input, app_def], outputs=[debug_examples, app_def, app_def_display]) \
        .success(gen_app_prompt_chain, inputs=[has_idea, app_domain, app_topic, app_remark, app_prompt], outputs=[followup_question]) \
        .success(gen_app_extract_chains, inputs=[followup_question, app_def], outputs=[debug_chain, app_def, app_def_display])
    btn_assemble.click(retry_assembly, inputs=[debug_meta, debug_ui, debug_examples], outputs=[app_def, app_def_display])
    btn_deploy.click(deploy_app, inputs=[app_def] + dynamic_inputs, outputs=[app_banner, eg] + dynamic_inputs)
    btn_run_app.click(user_submit_form, inputs=[app_def] + dynamic_inputs, outputs=[app_user_input]) \
        .success(run_app_first, inputs=[app_def, app_user_input], outputs=[app_first_response])
    eg.select(fn=run_selected_eg, inputs=None, outputs=selected_eg) \
        .success(dynamic_fill_eg_input, inputs=[app_def, selected_eg], outputs=dynamic_inputs)
    #btn_temp.click(add_textbox, inputs=[t2], outputs=[])
    #t2.add_child(gr.Textbox())
    #with gr.Tab("Test Run"):
        #d
    #def gen_app_prompt_chain(has_idea, app_domain, app_topic, app_remark, app_prompt):
    #def gen_app_extract_chains(followup_question, app_def):

demo.queue().launch(debug=True)
