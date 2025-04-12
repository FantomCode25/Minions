from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline
from datasets import load_dataset
import torch
import random

class EmpatheticMentalHealthChatbot:
    def __init__(self, model_name='distilbert-base-uncased-finetuned-sst-2-english', dataset_name='heliosbrahma/mental_health_chatbot_dataset'):
        # Load tokenizer and BERT model
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_name)
        
        # Load GPT-2 pipeline for text generation
        self.chatbot_model = pipeline("text-generation", model="gpt2")  # Replace with your transformer model
        
        # Load dataset
        try:
            self.dataset = load_dataset(dataset_name)
        except Exception as e:
            raise ValueError(f"Failed to load dataset: {e}")
        
        # Process dataset and verify the 'text' column
        if 'train' not in self.dataset or 'text' not in self.dataset['train'].column_names:
            raise ValueError("The dataset must contain a 'text' column in the 'train' split.")
        
        self.responses = self._load_responses()
        print("Dataset loaded and responses prepared successfully!")

    def _load_responses(self):
        """
        Load supportive responses from the dataset's 'text' column.
        """
        responses = []
        for example in self.dataset['train']:
            response_text = example.get('text')
            if response_text:
                responses.append(response_text)
        return responses

    def preprocess(self, input_text):
        """
        Tokenize user input for DistilBERT.
        """
        return self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)

    def analyze_sentiment(self, input_text):
        """
        Predict sentiment using DistilBERT.
        """
        inputs = self.preprocess(input_text)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            sentiment = torch.argmax(logits, dim=1).item()
        return sentiment

    def get_empathetic_response(self, sentiment, user_input):
        """
        Generate an empathetic response based on sentiment.
        """
        predefined_responses = []
        if sentiment == 0:  # Negative sentiment
            predefined_responses = [
                "That's unfortunate, but I'm here if you need anything.",
                "I understand how you must feel, but let's hope for the best.",
                "I'm sorry to hear that you're feeling this way. I'm here for you.",
                "It sounds like you're going through a tough time. Please know that you're not alone.",
                "I'm here to support you. Would you like to talk more about how you're feeling?",
                "It must be really hard for you. Stay strong champ!",
                "I'm feeling sorry for you, I hope it gets better.",
                "Take a moment to calm yourself. Would you like to tell more about it?",
                "It must be sad to go through all this. But don't worry, I'm here for you."
            ]
        elif sentiment == 1:  # Positive sentiment
            predefined_responses = [
                "I'm thrilled to hear that things are going so well for you.",
                "Excellent! You must be thrilled.",
                "That sounds fantastic!",
                "You must be delighted.",
                "I'm happy for you! Sounds like a good experience.",
                "That's great to hear! I'm glad things are going well for you.",
                "You sound like you're in a good place right now. Keep it up!",
                "I'm happy to hear that you're feeling positive. Keep sharing your good moments!",
                "Sounds good."
            ]
        else:  # Neutral sentiment
            predefined_responses = [
                "So would you like to talk more about it?",
                "Thanks for sharing that with me.",
                "That's interesting to know.",
                "I'll keep that in mind.",
                "Sure, sounds like I have heard it before.",
                "I see. Could you tell me more about what's on your mind?",
                "Thanks for sharing. I'm here to listen if you want to talk more.",
                "Feel free to share more if you'd like. I'm here for you.",
                "Sounds like a normal thing to do."
            ]

        # Combine predefined response with GPT-2's generated response
        predefined_response = random.choice(predefined_responses)
        gpt2_response = self.process_text(f"{predefined_response}")
        return f"{predefined_response}"

    def process_text(self, message):
        """
        Process text input using GPT-2 and return the chatbot's response.
        """
        try:
            response = self.chatbot_model(message, max_length=50, num_return_sequences=1)
            return response[0]["generated_text"]  # Extract the generated text
        except Exception as e:
            print(f"Error in chatbot processing: {e}")
            return "Sorry, I couldn't process your message."

    def chat(self):
        """
        Start chatbot interaction.
        """
        print("Chatbot is ready! Type 'exit' to end the conversation.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Chatbot: Goodbye! Take care of yourself!")
                break
            sentiment = self.analyze_sentiment(user_input)
            response = self.get_empathetic_response(sentiment, user_input)
            print(f"Chatbot: {response}")


# Run the chatbot
if __name__ == "__main__":
    chatbot = EmpatheticMentalHealthChatbot()
    chatbot.chat()