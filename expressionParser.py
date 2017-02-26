import math

prefixOperators = {
    "-": lambda a:-a,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "sqrt": math.sqrt,
    "ln": math.log
}

binaryOperators = {
    "=": lambda a,b: exec('raise Exception("Not an expression (contains an equals sign)")'),
    "+": lambda a,b: a+b,
    "-": lambda a,b: a-b,
    "*": lambda a,b: a*b,
    "/": lambda a,b: a/b,
    "C": lambda n,r: math.factorial(n) / math.factorial(r) / math.factorial(n-r),
    "^": math.pow
}

postfixOperators = {
    "!": math.factorial
}

class Expression:
    def __init__(self, expression):
        self.prefixOperator = ""
        self.left = ""
        self.binaryOperator = ""
        self.right = ""
        self.postfixOperator = ""
        
        expression = expression.replace(" ", "")

        # Check for binary operators
        for binaryOperator in binaryOperators:
            depth = 0
            for index, char in list(enumerate(expression))[::-1]:
                if char == ")":
                    depth += 1
                if char == "(":
                    depth -= 1
                    if depth < 0:
                        raise Exception("Brackets do not match")

                if depth == 0:
                    if char == binaryOperator:
                        if not ((index == 0 or expression[index-1] in binaryOperators) and binaryOperator == "-"):
                            self.operator = binaryOperators[binaryOperator]
                            self.left = Expression(expression[:index])
                            self.binaryOperator = binaryOperator
                            self.right = Expression(expression[index+1:])
                            return

        # Make sure brackets after prefix operators work as intended when post-multiplying
        depth = 0
        for index, char in enumerate(expression):
            if char == "(":
                depth += 1
            if char == ")":
                depth -= 1
            if char == ")" and depth == 0:
                if len(expression)-1 != index:
                    # Post multiplication
                    if expression[index+1] in postfixOperators:
                        if len(expression)-1 != index+1:
                            # Account for a postfix operator
                            self.__init__(expression[:index+2]+"*"+expression[index+2:])
                            return
                    else:
                        self.__init__(expression[:index+1]+"*"+expression[index+1:])
                        return
        
        # Check for postfix operators (and implicit multiplication after them)
        for postfixOperator in postfixOperators:
            depth = 0
            for index, char in enumerate(expression):
                if char == "(":
                    depth += 1
                if char == ")":
                    depth -= 1
                if char == postfixOperator and depth == 0:
                    if len(expression)-1 != index:
                        self.__init__(expression[:index+1]+"*"+expression[index+1:])
                        return
                    else:
                        self.operator = postfixOperators[postfixOperator]
                        self.postfixOperator = postfixOperator
                        self.left = Expression(expression[:-len(postfixOperator)])
                        return

        # Check for prefix operators
        for prefixOperator in prefixOperators:
            if expression.startswith(prefixOperator):
                self.operator = prefixOperators[prefixOperator]
                self.prefixOperator = prefixOperator
                self.left = Expression(expression[len(prefixOperator):])
                return

        # Try to split remainder into implicit multiplications
        if expression[0].isalpha():
            if len(expression) > 1:
                # Starts with letter
                self.__init__(expression[:1]+"*"+expression[1:])
                return
            else:
                # Just a letter
                self.left = Constant(expression)
                return
        preMultiply = expression[0] != "("
        depth = 0
        for index, char in enumerate(expression):
            if char == "(":
                depth += 1
            if char == ")":
                depth -= 1
            if preMultiply:
                if char == "(" or char.isalpha():
                    # Pre-multiplication or Numerical -> Alpha
                    self.__init__(expression[:index]+"*"+expression[index:])
                    return
            else:
                if char == ")" and depth == 0:
                    if len(expression)-1 == index:
                        # Just wrapped in brackets
                        self.__init__(expression[1:-1])
                        return
                    else:
                        # Post multiplication
                        self.__init__(expression[:index+1]+"*"+expression[index+1:])
                        return
                    
        # Left with 'unknown stuff'
        self.left = Constant(expression)

    def __repr__(self):
        return f"""Expression:
 Prefix Operator = {self.prefixOperator}
            Left = {self.left}
 Binary Operator = {self.binaryOperator}
           Right = {self.right}
Postfix Operator = {self.postfixOperator}"""

    def __str__(self):
        return f"{self.prefixOperator}({str(self.left)}{self.binaryOperator}{str(self.right)}{self.postfixOperator})"

    def evaluate(self):
        if self.prefixOperator != "" or self.postfixOperator != "":
            try:
                return self.operator(self.left.evaluate())
            except Exception as e:
                print(e)
        elif self.binaryOperator != "":
            try:
                return self.operator(self.left.evaluate(), self.right.evaluate())
            except Exception as e:
                print(e) 
        else:
            return self.left.evaluate()

class Constant:
    def __init__(self, constant):
        self.constant = constant

    def __repr__(self):
        return f"Constant = {self.constant}"

    def __str__(self):
        return self.constant

    def evaluate(self):
        return float(self.constant)
