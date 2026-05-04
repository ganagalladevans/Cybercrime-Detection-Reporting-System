from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# Sample dataset (you can expand later)
texts = [
    "your bank account is blocked click link",
    "urgent OTP required verify now",
    "win lottery click here",
    "hello how are you",
    "meeting scheduled tomorrow",
    "project submission deadline",
    "update your password immediately",
    "free gift claim now"
]

labels = [
    "High Risk",
    "High Risk",
    "High Risk",
    "Low Risk",
    "Low Risk",
    "Low Risk",
    "Medium Risk",
    "High Risk"
]

# Convert text to numbers
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Train model
model = MultinomialNB()
model.fit(X, labels)

# Save model and vectorizer
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model trained and saved!")