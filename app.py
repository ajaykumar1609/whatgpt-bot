from flask import Flask, request
import openai
from twilio.twiml.messaging_response import MessagingResponse
import os
import mysql.connector

# Init the Flask App
app = Flask(__name__)

# Initialize the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the MySQL database connection details
MYSQLHOST = os.getenv("MYSQLHOST")
MYSQLPORT = os.getenv("MYSQLPORT")
MYSQLUSER = os.getenv("MYSQLUSER")
MYSQLPASSWORD = os.getenv("MYSQLPASSWORD")
MYSQLDATABASE = os.getenv("MYSQLDATABASE")

# Define a function to connect to the MySQL database
def connect_db():
    try:
        connection = mysql.connector.connect(
            host=MYSQLHOST,
            port=MYSQLPORT,
            user=MYSQLUSER,
            password=MYSQLPASSWORD,
            database=MYSQLDATABASE
        )
        return connection
    except Exception as e:
        print("Error connecting to the database:", e)

# Define function togenerate response using GPT-3
def generate_response(prompt, history=""):
    """
    Generates a response to the user's input using GPT-3 and the conversation history.
    """
    # Concatenate prompt and history
    prompt = f"{prompt.strip()} {history.strip()}"
    print(prompt)

    # Generate response using GPT-3
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5
    )

    # Extract response text from API result
    response_text = response.choices[0].text.strip()
    return response_text

# Define a route to handle incoming requests
@app.route('/whatgpt', methods=['POST'])
def whatgpt():
    print("Bot is running")
    incoming_que = request.values.get('Body', '').lower()
    print("Question: ", incoming_que)

    # Connect to the MySQL database
    connection = connect_db()

    # Get the conversation history from the database
    cursor = connection.cursor()
    cursor.execute("SELECT input_text, response_text FROM conversation_history ORDER BY id DESC LIMIT 1")
    result =cursor.fetchone()
    if result is None:
        history = ""
    else:
        history = f"Q: {result[0]}\nA: {result[1]}\n"

    # Generate the response using GPT-3
    answer = generate_response(incoming_que, history)

    # Store the conversation history in the database
    cursor.execute("INSERT INTO conversation_history (input_text, response_text, history) VALUES (%s, %s, %s)",
                   (incoming_que, answer, history))
    connection.commit()

    # Close the database connection
    cursor.close()
    connection.close()

    print("Bot Answer: ", answer)

    # Send the response to Twilio
    bot_resp = MessagingResponse()
    msg = bot_resp.message()
    msg.body(answer)
    return str(bot_resp)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)