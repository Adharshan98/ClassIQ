"""
train_model.py
--------------
Trains TF-IDF + Logistic Regression + Naive Bayes models on a labelled
student-response dataset and saves the artefacts to model/.

Run once before launching the app:
    python train_model.py
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Output directory ──────────────────────────────────────────────────────────
_BASE      = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(_BASE, "model")
os.makedirs(MODEL_DIR, exist_ok=True)

# ── Synthetic training data ───────────────────────────────────────────────────
# Label 1 = Engaged, 0 = Not Engaged
TRAINING_DATA: list[tuple[str, int]] = [
    # Engaged responses
    ("Recursion is when a function calls itself with a smaller input until the base case is reached.", 1),
    ("The base case prevents infinite recursion by terminating the call stack.", 1),
    ("OOP uses classes and objects. Inheritance allows subclasses to reuse parent code.", 1),
    ("Polymorphism enables different classes to implement the same interface differently.", 1),
    ("Binary search works on sorted arrays by dividing the search space in half each step.", 1),
    ("The time complexity of binary search is O(log n) because we halve the array each iteration.", 1),
    ("A linked list is made of nodes where each node holds data and a pointer to the next node.", 1),
    ("Traversal of a linked list starts from the head and follows the next pointers.", 1),
    ("Dynamic programming stores sub-problem results to avoid redundant computation.", 1),
    ("Memoization is a top-down approach where results are cached in a dictionary.", 1),
    ("A hash table uses a hash function to map keys to buckets for O(1) average lookups.", 1),
    ("Collisions in hashing can be resolved using separate chaining or open addressing.", 1),
    ("BFS uses a queue and explores all neighbours level by level.", 1),
    ("DFS uses a stack or recursion and explores as far as possible before backtracking.", 1),
    ("A stack is a LIFO data structure where push adds and pop removes from the top.", 1),
    ("A queue follows FIFO, meaning the first element enqueued is the first dequeued.", 1),
    ("Merge sort divides the array recursively and merges sorted halves.", 1),
    ("QuickSort partitions the array around a pivot and sorts sub-arrays recursively.", 1),
    ("Encapsulation hides internal state and requires methods to access it.", 1),
    ("The call stack tracks function invocations and local variables during execution.", 1),
    ("Tabulation is a bottom-up DP approach that fills a table iteratively.", 1),
    ("A graph uses vertices and edges to model relationships between entities.", 1),
    ("Insertion sort works by placing each element in its correct sorted position.", 1),
    ("Binary trees have at most two children per node and support hierarchical data.", 1),
    ("The load factor of a hash table determines when to resize to maintain performance.", 1),

    # Not engaged responses
    ("I don't know how recursion works.", 0),
    ("Not sure about this concept.", 0),
    ("I'm confused and cannot explain it.", 0),
    ("I don't understand OOP at all.", 0),
    ("No idea what binary search does.", 0),
    ("I forgot the topic.", 0),
    ("I wasn't paying attention in class.", 0),
    ("I have no clue what this means.", 0),
    ("I'm lost.", 0),
    ("Vaguely remember something but can't explain.", 0),
    ("It loops somehow maybe.", 0),
    ("I think it checks every element one by one.", 0),
    ("Not clear to me.", 0),
    ("I didn't attend the lecture.", 0),
    ("My notes are missing.", 0),
    ("Confused about most of this.", 0),
    ("I can't explain it.", 0),
    ("I don't remember.", 0),
    ("Something with nodes I think.", 0),
    ("It does something with memory I forget what.", 0),
    ("I'm not confident about this topic.", 0),
    ("I need more explanation.", 0),
    ("I didn't understand the class.", 0),
    ("No clue whatsoever.", 0),
    ("I think it is some kind of loop maybe.", 0),
]

def main():
    texts, labels = zip(*TRAINING_DATA)
    texts  = list(texts)
    labels = list(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # ── TF-IDF ────────────────────────────────────────────────────────────────
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    # ── Logistic Regression ───────────────────────────────────────────────────
    lr_model = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    lr_model.fit(X_train_vec, y_train)
    print("=== Logistic Regression ===")
    print(classification_report(y_test, lr_model.predict(X_test_vec),
                                 zero_division=0))

    # ── Naive Bayes ───────────────────────────────────────────────────────────
    nb_model = MultinomialNB(alpha=0.5)
    nb_model.fit(X_train_vec, y_train)
    print("=== Naive Bayes ===")
    print(classification_report(y_test, nb_model.predict(X_test_vec),
                                 zero_division=0))

    # ── Save artefacts ────────────────────────────────────────────────────────
    with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(MODEL_DIR, "ml_model.pkl"), "wb") as f:
        pickle.dump(lr_model, f)
    with open(os.path.join(MODEL_DIR, "nb_model.pkl"), "wb") as f:
        pickle.dump(nb_model, f)

    print(f"\n✅ Models saved to {MODEL_DIR}/")


if __name__ == "__main__":
    main()
