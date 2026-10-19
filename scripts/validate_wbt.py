import os
import re

nodes_dir = r"C:\Program Files\Webots\resources\nodes"
node_schemas = {}

for f in os.listdir(nodes_dir):
    if f.endswith('.wrl'):
        node_name = f[:-4]
        with open(os.path.join(nodes_dir, f), 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        fields = set(re.findall(r'(?:field|vrmlField|deprecatedField)\s+\S+\s+(\w+)', content))
        node_schemas[node_name] = fields

print(f"Loaded {len(node_schemas)} node schemas.")

wbt_file = r"worlds\pista_montana_rusa.wbt"
with open(wbt_file, 'r', encoding='utf-8') as fp:
    lines = fp.readlines()

print(f"Checking {wbt_file} ({len(lines)} lines)...")

node_stack = []
errors = []

for line_num, line in enumerate(lines, 1):
    line = line.strip()
    if not line or line.startswith('#'):
        continue

    # Count braces on this line
    open_b = line.count('{')
    close_b = line.count('}')

    # Check node opening: could be "Node {", "DEF X Node {", "field Node {", "field DEF X Node {"
    m = re.search(r'(?:(?:DEF\s+\w+\s+)|(?:\w+\s+DEF\s+\w+\s+)|(?:\w+\s+))?([A-Z]\w*)\s*\{', line)
    if m:
        n_name = m.group(1)
        if n_name in node_schemas or n_name in ['Group', 'USE']:
            node_stack.append((n_name, line_num))
        else:
            errors.append(f"Line {line_num}: Unknown node '{n_name}' in '{line}'")
            node_stack.append((n_name, line_num))
    
    # Check field on this line if not opening a node
    elif node_stack:
        parent, s_line = node_stack[-1]
        if parent in node_schemas:
            fm = re.match(r'^([a-zA-Z_]\w*)\s+(.+)$', line)
            if fm:
                fname = fm.group(1)
                allowed = node_schemas[parent]
                if fname not in allowed:
                    if fname not in ['USE', 'DEF', 'children', 'boundingObject', 'physics', 'appearance', 'geometry']:
                        errors.append(f"Line {line_num}: Node '{parent}' (started L{s_line}) has unknown field '{fname}' (line: '{line}')")

    for _ in range(close_b):
        if node_stack:
            node_stack.pop()

print(f"Total REAL issues found: {len(errors)}")
for err in errors[:30]:
    print("  ->", err)
