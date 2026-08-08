import os
import sys
import logging
from dotenv import load_dotenv

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from app.db.neo4j import init_neo4j_driver, close_neo4j_driver, is_neo4j_available
from app.services.graph_service import (
    init_neo4j_constraints,
    GraphService
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def seed_knowledge_graph():
    """
    Seeds global Computer Science Knowledge Graph with foundational DSA concepts, algorithms,
    data structures, complexity, and relationships. Idempotent and safe to execute multiple times.
    """
    logger.info("Initializing Neo4j connection for seeding...")
    init_neo4j_driver()

    if not is_neo4j_available():
        logger.error("❌ Neo4j unavailable. Check NEO4J_ENABLED, NEO4J_URI, and NEO4J_PASSWORD settings in .env.")
        return

    logger.info("Setting up Neo4j uniqueness constraints...")
    init_neo4j_constraints()

    logger.info("Seeding foundational Data Structures...")
    ds_list = [
        ("Array", "Contiguous array of elements stored in sequential memory locations"),
        ("Linked List", "Linear data structure where elements are linked using pointers"),
        ("Stack", "LIFO (Last In First Out) abstract data type"),
        ("Queue", "FIFO (First In First Out) abstract data type"),
        ("Hash Map", "Key-value pair data structure providing average O(1) lookups"),
        ("Binary Tree", "Hierarchical tree structure with at most two children per node"),
        ("Binary Search Tree", "Binary tree with left child < parent <= right child invariant"),
        ("Heap", "Tree-based data structure satisfying the max-heap or min-heap property"),
        ("Priority Queue", "Abstract queue where elements have priority values"),
        ("Graph", "Non-linear data structure consisting of vertices (nodes) and edges")
    ]
    for name, desc in ds_list:
        GraphService.create_or_get_data_structure(name, description=desc)

    logger.info("Seeding foundational Core Concepts & Categories...")
    concept_list = [
        ("Searching", "Finding specific element target in datasets", "Category"),
        ("Sorting", "Ordering elements according to specific key comparator", "Category"),
        ("Recursion", "Solving problems by breaking them into smaller instances of same problem", "Technique"),
        ("Divide and Conquer", "Algorithmic paradigm breaking problems into subproblems and combining results", "Paradigm"),
        ("Greedy Paradigm", "Making locally optimal choices at each stage", "Paradigm"),
        ("Dynamic Programming", "Optimizing overlapping subproblems using memoization/tabulation", "Paradigm"),
        ("Shortest Path", "Finding path between vertices in graph such that sum of edge weights is minimized", "Problem")
    ]
    for name, desc, cat in concept_list:
        GraphService.create_or_get_concept(name, category=cat, description=desc)

    logger.info("Seeding foundational Algorithms...")
    algo_list = [
        ("Linear Search", "Sequential search across elements in O(n) time", "Searching"),
        ("Binary Search", "Logarithmic O(log n) search on sorted arrays", "Searching"),
        ("Bubble Sort", "Simple comparison sort swapping adjacent elements", "Sorting"),
        ("Merge Sort", "Divide-and-conquer O(n log n) stable sorting algorithm", "Sorting"),
        ("Quick Sort", "In-place partition sorting algorithm", "Sorting"),
        ("BFS", "Breadth-First Search level-order traversal for graphs and trees", "Graph Traversal"),
        ("DFS", "Depth-First Search deep-branch traversal for graphs and trees", "Graph Traversal"),
        ("Dijkstra's Algorithm", "Single-source shortest path algorithm on non-negative weighted graphs", "Graph Algorithm")
    ]
    for name, desc, cat in algo_list:
        GraphService.create_or_get_algorithm(name, category=cat, description=desc)

    logger.info("Seeding Complexity Nodes...")
    complexities = [
        ("O(1)", "Constant time complexity"),
        ("O(log n)", "Logarithmic time complexity"),
        ("O(n)", "Linear time complexity"),
        ("O(n log n)", "Linearithmic time complexity"),
        ("O(n²)", "Quadratic time complexity"),
        ("O((V+E)logV)", "Weighted graph search complexity")
    ]
    for notation, desc in complexities:
        GraphService.create_or_get_complexity(notation, description=desc)

    logger.info("Creating Relationships & Learning Paths...")
    # Prerequisites
    prereqs = [
        ("Array", "Binary Search"),
        ("Sorting", "Binary Search"),
        ("Array", "Merge Sort"),
        ("Recursion", "Merge Sort"),
        ("Array", "Quick Sort"),
        ("Recursion", "Quick Sort"),
        ("Graph", "BFS"),
        ("Queue", "BFS"),
        ("Graph", "DFS"),
        ("Stack", "DFS"),
        ("Graph", "Dijkstra's Algorithm"),
        ("Priority Queue", "Dijkstra's Algorithm"),
        ("Binary Tree", "Binary Search Tree"),
        ("Binary Tree", "Heap"),
        ("Heap", "Priority Queue")
    ]
    for p, t in prereqs:
        GraphService.add_prerequisite(p, t)

    # Related Concepts
    related = [
        ("Binary Search", "Divide and Conquer"),
        ("Binary Search", "Two Pointer"),
        ("Merge Sort", "Divide and Conquer"),
        ("Quick Sort", "Divide and Conquer"),
        ("BFS", "DFS"),
        ("Dijkstra's Algorithm", "BFS"),
        ("Dijkstra's Algorithm", "Bellman-Ford"),
        ("Dijkstra's Algorithm", "Shortest Path")
    ]
    for a, b in related:
        GraphService.add_related_concept(a, b)

    # Algorithm Uses Data Structure
    uses = [
        ("Dijkstra's Algorithm", "Priority Queue"),
        ("BFS", "Queue"),
        ("DFS", "Stack"),
        ("Binary Search", "Array")
    ]
    for algo, ds in uses:
        GraphService.add_uses_relationship(algo, ds)

    # Algorithm Solves Problem
    solves = [
        ("Dijkstra's Algorithm", "Shortest Path"),
        ("Binary Search", "Searching"),
        ("Merge Sort", "Sorting"),
        ("Quick Sort", "Sorting")
    ]
    for algo, prob in solves:
        GraphService.add_solves_relationship(algo, prob)

    # Complexities
    cxs = [
        ("Binary Search", "O(log n)"),
        ("Linear Search", "O(n)"),
        ("Merge Sort", "O(n log n)"),
        ("Quick Sort", "O(n log n)"),
        ("Bubble Sort", "O(n²)"),
        ("Dijkstra's Algorithm", "O((V+E)logV)"),
        ("Hash Map", "O(1)")
    ]
    for entity, cx in cxs:
        GraphService.add_complexity_relationship(entity, cx)

    logger.info("✅ Knowledge Graph successfully seeded!")
    close_neo4j_driver()


if __name__ == "__main__":
    seed_knowledge_graph()
