from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
from collections import defaultdict

app = Flask(__name__)
CORS(app)

def is_valid(edge):
    edge = edge.strip()
    if not re.match(r'^[A-Z]->[A-Z]$', edge):
        return False
    if edge[0] == edge[3]:
        return False
    return True

@app.route('/')
def home():
    return "Backend is running!"

@app.route('/bfhl', methods=['POST'])
def bfhl():
    data = request.json.get("data", [])

    valid_edges = []
    invalid_entries = []
    duplicate_edges = []

    seen = set()

    for edge in data:
        edge = edge.strip()
        if not is_valid(edge):
            invalid_entries.append(edge)
            continue

        if edge in seen:
            if edge not in duplicate_edges:
                duplicate_edges.append(edge)
            continue

        seen.add(edge)
        valid_edges.append(edge)

    graph = defaultdict(list)
    child_nodes = set()

    for edge in valid_edges:
        parent, child = edge.split("->")
        graph[parent].append(child)
        child_nodes.add(child)

    nodes = set(graph.keys()) | child_nodes
    roots = [n for n in nodes if n not in child_nodes]

    hierarchies = []
    total_cycles = 0
    max_depth = 0
    largest_root = ""

    def dfs(node, visited, rec):
        if node in rec:
            return True
        if node in visited:
            return False

        visited.add(node)
        rec.add(node)

        for nei in graph[node]:
            if dfs(nei, visited, rec):
                return True

        rec.remove(node)
        return False

    def build_tree(node):
        tree = {}
        for child in graph[node]:
            tree[child] = build_tree(child)
        return tree

    def depth(node):
        if not graph[node]:
            return 1
        return 1 + max(depth(child) for child in graph[node])

    for root in roots:
        visited = set()
        rec = set()

        if dfs(root, visited, rec):
            total_cycles += 1
            hierarchies.append({
                "root": root,
                "tree": {},
                "has_cycle": True
            })
        else:
            d = depth(root)
            if d > max_depth or (d == max_depth and root < largest_root):
                max_depth = d
                largest_root = root

            hierarchies.append({
                "root": root,
                "tree": {root: build_tree(root)},
                "depth": d
            })

    return jsonify({
        "user_id": "aditya_11082005",
        "email_id": "ac3459@srmist.edu.in",
        "college_roll_number": "RA2311003010936",
        "hierarchies": hierarchies,
        "invalid_entries": invalid_entries,
        "duplicate_edges": duplicate_edges,
        "summary": {
            "total_trees": len(hierarchies) - total_cycles,
            "total_cycles": total_cycles,
            "largest_tree_root": largest_root
        }
    })

if __name__ == '__main__':
    print("🚀 Server starting...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)