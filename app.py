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



# Define a function to retrieve the last 3 questions and their corresponding answers from the database
def get_last_3_questions_answers(user_id):
    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor()

        # Retrieve the last 3 questions and their corresponding answers from the table
        cursor.execute("SELECT question, answer FROM user_conversation WHERE phone_number = %s ORDER BY id DESC LIMIT 3", (user_id,))
        results = cursor.fetchall()

        # Close the database connection
        connection.close()

        return results
    except Exception as e:
        print("Error retrieving last 3 questions and answers:", e)


# Define a function to add a question and its corresponding answer to the database
def add_question_answer(user_id,question, answer):
    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor()

        # Insert the question and answer into the table
        cursor.execute("INSERT INTO user_conversation (phone_number, question, answer) VALUES (%s, %s, %s)", (user_id, question, answer))
        # val = (question, answer)
        # cursor.execute(sql, val)

        # Commit the changes
        connection.commit()

        # Close the database connection
        connection.close()

        print("Question and answer added successfully!")
    except Exception as e:
        print("Error adding question and answer:", e)




# Define function togenerate response using GPT-3
def generate_response(prompt, user_id):
    """
    Generates a response to the user's input using GPT-3 and the conversation history.
    """
    promp=""
    p_QA = get_last_3_questions_answers(user_id)
    p=[]
    for row in p_QA:
        p.append(f"Q:{row[0]}\nA:{row[1]}\n")
    for i in range(len(p)-1,-1,-1):
        promp+=p[i]
    promp += (f"Q: {prompt}\n"
              "A:")
    print(promp)
    # Concatenate prompt and history
    # prompt = f"{prompt.strip()} {history.strip()}"

    # Generate response using GPT-3
    response = openai.Completion.create(
        engine="davinci",
        prompt=promp,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.4
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
    user_id = request.values.get('From')
    print('User ID:', user_id)
    answer = generate_response(incoming_que)
    for i in range(len(answer)):
        if answer[i]=="Q":
            if answer[i+1]==":":
                answer = answer[:i-1]
                break
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