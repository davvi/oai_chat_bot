import openai


def chat_request(oai_token, model, context):
    openai.api_key = oai_token

    response = openai.Completion.create(
        engine=model,
        prompt=context,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

