import math
import os
import re

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dave-local-portfolio-development-key"
)


# INFIX TO POSTFIX FUNCTION
def convert_to_postfix(expression):
    precedence = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2,
        "%": 2,
        "^": 3
    }

    pattern = re.compile(
        r"\s+|[A-Za-z_][A-Za-z_0-9]*|"
        r"(?:\d+(?:\.\d*)?|\.\d+)|[()+*/%^\-]"
    )

    tokens = []
    position = 0

    while position < len(expression):
        match = pattern.match(expression, position)

        if match is None:
            raise ValueError(
                f"Unsupported character: {expression[position]}"
            )

        token = match.group()
        position = match.end()

        if not token.isspace():
            tokens.append(token)

    if not tokens:
        raise ValueError("Enter an infix expression.")

    stack = []
    output = []
    expecting_operand = True

    for token in tokens:
        if token == "(":
            if not expecting_operand:
                raise ValueError("Add an operator before '('.")

            stack.append(token)

        elif token == ")":
            if expecting_operand:
                raise ValueError("Missing operand before ')'.")

            while stack and stack[-1] != "(":
                output.append(stack.pop())

            if not stack:
                raise ValueError("Parentheses do not match.")

            stack.pop()
            expecting_operand = False

        elif token in precedence:
            if expecting_operand:
                raise ValueError(
                    "Enter an operand before the operator. "
                    "Unary plus and minus are unsupported."
                )

            while stack and stack[-1] != "(":
                top = stack[-1]

                higher = precedence[top] > precedence[token]

                equal = (
                    precedence[top] == precedence[token]
                    and token != "^"
                )

                if higher or equal:
                    output.append(stack.pop())
                else:
                    break

            stack.append(token)
            expecting_operand = True

        else:
            if not expecting_operand:
                raise ValueError(
                    "Add an operator between operands."
                )

            output.append(token)
            expecting_operand = False

    if expecting_operand:
        raise ValueError("Your expression is incomplete.")

    while stack:
        token = stack.pop()

        if token == "(":
            raise ValueError("Parentheses do not match.")

        output.append(token)

    return " ".join(output)


# VALIDATE CALCULATOR INPUTS
def read_dimension(value, name):
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Enter a valid {name.lower()}.")

    if not math.isfinite(number) or number <= 0:
        raise ValueError(
            f"{name} must be a positive, finite number."
        )

    return number


# HOME
@app.route("/")
def index():
    return render_template("index.html")


# PROFILE
@app.route("/profile")
def profile():
    return render_template("profile.html")


# WORKS AND UPPERCASE CONVERTER
@app.route("/works", methods=["GET", "POST"])
def works():
    result = None
    input_string = ""

    if request.method == "POST":
        input_string = request.form.get("inputString", "")
        result = input_string.upper()

    return render_template(
        "touppercase.html",
        result=result,
        input_string=input_string
    )


# CIRCLE AREA
@app.route("/works/area/circle", methods=["GET", "POST"])
def acircle():
    result = None
    error = ""
    radius = ""

    if request.method == "POST":
        radius = request.form.get("radius", "")

        try:
            radius_number = read_dimension(radius, "Radius")
            area = radius_number * 3.14 * radius_number

            if not math.isfinite(area):
                raise ValueError("The result is too large.")

            result = f"{area:,.2f}"

        except ValueError as message:
            error = str(message)

    return render_template(
        "circle.html",
        result=result,
        error=error,
        radius=radius
    )


# RECTANGLE AREA
@app.route("/works/area/rectangle", methods=["GET", "POST"])
def arectangle():
    result = None
    error = ""
    length = ""
    width = ""

    if request.method == "POST":
        length = request.form.get("length", "")
        width = request.form.get("width", "")

        try:
            length_number = read_dimension(length, "Length")
            width_number = read_dimension(width, "Width")

            area = length_number * width_number

            if not math.isfinite(area):
                raise ValueError("The result is too large.")

            result = f"{area:,.2f}"

        except ValueError as message:
            error = str(message)

    return render_template(
        "rectangle.html",
        result=result,
        error=error,
        length=length,
        width=width
    )


# INFIX TO POSTFIX PAGE
@app.route("/works/infix-to-postfix", methods=["GET", "POST"])
def infix_to_postfix():
    expression = ""
    result = None
    error = ""

    if request.method == "POST":
        expression = request.form.get(
            "expression", ""
        ).strip()

        try:
            result = convert_to_postfix(expression)
        except ValueError as message:
            error = str(message)

    return render_template(
        "infix_to_postfix.html",
        expression=expression,
        result=result,
        error=error
    )


