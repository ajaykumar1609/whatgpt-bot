# Flask Chatbot with OpenAI GPT-3 and MySQL

This is a Flask-based chatbot that uses OpenAI's GPT-3 natural language processing API to generate responses to user input. The chatbot also stores the conversation history in a MySQL database. You can access the bot by messaging "join salt-properly" at [+1 (415) 523-8886].

## Technologies Used

- Flask
- OpenAI API
- MySQL
- Twilio

## Installation

1. Clone the repository: `git clone https://github.com/ajaykumar1609/whatgpt-bot.git`
2. Install the required packages: `pip install -r requirements.txt`
3. Set up your Twilio account and obtain your `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_PHONE_NUMBER`.
4. Set up your OpenAI account and obtain your `OPENAI_API_KEY`.
5. Set up your MySQL database and obtain your `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, and `MYSQLDATABASE`.
6. Set your environment variables:
    - `FLASK_APP=app.py`
    - `FLASK_ENV=development`
    - `OPENAI_API_KEY=<your-openai-api-key>`
    - `MYSQLHOST=<your-mysql-host>`
    - `MYSQLPORT=<your-mysql-port>`
    - `MYSQLUSER=<your-mysql-username>`
    - `MYSQLPASSWORD=<your-mysql-password>`
    - `MYSQLDATABASE=<your-mysql-database-name>`
    - `TWILIO_ACCOUNT_SID=<your-twilio-account-sid>`
    - `TWILIO_AUTH_TOKEN=<your-twilio-auth-token>`
    - `TWILIO_PHONE_NUMBER=<your-twilio-phone-number>`
7. Run the application: `flask run`

## Usage

To use the chatbot, send a message to your Twilio phone number. The chatbot will respond with a generated response based on the conversation history.

## Deployment

This app can be easily deployed using [Railway.app](https://railway.app/). Simply create a new project, set up the environment variables, and deploy the app.

