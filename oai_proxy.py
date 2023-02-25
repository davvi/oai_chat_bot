import openai
import logging


def chat_request(oai_token, model, context):
    openai.api_key = oai_token

    logging.debug('Chat request: model - %s; context - %s', model, context)

    response = openai.Completion.create(
        engine=model,
        prompt=context,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

