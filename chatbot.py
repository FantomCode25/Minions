from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from datasets import load_dataset
import torch
import random

class EmpatheticMentalHealthChatbot:
    def __init__(self, model_name='distilbert-base-uncased-finetuned-sst-2-english', dataset_name='heliosbrahma/mental_health_chatbot_dataset'):
        # Load tokenizer and BERT model
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_name)
        
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

    def get_empathetic_response(self, sentiment):
        """
        Generate an empathetic response based on sentiment.
        """
        if sentiment == 0:  # Negative sentiment
            return random.choice([
                "I'm sorry to hear that you're feeling this way. I'm here for you.",
                "It sounds like you're going through a tough time. Please know that you're not alone.",
                "I'm here to support you. Would you like to talk more about how you're feeling?"
            ])
        elif sentiment == 1:  # Positive sentiment
            return random.choice([
                "That's great to hear! I'm glad things are going well for you.",
                "You sound like you're in a good place right now. Keep it up!",
                "I'm happy to hear that you're feeling positive. Keep sharing your good moments!"
            ])
        else:  # Neutral sentiment
            return random.choice([
                "I see. Could you tell me more about what's on your mind?",
                "Thanks for sharing. I'm here to listen if you want to talk more.",
                "Feel free to share more if you'd like. I'm here for you."
            ])

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
            sentiment_label = ['Negative', 'Positive'][sentiment] if sentiment < 2 else 'Neutral'
            response = self.get_empathetic_response(sentiment)
            print(f"Chatbot: {response}")

# Run the chatbot
if __name__ == "__main__":
    chatbot = EmpatheticMentalHealthChatbot()
    chatbot.chat()
