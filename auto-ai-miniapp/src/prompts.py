from llm import instruct, attempt_extraction
import json

prompts = {
    "chat": {},
    "coding": {}
}

prompts["chat"]["system"] = """You are an AI system designer. You are tasked to design a lightweight LLM (Large Language Model) based app.

- A roleplaying prompt is one that starts with something similar to "As a <role>, I understand that <description>. I will <task to perform>..."
- A chat based prompt is one that starts with something similar to "Welcome to <app name>. I am your <role>. <some intro to what the app does>..."
"""

prompts["chat"]["first-topic"] = """Design a roleplaying prompt to the LLM for a "{topic}" app. It should ask the user for some basic info to kickstart.
{remark}"""
prompts["chat"]["first-idea"] = """Generate one random idea for an AI app in the domain/area of "{area}". Then, Design a roleplaying prompt to the LLM for the app idea you proposed. It should ask the user for some basic info to kickstart.
{remark}"""

prompts["chat"]["second-ui"] = """The app will provide an UI for user to enter the info easily. Provide a list of inputs according to the prompt above. Each input should have a text description and a data type. The following datatype are supported:

- textfield
For textfield, it has two variant: short (for one line text input) and long (for potentially longer, multiple sentence input)
- options
For options, a list of the options available to user should be provided. It also has three variants: radio, dropdown-single, and dropdown-multiselect.

When applicable, please specify which variant is in effect.
"""

prompts["chat"]["third-examples"] = """Below is the JSON representation of the UI for the app:
```
{ui}
```
Generate up to 5 plausible example inputs a user may enter. Each example should include input for each fields in the UI. Leave a field empty if it is optional and user have no special info to provide.
Moreover, note that the app UI has a hardcoded optional "Additional notes" field. The example you generate may use that field to supply info that you think is necessary but not covered but any of the UI input above.
"""

prompts["chat"]["fourth-chain"] = """Here's some concept about LLM based AI app development:
Prompt-chaining is a simple way to achieve automation. We can think by analogy: LLM is a new form of computer where the basic unit of data is no longer bits but natural language text. A prompt is like a "natural language program". Due to current LLM limitation, we can apply similar notions of functions and problem decomposition in traditional programming. Each prompt represent a function that perform some primitive processing.
A prompt can accept input value through template variable in the prompt text. The output of a LLM call on the prompt with inputs substituted is also a natural language text/data that can be passed as input to other prompt.
Prompt-chaining for automation can be especially useful for tasks where a comprehensive response require addressing it from multiple angle/aspects, in such case we can think of each prompt as generating documents focusing on one specific aspect, and it is all of the documents combined that become the actual answer to the user query.

We will now try to do a simplified form of prompt chaining:
Propose a collection of at most 10 followup questions/requests that the user may ask of the AI after AI gave an initial answer (Notice it is user asking AI, not the other way around). Each followup question/request should correspond to a specific document addressing some aspect of the original user query. If you think there are legitimately more than 10 aspects, you may use a trick where thematically related questions are grouped as **subquestions** (which will then only count as one). However, be careful not to have too many subquestion in a followup question due to LLM cognitive bandwidth limit.

As an example, for an AI app that help user start a new physical shop, followup questions/requests may include:
- "Do a SWOT analysis on my shop idea for me."
- "What are the minimum number of staffs I need to hire to open the shop? Group your answer by role and specify number needed for each role. Also, for each role, please write a brief Job Ad for that role with responsibilities and job requirement/qualification."
- "What licenses or legal requirement do I need to meet to operate the shop in the region specified? What documents would I need to prepare? If I hire a secretary company to help, how much would that costs?"
(Showing just 3 examples, there could be more but we omitted them for brevity)

Now, please do your task similar to the example above, but on the AI app that is under design in the conversation above.
"""

