"""
core/question_generator.py
--------------------------
Fully offline question generator for ClassIQ.
Returns a randomly selected conceptual question from a local question bank.

If the topic is not found, returns a generic fallback question.
No external APIs, no internet connection required.
"""

import random

# ── Local Question Bank ────────────────────────────────────────────────────────
# Each topic has 3–5 conceptual short-answer questions.
QUESTION_BANK: dict[str, list[str]] = {
    "Recursion": [
        "Explain what a base case is in recursion and why it is necessary.",
        "How does the call stack behave when a recursive function is executed?",
        "What is the difference between direct and indirect recursion?",
        "What happens when a recursive function never reaches its base case?",
    ],
    "OOP": [
        "What is encapsulation and how does it improve code maintainability?",
        "Explain polymorphism with a real-world programming example.",
        "How is inheritance different from composition in object-oriented design?",
        "What is the difference between a class and an object?",
    ],
    "Linked List": [
        "What are the advantages of a linked list over an array?",
        "Explain how memory is allocated for a linked list compared to an array.",
        "Describe the process of reversing a singly linked list.",
        "What is the role of the head pointer in a linked list?",
    ],
    "Binary Search": [
        "Why must an array be sorted before applying binary search?",
        "Explain the time complexity of binary search O(log n) in simple terms.",
        "How do you find the middle element during binary search without overflow?",
    ],
    "Sorting": [
        "Compare the time complexities of Merge Sort and QuickSort. When would you use each?",
        "Explain how the pivot element is chosen and used in QuickSort.",
        "Describe the logic behind Insertion Sort and when it is most efficient.",
        "What does it mean for a sorting algorithm to be stable?",
    ],
    "Hashing": [
        "What is a hash collision and how can it be resolved using separate chaining?",
        "Explain the concept of a 'load factor' in a hash table.",
        "Why is it important to have a good hash function?",
        "What makes O(1) lookup in a hash table only an average-case guarantee?",
    ],
    "Dynamic Programming": [
        "What is the principle of optimality in Dynamic Programming?",
        "Compare memoization (top-down) and tabulation (bottom-up) approaches.",
        "Why is DP generally faster than plain recursion for problems like Fibonacci?",
        "What are 'overlapping sub-problems' and why do they matter in DP?",
    ],
    "Graph": [
        "Compare Breadth-First Search (BFS) and Depth-First Search (DFS).",
        "What is the difference between an adjacency matrix and an adjacency list?",
        "Explain what a cycle in a graph is and how DFS can detect it.",
        "What is the difference between a directed and an undirected graph?",
    ],
    "Stack": [
        "Describe the LIFO principle and give two real-world applications of a Stack.",
        "How can a stack be used to evaluate a postfix expression?",
        "Explain how the call stack operates during nested function calls.",
    ],
    "Queue": [
        "Describe the FIFO principle and give an example from operating systems.",
        "What is a circular queue and what problem does it solve?",
        "Compare a Priority Queue with a standard Queue.",
    ],
    # Additional topics from the spec
    "AI": [
        "What is the difference between supervised and unsupervised learning?",
        "Explain what a neural network is in simple terms.",
        "What role does training data play in machine learning models?",
        "What is overfitting and how can it be prevented?",
    ],
    "DBMS": [
        "What is the purpose of normalization in a relational database?",
        "Explain the difference between a primary key and a foreign key.",
        "What is a transaction and what are its ACID properties?",
        "Compare SQL and NoSQL databases with examples.",
    ],
    "OS": [
        "What is the difference between a process and a thread?",
        "Explain the concept of deadlock and the conditions required for it.",
        "What is virtual memory and why is it used?",
        "Describe the round-robin CPU scheduling algorithm.",
    ],
    "Networking": [
        "What is the role of the OSI model in computer networking?",
        "Explain how TCP differs from UDP with an example use case.",
        "What is the purpose of a subnet mask in IP addressing?",
        "How does DNS resolve a domain name to an IP address?",
    ],
    "Data Structures": [
        "What is the difference between a stack and a queue?",
        "When would you use a heap over a balanced BST?",
        "Explain the trade-offs between using an array vs. a linked list.",
        "What is a priority queue and where is it commonly used?",
    ],
}


def generate_question(topic: str) -> str:
    """
    Return a randomly selected conceptual question for the given topic.

    Falls back to a generic question if the topic is not in the question bank.

    Parameters
    ----------
    topic : str
        The lesson topic (e.g. 'Recursion', 'OOP', 'Graph').

    Returns
    -------
    str – a single conceptual question.
    """
    # Exact match first, then case-insensitive match
    bank = QUESTION_BANK.get(topic)
    if bank is None:
        # Try case-insensitive lookup
        for key in QUESTION_BANK:
            if key.lower() == topic.lower():
                bank = QUESTION_BANK[key]
                break

    if bank:
        return random.choice(bank)

    # Generic fallback for unknown topics
    return f"Explain the core concepts of {topic} in your own words."
