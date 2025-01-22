from openai import OpenAI

api_key = "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"

OPENAI_CLIENT = OpenAI(api_key=api_key)

response_iter = OPENAI_CLIENT.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say something interesting"}],
    stream=True,
    temperature=0.4,
)

for chunk in response_iter:
    print("CHUNK:", chunk)
