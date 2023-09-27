import openai
import json

def convert_message_to_openai_format(system_prompt : str, messages : list[tuple[str, str]]):
    res = [{"role":"system", "content": system_prompt}]
    for (user_msg, bot_msg) in messages:
        res.append({"role": "user", "content": user_msg})
        if bot_msg is not None:
            res.append({"role": "assistant", "content": bot_msg})
    return res

def instruct(system_prompt : str, messages : list[tuple[str, str]]) -> str:
    """
    General purpose LLM/AI invocation. Use llama v2 13b chat as an instruct model by wrapping it up
    in a single turn conversation.
    """
    response = openai.ChatCompletion.create(
        model="accounts/fireworks/models/llama-v2-13b-chat-w8a16",
        messages=convert_message_to_openai_format(system_prompt, messages),
        temperature=0.7,
        max_tokens=2048
    )
    return response.choices[0].message.content

def attempt_extraction(instruct_prompt : str, prefix : str, parse : bool):
    """
    Attempt to turn natural language text into structured format. We use this flow/pattern:
    1. Use a coding focused LLM which work better on this kind of task. (guess only)
    2. Use guidance like technique (called "nudge") - prim AI into a JSON only output
       by writing the beginning part of the answer for it.
    3. Due to limitation of specific API provider, use streaming mode and detect stop token
       ourself. Here the JSON is enclosed in markdown codeblock so we stop at ```.
    4. Then backfill the nudge tokens and attempt a parse.
    """
    response = openai.Completion.create(
        model="accounts/fireworks/models/llama-v2-34b-code-instruct-w8a16",
        prompt=instruct_prompt,
        temperature=0.1,
        max_tokens=1280,
        stream=True
    )
    ans = ""
    for chunk in response:
        txt = chunk.choices[0].get("text", "")
        if txt is not None:
            ans += txt
            if "```" in ans:
                break
    ans = prefix + ans
    if "```" in ans:
        loc = ans.index("```")
        ans = ans[:loc]
    if parse:
        return json.loads(ans)
    else:
        return ans