prompts["coding"]["metainfo"] = """# Instruction
The input section below will show a text prompt for an AI enabled app.

Write a JSON encoding basic metainfo about the app. The JSON should have these fields:
- appName: Name of the app.
- description: Short description of what the app is/does.
- prompt: The text prompt for the app.

As the JSON will be parsed in python, remember to do the appropiate conversion for any multiline string: newline should be printed as '\\n' and the string become single line. The extra slash is for proper escaping.
# Input
{prompt}
# Output
Here is the requested JSON representing the metainfo:
```json
{{
"""

prompts["coding"]["ui"] = """# Instruction
The input section below will show a text prompt for an AI enabled app. Generate a UI for user to enter info easily according to the input the app asks of the user. The UI will be a simple form with a list of input fields.
Each input should have a text description and a data type. The following datatype are supported:
- textfield
For textfield, it has two variant: short (for one line text input) and long (for potentially longer, multiple sentence input)
- options
For options, a list of the options available to user should be provided. It also has two variants: dropdown-single, and dropdown-multiselect.

When applicable, please specify which variant is in effect.

Your answer should be a JSON object specifying the UI. Top level is a JSON list, each object has fields:
- desc: a string, text description of the input field
- datatype: type of UI input, a JSON object.
JSON object for datatype have fields:
- type: name of the datatype, one of: "textfield", "options".
- variant: string specifying which variant is used for datatype where it is applicable.
- options: (Applicable for "options" datatype) JSON list of string, one for each option.

Due to technical limitation, please make sure that the UI you design have at most 9 inputs, and that each option should contain at most 9 choices. You may consider focusing on the most important info/choices, or grouping similar inputs. For options, you may also consider providing more coarse grained/higher level concepts as choices. The UI will provide an additional "catch all" input anyway, so don't worry. (You do NOT need to specify this catch all input in your response)
# Input
{prompt}
# Output
Here is the JSON representing the UI:
```json
[{{
"""

prompts["coding"]["examples-nestedlist"] = """# Instruction
Convert the free form example data in the input section below into structured JSON format. The input section below will have two subsections: 1. A JSON representing the UI of an app, which is a form with some input fields. 2. A set of example data for the UI input.

Your output should be a (nested) JSON list, each item is in turn a JSON list that contain a field for each input field in the UI. The i-th item in that list is the example value for the i-th item in the UI form. There should be an additional last item in the list, for supplying additional contextual info of that example. Stuff an empty string if that is not needed for that example.

Example for reference:
```
[
    ["Ice cream", 123, true, ""],
    ["Potato chip", 23, false, "Special Order"],
    ["Testing", 0, true, "System test"],
    ["Pizza", 11, true, "Has discount"]
]
```

Note that the datatype of the value must match the datatype of the corresponding UI field. For instance, even if the example are numeric etc, if the UI field specify textfield, then it must be in JSON string type.
Text data must be preserved, that is, you should be faithful to the example provided. As an example, "$10, plan for 5% p.a. in next five year" **should be copied verbatim** instead of converting to "$10".
# Input
## UI form input fields
{ui}
## Examples data
{eg}
# Output
Sure, here is the examples in JSON format:
```
[
    ["""


prompts["coding"]["chains"] = """# Instruction

## Background info
Here's some concept about LLM (Large Language Model) based AI app development:
Prompt-chaining is a simple way to achieve automation. We can think by analogy: LLM is a new form of computer where the basic unit of data is no longer bits but natural language text. A prompt is like a "natural language program". Due to current LLM limitation, we can apply similar notions of functions and problem decomposition in traditional programming. Each prompt represent a function that perform some primitive processing.
A prompt can accept input value through template variable in the prompt text. The output of a LLM call on the prompt with inputs substituted is also a natural language text/data that can be passed as input to other prompt.
Prompt-chaining for automation can be especially useful for tasks where a comprehensive response require addressing it from multiple angle/aspects, in such case we can think of each prompt as generating documents focusing on one specific aspect, and it is all of the documents combined that become the actual answer to the user query.

## Your Task
We are developing a LLM based AI app, where it will deliver a comprehensive answer to user query, addressing various aspects/dimension in the topic/domain of that app according to user info. For each aspect, we will output a document answering that part.
The input section below will contain some suggested followup questions a user may ask of an AI. Each question roughly correspond to a output document/aspect. Notice that the suggested question may have employed a trick where multiple thematically related subquestions are grouped. In that case you may consider treating them as a single aspect/document/question or not at your discretion.

Your task is to convert it to a JSON representation. Your output should be a JSON list, each item in the list being a JSON object representing the aspect/document/followup.
That JSON object should have these fields:
- category: the category/group that this question belongs to. Should be in snake case.
- name: a brief descriptive name for the document/aspect being addressed. Should be in snake case. No file extension is included. Should be unique.
- question: Text prompt for the followup question the user ask of the AI to trigger generating the document.

# Input
{followup}
# Output
Yes, here is the JSON representation of the aspects/dimension/followup questions:
```
[{{
"""

