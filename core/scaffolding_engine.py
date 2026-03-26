"""
core/scaffolding_engine.py
--------------------------
Generates targeted scaffolding / hint questions for students who score in the
"Needs Attention" category.
"""

import random

_SCAFFOLDING_BANK: dict[str, list[str]] = {
    "recursion": [
        "Can you describe what a base case is in your own words?",
        "What happens if a recursive function never reaches its base case?",
        "Try to trace the call stack for factorial(3). What do you notice?",
    ],
    "oop": [
        "Can you explain what makes a class different from an object?",
        "Try defining a simple class with one attribute and one method.",
        "What problem does inheritance solve in object-oriented programming?",
    ],
    "linked list": [
        "Can you describe how two nodes are connected in a linked list?",
        "What is the purpose of the head pointer in a linked list?",
        "How would you traverse a linked list to find a specific value?",
    ],
    "binary search": [
        "Why is binary search only applicable to sorted arrays?",
        "What does 'dividing the search space in half' mean concretely?",
        "Step through binary search on [1,3,5,7,9] looking for 5.",
    ],
    "sorting": [
        "Can you explain what 'swapping' elements means in sorting?",
        "Trace bubble sort on [3,1,2]. What happens in each pass?",
        "What does it mean for a sorting algorithm to be 'stable'?",
    ],
    "hashing": [
        "What is the role of a hash function?",
        "If two keys produce the same hash, what strategy handles this?",
        "Why is O(1) lookup in a hash table only an average-case guarantee?",
    ],
    "dynamic programming": [
        "What does 'overlapping sub-problems' mean and can you give an example?",
        "Explain memoization as if you were explaining it to a friend.",
        "How does tabulation differ from recursion with memoization?",
    ],
    "graph": [
        "What is the difference between a directed and an undirected graph?",
        "Can you describe BFS step-by-step on a small graph?",
        "How do you represent a graph using an adjacency list?",
    ],
    "stack": [
        "What does LIFO mean and can you give a real-world example?",
        "Trace push and pop operations on a stack holding [1,2,3].",
        "How is a call stack used when you call a function inside another?",
    ],
    "queue": [
        "Can you explain the FIFO principle in your own words?",
        "What happens during an enqueue and a dequeue operation?",
        "Describe a scenario where a circular queue is more efficient.",
    ],
    "default": [
        "Can you re-read the question and share any part you do understand?",
        "Try to define just one key term related to this topic.",
        "Think of a real-world analogy that might help explain this concept.",
    ],
}


def get_scaffolding_question(topic: str, index: int = 0) -> str:
    """
    Return a scaffolding hint question for a student who needs attention.

    Parameters
    ----------
    topic : str  – current lesson topic
    index : int  – student index (used for variety across students)
    """
    key  = topic.lower().strip()
    bank = _SCAFFOLDING_BANK.get(key, _SCAFFOLDING_BANK["default"])
    return bank[index % len(bank)]
