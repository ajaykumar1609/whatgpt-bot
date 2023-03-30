import os
import openai
import mysql.connector
from flask import Flask, request, jsonify

# Connect to MySQL database
mysql_host = os.getenv("MYSQLHOST")
mysql_user = os.getenv("MYSQLUSER")
mysql_password = os.getenv("MYSQLPASSWORD")
mysql_database = os.getenv("MYSQLDATABASE")
mysql_port = os.getenv("MYSQLPORT")

try:
    connection = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database,
        port=mysql_port,
    )
    cursor = connection.cursor()
    print("MySQL Connection Established!")
except mysql.connector.Error as error:
    print("Error while connecting to MySQL", error)


# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)


# Create a new conversation history
def create_new_history(input_text, response_text):
    cursor.execute("INSERT INTO conversation_history2 (input_text, response_text, history) VALUES (%s, %s, %s)", (input_text, response_text, ""))
    connection.commit()
    return cursor.lastrowid


# Append to existing conversation history
def append_to_history(conversation_id, response_text):
    cursor.execute("SELECT history FROM conversation_history2 WHERE id=%s", (conversation_id,))
    history = cursor.fetchone()[0]
    history += response_text + "\n"
    cursor.execute("UPDATE conversation_history2 SET response_text=%s, history=%s WHERE id=%s", (response_text, history, conversation_id))
    connection.commit()


# Generate a response from OpenAI API
def generate_response(prompt):
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()


# Define a route to receive messages from the user
@app.route("/whatgpt", methods=["POST"])
def whatgpt():
    message = request.form["message"]
    print(message)

    # Retrieve the conversation history
    cursor.execute("SELECT id, input_text, response_text FROM conversation_history2 ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    # If no conversation history exists, create a new one
    if not row:
        conversation_id = create_new_history(message, "")
        response = generate_response(message)
        append_to_history(conversation_id, response)
        return jsonify(response)

    # If a conversation history exists, retrieve it
    conversation_id, input_text, response_text = row

    # If the most recent message was from the user, generate a response
    if response_text == "":
        response = generate_response(input_text + "\n" + message)
        append_to_history(conversation_id, response)
        return jsonify(response)

    # If the most recent message was from the bot, return the next message in the history
    else:
        append_to_history(conversation_id, "")
        return jsonify(response_text)


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