# QUEUE
@app.route("/works/queue", methods=["GET", "POST"])
def queue():
    items = session.get("queue_items", [])
    message = session.pop("queue_message", "")

    if request.method == "POST":
        action = request.form.get("action", "")
        value = request.form.get("value", "").strip()

        if action == "enqueue":
            if not value:
                message = "Enter a value first."

            elif len(value) > 50:
                message = "Use up to 50 characters."

            elif len(items) >= 20:
                message = "Queue limit reached. Remove an item first."

            else:
                items.append(value)
                message = f"Added to rear: {value}"

        elif action == "dequeue":
            if items:
                removed = items.pop(0)
                message = f"Removed from front: {removed}"
            else:
                message = "The queue is empty."

        elif action == "peek":
            if items:
                message = f"Front item: {items[0]}"
            else:
                message = "The queue is empty."

        elif action == "clear":
            items = []
            message = "Queue cleared."

        session["queue_items"] = items
        session["queue_message"] = message

        return redirect(url_for("queue"))

    return render_template(
        "queue.html",
        items=items,
        message=message
    )


# DEQUE
@app.route("/works/deque", methods=["GET", "POST"])
def deque():
    items = session.get("deque_items", [])
    message = session.pop("deque_message", "")

    if request.method == "POST":
        action = request.form.get("action", "")
        value = request.form.get("value", "").strip()

        if action in ("add_front", "add_rear"):
            if not value:
                message = "Enter a value first."

            elif len(value) > 50:
                message = "Use up to 50 characters."

            elif len(items) >= 20:
                message = "Deque limit reached. Remove an item first."

            elif action == "add_front":
                items.insert(0, value)
                message = f"Added to front: {value}"

            else:
                items.append(value)
                message = f"Added to rear: {value}"

        elif action == "remove_front":
            if items:
                removed = items.pop(0)
                message = f"Removed from front: {removed}"
            else:
                message = "The deque is empty."

        elif action == "remove_rear":
            if items:
                removed = items.pop()
                message = f"Removed from rear: {removed}"
            else:
                message = "The deque is empty."

        elif action == "peek_front":
            if items:
                message = f"Front item: {items[0]}"
            else:
                message = "The deque is empty."

        elif action == "peek_rear":
            if items:
                message = f"Rear item: {items[-1]}"
            else:
                message = "The deque is empty."

        elif action == "clear":
            items = []
            message = "Deque cleared."

        session["deque_items"] = items
        session["deque_message"] = message

        return redirect(url_for("deque"))

    return render_template(
        "deque.html",
        items=items,
        message=message
    )
# BINARY SEARCH TREE FUNCTIONS
def insert_tree_node(root, value):
    if root is None:
        return {
            "value": value,
            "left": None,
            "right": None
        }

    if value < root["value"]:
        root["left"] = insert_tree_node(root["left"], value)

    elif value > root["value"]:
        root["right"] = insert_tree_node(root["right"], value)

    return root


def get_inorder(root):
    if root is None:
        return []

    return (
        get_inorder(root["left"])
        + [root["value"]]
        + get_inorder(root["right"])
    )


def get_preorder(root):
    if root is None:
        return []

    return (
        [root["value"]]
        + get_preorder(root["left"])
        + get_preorder(root["right"])
    )


def get_postorder(root):
    if root is None:
        return []

    return (
        get_postorder(root["left"])
        + get_postorder(root["right"])
        + [root["value"]]
    )


# BINARY SEARCH TREE PAGE
@app.route("/works/binary-tree", methods=["GET", "POST"])
def binary_tree():
    values = session.get("tree_values", [])
    message = session.pop("tree_message", "")

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "insert":
            raw_value = request.form.get("value", "").strip()

            try:
                value = int(raw_value)

                if value < -999 or value > 999:
                    message = "Enter a whole number from -999 to 999."

                elif value in values:
                    message = "This number is already in the tree."

                elif len(values) >= 15:
                    message = "Tree limit reached. Clear the tree first."

                else:
                    values.append(value)
                    message = f"Inserted: {value}"

            except ValueError:
                message = "Enter a valid whole number."

        elif action == "sample":
            values = [50, 30, 70, 20, 40, 60, 80]
            message = "Sample tree loaded."

        elif action == "clear":
            values = []
            message = "Tree cleared."

        session["tree_values"] = values
        session["tree_message"] = message

        return redirect(url_for("binary_tree"))

    root = None

    for value in values:
        root = insert_tree_node(root, value)

    return render_template(
        "binary_tree.html",
        root=root,
        count=len(values),
        message=message,
        inorder=get_inorder(root),
        preorder=get_preorder(root),
        postorder=get_postorder(root)
    ) 

# CONTACT
@app.route("/contact")
def contact():
    return render_template("contact.html")


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True) 