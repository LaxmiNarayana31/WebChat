### WebChat

WebChat is a Streamlit application that enables users to chat with a website as if it were a person. It uses Gemini AI to generate responses based on the content of the website.

### Project setup

- Clone the repository:
  ```bash
  git clone https://github.com/LaxmiNarayana31/WebChat.git
  ```
- Create a virtual environment using pipenv. If you don't have pipenv installed, you can install it by running `pip install pipenv` in your terminal.
  ```bash
  pipenv shell # Create a virtual environment
  pipenv install # Install dependencies
  ```
- Create a `.env` file and add the gemini api key to it.

  ```bash
  GEMINI_API_KEY=
  ```

- Run the application:
  ```bash
  pipenv run main
  ```
  or
  ```bash
  streamlit run main.py
  ```
