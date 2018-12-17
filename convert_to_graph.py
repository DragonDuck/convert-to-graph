import re
import sys


class Node(object):
    """
    A node of a hierarchical tree. Has a single parent and 0+ children
    """
    def __init__(self, name, parent=None):
        self._name = name
        self._id = re.sub(pattern="[^A-Za-z0-9]", repl="", string=name).lower()
        self._parent = parent
        self._children = []

    def __str__(self):
        return "NODE({})".format(self._name)

    def __repr__(self):
        return "NODE({})".format(self._name)

    def get_name(self):
        return self._name

    def get_id(self):
        return self._id

    def get_parent(self):
        return self._parent

    def set_parent(self, new_parent):
        self._parent = new_parent

    def get_children(self):
        return self._children

    def add_child(self, new_child):
        self._children.append(new_child)
        new_child._parent = self


def build_tree(filename):
    file = open(filename, "r")

    # Assume the first line is the base node
    first_line = file.readline().rstrip()
    base_leading_spaces = len(first_line) - len(first_line.lstrip(" "))
    cur_depth = base_leading_spaces
    cur_node = Node(name=first_line.strip())
    tree = cur_node

    for line in file:
        line = line.rstrip()
        leading_spaces = len(line) - len(line.lstrip(" "))
        new_node = Node(name=line.strip())

        # Add child
        if leading_spaces > cur_depth:
            cur_node.add_child(new_node)
            cur_depth = leading_spaces
        # Add sibling
        elif leading_spaces == cur_depth:
            cur_node.get_parent().add_child(new_node)
        # Travel back up the tree
        else:
            parent = cur_node.get_parent()
            for i in range(0, cur_depth - leading_spaces):
                parent = parent.get_parent()
            parent.add_child(new_node)
            cur_depth = leading_spaces

        cur_node = new_node

    return tree


def print_tree(tree, indent=0):
    print(" " * indent + tree.get_name())
    children = tree.get_children()
    for child in children:
        print_tree(child, indent+1)


def write_neo4j_instructions(tree):
    """
    Converts a text file into Neo4J instructions
    :param tree:
    :return:
    """
    print("CREATE ({}:Node {{name: '{}'}})".format(tree.get_id(), tree.get_name()))
    children = tree.get_children()
    for child in children:
        write_neo4j_instructions(child)

    for child in children:
        print("CREATE ({}) -[:CONTAINS]-> ({})".format(child.get_parent().get_id(), child.get_id()))


if __name__ == "__main__":
    try:
        fname = sys.argv[1]
        tree = build_tree(filename=fname)
    except IndexError:
        print("Usage: python {} <FILENAME>".format(sys.argv[0]), file=sys.stderr)
    except FileNotFoundError:
        print("File {} does not exist".format(sys.argv[1]), file=sys.stderr)
    else:
        write_neo4j_instructions(tree)
