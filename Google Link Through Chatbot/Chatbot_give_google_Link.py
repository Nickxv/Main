from googlesearch import search
import re

def search_google(query):
    search_results = list(search(query, num=3, stop=3, pause=2))

    return search_results

def process_question(question):
    # Add any preprocessing steps if needed
    # For simplicity, we remove non-alphanumeric characters
    processed_question = re.sub(r'[^a-zA-Z0-9\s]', '', question)

    return processed_question

def chatbot():
    print("Chatbot: Hello! I'm your Google search assistant. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        processed_input = process_question(user_input)
        search_results = search_google(processed_input)

        if not search_results:
            print("\nChatbot: I couldn't find any relevant results.")
        else:
            print("\nChatbot: Here are some search results:")
            for idx, result in enumerate(search_results, start=1):
                print(f"{idx}. {result}")

if __name__ == "__main__":
    chatbot()
