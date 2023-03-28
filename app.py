from flask import Flask, request
import openai
from twilio.twiml.messaging_response import MessagingResponse
import os

# Init the Flask App
app = Flask(__name__)

# Initialize the OpenAI API key

openai.api_key = "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"

def generate_answer(question):
    model_engine = "davinci"
    prompt = (f"Q: {question}\n"
              "A:")

    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    answer = response.choices[0].text.strip()
    for i in range(len(answer)):
        if answer[i]=="Q":
            if answer[i+1]==":":
                return answer[:i]

    return answer


# Call OpenAI API to generate response
def generate_response(question):
    prompt = question.strip()
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Extract response text from API result
    response_text = response.choices[0].text.strip()
    return response_text


# Define a route to handle incoming requests
@app.route('/whatgpt', methods=['POST'])
def whatgpt():
    print("bot is running")
    incoming_que = request.values.get('Body', '').lower()
    print("Question: ", incoming_que)
    # Generate the answer using GPT-3
    answer = generate_answer(incoming_que)
    print("BOT Answer: ", answer)
    bot_resp = MessagingResponse()
    msg = bot_resp.message()
    msg.body(answer)
    return str(bot_resp)


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
