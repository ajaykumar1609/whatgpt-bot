from flask import Flask, request
import openai

import mysql.connector

from twilio.twiml.messaging_response import MessagingResponse
import os


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



# Define a function to retrieve the last 3 questions and their corresponding answers from the database
def get_last_3_questions_answers(user_id):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Retrieve the last 3 questions and their corresponding answers from the table
        cursor.execute("SELECT question, answer FROM user_conversation WHERE user_id = %s ORDER BY id DESC LIMIT 10", (user_id,))
        results = cursor.fetchall()

        connection.close()

        return results
    except Exception as e:
        print("Error retrieving last 3 questions and answers:", e)


# Define a function to add a question and its corresponding answer to the database
def add_question_answer(user_id,question, answer):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Insert the question and answer into the table
        cursor.execute("INSERT INTO user_conversation (user_id, question, answer) VALUES (%s, %s, %s)", (user_id, question, answer))
        # val = (question, answer)
        # cursor.execute(sql, val)

        # Commit the changes
        connection.commit()

        connection.close()

        print("Question and answer added successfully!")
    except Exception as e:
        print("Error adding question and answer:", e)


def delete_history(user_id):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Insert the question and answer into the table
        cursor.execute("DELETE FROM user_conversation WHERE user_id = %s", (user_id,))
        # val = (question, answer)
        # cursor.execute(sql, val)

        # Commit the changes
        connection.commit()

        connection.close()

        print("deleted history successfully!")
    except Exception as e:
        print("Error deleting:", e)


# Define function togenerate response using GPT-3
def generate_response(prompt, user_id):
    rows = get_last_3_questions_answers(user_id)
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for row in reversed(rows):
        question = row[0]
        answer = row[1]
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
    messages.append(prompt)
    print(messages)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )
    return response['choices'][0]['message']['content']

# Define a route to handle incoming requests
@app.route('/whatgpt', methods=['POST'])
def whatgpt():
    print("Bot is running")
    incoming_que = request.values.get('Body', '').lower()
    
    print("Question: ", incoming_que)
    user_id = request.values.get('From')
    print('User ID:', user_id)
    if incoming_que == "new topic":
        delete_history(user_id)
        # Send the response to Twilio
        bot_resp = MessagingResponse()
        msg = bot_resp.message()
        msg.body("Yeah now you can start a new topic")
        return str(bot_resp)
    m = {"role": "user", "content": incoming_que}
    answer = generate_response(m,user_id)
    # for i in range(len(answer)):
    #     if answer[i]=="Q":
    #         if answer[i+1]==":":
    #             answer = answer[:i-1]
    #             break
    add_question_answer(user_id,incoming_que,answer)
    print("Bot Answer: ", answer)
    # Send the response to Twilio
    bot_resp = MessagingResponse()
    msg = bot_resp.message()
    msg.body(answer)
    return str(bot_resp)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)

