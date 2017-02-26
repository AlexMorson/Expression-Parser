import expressionParser
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("calibri.ttf", 16)#"courbd.ttf", 16)
marginTop = 1#3
lineThickness = 1

backgroundColour = (54, 57, 62, 255)
foregroundColour = (185, 186, 188, 255)

def renderText(text):
    if text == "":
        return Image.new("RGBA", (1, 1), backgroundColour)
    
    im = Image.new("RGBA", (1,1))
    draw = ImageDraw.Draw(im)
    width, height = draw.textsize(text, font)

    im = Image.new("RGBA", (width, height-marginTop), backgroundColour)
    draw = ImageDraw.Draw(im)
    draw.text((0, -marginTop), text, foregroundColour, font)

    return im

def surroundImageWithText(leftText, image, rightText):
    imLeft = renderText(leftText)
    imRight = renderText(rightText)

    height = image.size[1]

    imLeft = imLeft.resize((imLeft.size[0], height))
    imRight = imRight.resize((imRight.size[0], height))

    return composeImagesHorizontally(imLeft, image, imRight)

def composeImagesHorizontally(*images):
    width = sum(image.size[0] for image in images)
    height = max(image.size[1] for image in images)

    im = Image.new("RGBA", (width, height), backgroundColour)
    
    currentXPos = 0
    for image in images:
        im.paste(image, (currentXPos, (height-image.size[1])//2))
        currentXPos += image.size[0]

    return im

def composeImagesVertically(*images):
    width = max(image.size[0] for image in images)
    height = sum(image.size[1] for image in images)

    im = Image.new("RGBA", (width, height), backgroundColour)
    
    currentYPos = 0
    for image in images:
        im.paste(image, ((width-image.size[0])//2, currentYPos))
        currentYPos += image.size[1]

    return im

def composeImagesDiagonally(centre, tl=None, tr=None, bl=None, br=None):
    tlw, tlh = (0, 0) if tl is None else tl.size
    trw, trh = (0, 0) if tr is None else tr.size
    blw, blh = (0, 0) if bl is None else bl.size
    brw, brh = (0, 0) if br is None else br.size

    leftWidth = max(tlw, blw)
    rightWidth = max(trw, brw)
    topHeight = max(tlh, trh)
    bottomHeight = max(blh, brh)

    width = leftWidth + centre.size[0] + rightWidth
    height = topHeight + centre.size[1] + bottomHeight

    im = Image.new("RGBA", (width, height), backgroundColour)

    im.paste(centre, (leftWidth, topHeight))

    if tl is not None: im.paste(tl, (leftWidth-tlw, topHeight-tlh))
    if tr is not None: im.paste(tr, (leftWidth+centre.size[0], topHeight-trh))
    if bl is not None: im.paste(bl, (leftWidth-blw, topHeight+centre.size[1]))
    if br is not None: im.paste(br, (leftWidth+centre.size[0], topHeight+centre.size[1]))

    return im

def renderPrefixOperation(operator, left):
    brackets = operator not in ("abs", "sqrt")
    imLeft = renderExpression(left, brackets)

    if operator == "abs":
        return surroundImageWithText("|", imLeft, "|")

    if operator == "sqrt":
        height = imLeft.size[1] + lineThickness + 2
        sqrtTickWidth = max(lineThickness+2, int(height**0.5))
        width = imLeft.size[0] + sqrtTickWidth + lineThickness + 3 # Nice padding

        # Draw larger then scale down
        scale = 2
        imSqrt = Image.new("RGBA", (scale*width, scale*height), backgroundColour)
        draw = ImageDraw.Draw(imSqrt)
        draw.line([(0, scale*(height-int(height**0.75))), (scale*sqrtTickWidth, scale*height), (scale*sqrtTickWidth, 0), (scale*(width-lineThickness), 0), (scale*(width-lineThickness), scale*int(height**0.5))], foregroundColour, 2*lineThickness)
        imSqrt = imSqrt.resize((width, height), Image.LANCZOS)

        imSqrt.paste(imLeft, (sqrtTickWidth+lineThickness, lineThickness+2))

        return imSqrt

    # Default
    return composeImagesHorizontally(renderText(operator), imLeft)

def renderBinaryOperation(left, operator, right):
    # Check if brackets are needed
    if operator in ("=", "+", "/", "C", "^"):
        leftBrackets = False
        rightBrackets = False
    elif operator == "-":
        leftBrackets = False
        rightBrackets = right.binaryOperator == "+"
    elif operator == "*":
        leftBrackets = left.binaryOperator in ("+", "-")
        rightBrackets = right.binaryOperator in ("+", "-")
    else:
        leftBrackets = True
        rightBrackets = True

    # Remove extra multiplication signs
    if operator == "*":
        operator = "×"
        if left.isConstant():
            if right.isConstant():
                if str(right.left).isalpha():
                    operator = ""
            else:
                if right.binaryOperator == "*" and right.left.isConstant():
                    if str(right.left.left).isalpha():
                        operator = ""
                    rightBrackets = False
                elif right.prefixOperator != "":
                    if str(left.left).isalpha():
                        rightBrackets = False
                    else:
                        rightBrackets = False
                        operator = ""
                else:
                    rightBrackets = True
                    operator = ""

    # Render
    imLeft = renderExpression(left, leftBrackets)
    imRight = renderExpression(right, rightBrackets)
        
    if operator == "/":
        divideWidth = max(imLeft.size[0], imRight.size[0]) + lineThickness + 2
        
        imDivide = Image.new("RGBA", (divideWidth, lineThickness + 2), backgroundColour)
        draw = ImageDraw.Draw(imDivide)
        draw.line([(0, 1), (divideWidth, 1)], foregroundColour, lineThickness)
        
        return composeImagesVertically(imLeft, imDivide, imRight)
    
    if operator == "C":
        return composeImagesDiagonally(renderText("C"), tl=imLeft, br=imRight)
    
    if operator == "^":
        return composeImagesDiagonally(imLeft, tr=imRight)

    # Just render side by side
    return composeImagesHorizontally(imLeft, renderText(operator), imRight)

def renderPostfixOperation(left, operator):
    imLeft = renderExpression(left)
    
    return composeImagesHorizontally(imLeft, renderText(operator))

def renderExpression(expression, brackets=False):
    if type(expression) == expressionParser.Constant:
        return renderText(str(expression))

    if expression.prefixOperator != "":
        image = renderPrefixOperation(expression.prefixOperator, expression.left)
    
    elif expression.binaryOperator != "":
        image = renderBinaryOperation(expression.left, expression.binaryOperator, expression.right)

    elif expression.postfixOperator != "":
        image = renderPostfixOperation(expression.left, expression.postfixOperator)

    else:
        image = renderExpression(expression.left)

    if brackets:
        return surroundImageWithText("(", image, ")")
    else:
        return image

if __name__ == "__main__":
    expression = expressionParser.Expression("1+sqrt(5sin((1-x)/2))/5y")
    im = renderExpression(expression)
    im.save("test.png")