def remark_string(app_remark):
    if app_remark == "":
        return ""
    else:
        return "In addition, user made this remark in relation to the request above: " + app_remark

def gen_app_begin(has_idea, app_domain, app_topic, app_remark):
    if has_idea:
        return instruct(prompts["chat"]["system"], [(prompts["chat"]["first-topic"].format(topic=app_topic, remark=remark_string(app_remark)), None)])
    else:
        return instruct(prompts["chat"]["system"], [(prompts["chat"]["first-idea"].format(area=app_domain, remark=remark_string(app_remark)), None)])

def gen_app_extract_meta(app_prompt):
    data = attempt_extraction(prompts["coding"]["metainfo"].format(prompt=app_prompt), "{", False)
    map_meta = {}
    try:
      map_meta = json.loads(data)
    except ValueError as err:
      print(err)
    res = { "meta": map_meta }
    #return data
    return [data, res, res]

def gen_app_extract_ui(app_prompt, app_def):
    data = attempt_extraction(prompts["coding"]["ui"].format(prompt=app_prompt), "[{", False)
    map_ui = []
    try:
      map_ui = json.loads(data)
    except ValueError as err:
      print(err)
    res = app_def
    res["ui"] = map_ui
    #return data
    return [data, res, res]

def gen_app_examples(has_idea, app_domain, app_topic, app_remark, app_prompt, debug_ui):
    if has_idea:
        first_p = prompts["chat"]["first-topic"].format(topic=app_topic, remark=remark_string(app_remark))
    else:
        first_p = prompts["chat"]["first-idea"].format(area=app_domain, remark=remark_string(app_remark))
    chat = [(first_p, app_prompt), (prompts["chat"]["third-examples"].format(ui=debug_ui), None)]
    return instruct(prompts["chat"]["system"], chat)
    #raise NotImplementedError()

def gen_app_extract_examples(debug_ui, example_input, app_def):
    data = attempt_extraction(prompts["coding"]["examples-nestedlist"].format(ui=debug_ui, eg=example_input), "[[", False)
    map_eg = []
    try:
        map_eg = json.loads(data)
    except ValueError as err:
        print(err)
    res = app_def
    res["eg"] = map_eg
    return [data, res, res]

def gen_app_prompt_chain(has_idea, app_domain, app_topic, app_remark, app_prompt):
    if has_idea:
        first_p = prompts["chat"]["first-topic"].format(topic=app_topic, remark=remark_string(app_remark))
    else:
        first_p = prompts["chat"]["first-idea"].format(area=app_domain, remark=remark_string(app_remark))
    chat = [(first_p, app_prompt), (prompts["chat"]["fourth-chain"], None)]
    return instruct(prompts["chat"]["system"], chat)

def gen_app_extract_chains(followup_question, app_def):
    data = attempt_extraction(prompts["coding"]["chains"].format(followup=followup_question), "[{", False)
    map_chain = []
    try:
        map_chain = json.loads(data)
    except ValueError as err:
        print(err)
    res = app_def
    res["chain"] = map_chain
    return [data, res, res]

