import re
import sys
import keyword

inputString = ""
nextToken = ""


def lex():
    global inputString
    global nextToken
    termList = ["program", "if", "while", "begin", "read", "write", "end", "then", "else", "do"]

    p = re.compile('\S.*?(?= *\ )')
    iS = p.match(inputString)

    p = re.compile(':=')
    m = p.match(iS.group())
    if (m != None):
        nextToken = ':='
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    p = re.compile('[()]')
    m = p.match(iS.group())
    if (m != None):
        nextToken = '('
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    p = re.compile(';')
    m = p.match(iS.group())
    if (m != None):
        nextToken = ';'
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    p = re.compile(',')
    m = p.match(iS.group())
    if (m != None):
        nextToken = ','
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    p = re.compile('([*/])')
    m = p.match(iS.group())
    if (m != None):
        nextToken = '<multiplying_operator>'
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    p = re.compile('([+-])')
    m = p.match(iS.group())
    if (m != None):
        if (nextToken == '<term>'):
            nextToken = '<adding_operator>'
            inputString = inputString.replace(m.group() + " ", "", 1)
            return
        else:
            nextToken = '<sign>'
            inputString = inputString.replace(m.group() + " ", "", 1)
            return

    p = re.compile('([=><][=>]?)')
    m = p.match(iS.group())
    if (m != None):
        nextToken = '<relational_operator>'
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    p = re.compile('([A-Za-z]\w*)')
    m = p.match(iS.group())

    if (m != None):
        p2 = re.compile('([A-Z]\w*)')
        m2 = p2.match(inputString)
        if (m.group() in termList):
            nextToken = m.group()
            inputString = inputString.replace(m.group() + " ", "", 1)
            return
        elif (m2 != None and nextToken == 'program'):
            nextToken = '<progname>'
            inputString = inputString.replace(m2.group() + " ", "", 1)
            return
        else:
            if (m.group() in keyword.kwlist):
                print("Error: ", m.group(), " is a reserved word")
                sys.exit(1)
            nextToken = '<variable>'
            inputString = inputString.replace(m.group() + " ", "", 1)
            return

    p = re.compile('([1-9]\d*)')
    m = p.match(iS.group())
    if ((m != None) or (inputString[0] == '0')):
        nextToken = '<constant>'
        inputString = inputString.replace(m.group() + " ", "", 1)
        return

    print("Unknown symbol encountered")
    print("InputString: " + inputString + nextToken)
    sys.exit(1)


def program():
    global inputString
    global nextToken
    lex()
    if (nextToken == 'program'):
        lex()
        if (nextToken == '<progname>'):
            lex()
            compound_stmt()
        else:
            print("Expected a program name; got " + nextToken)
            sys.exit(3)
    else:
        print("Expected 'program'; got " + nextToken)
        sys.exit(2)


def compound_stmt():
    global inputString
    global nextToken
    if (nextToken == 'begin'):
        stmt()
        while (nextToken == ';'):
            stmt()

        if (nextToken == 'end'):
            if (inputString != ''):
                lex()
            return
        else:
            print("Error: expected end got ", nextToken)
            sys.exit(4)
    else:
        print("Error")
        sys.exit(42)


def stmt():
    global inputString
    global nextToken
    lex()
    if (nextToken == 'read' or nextToken == 'write' or nextToken == '<variable>'):
        simple_stmt()
        print("simple stmt hit")
    elif (nextToken == 'if' or nextToken == 'while' or nextToken == 'begin'):
        structured_stmt()
        print("structured stmt hit")
    else:
        print("Error: Expected statement start, got ", nextToken)
        sys.exit(6)


def simple_stmt():
    global inputString
    global nextToken

    if (nextToken == 'read'):
        read_stmt()
        print("read stmt hit")

    elif (nextToken == 'write'):
        write_stmt()
        print("write stmt hit")

    elif (nextToken == '<variable>'):
        assignment_stmt()
        print("assignment stmt hit")


def assignment_stmt():
    global inputString
    global nextToken

    lex()
    if (nextToken == ':='):
        lex()
        expression()

    else:
        print("expected :=, got ", nextToken)
        sys.exit(7)


def read_stmt():
    global inputString
    global nextToken
    lex()
    if (nextToken == '('):
        lex()
        if (nextToken == '<variable>'):
            lex()
            while (nextToken == ','):
                lex()
                if (nextToken != '<variable>'):
                    print("Error: expected <variable> got ", nextToken)
                    sys.exit(8)
                lex()
        lex()
    else:
        print("Error: expected ( got ", nextToken)
        sys.exit(8)


def write_stmt():
    global inputString
    global nextToken

    lex()

    if (nextToken == '('):

        expression()

        while (nextToken == ','):
            nextToken = '<expression>'
            expression()
            lex()
    else:
        print("Error: expected ( got ", nextToken)
        sys.exit(9)


def structured_stmt():
    global nextToken
    global inputString

    if (nextToken == 'begin'):
        compound_stmt()
        print("compound stmt hit")

    elif (nextToken == 'if'):
        if_stmt()
        print("if stmt hit")

    elif (nextToken == 'while'):
        while_stmt()
        print("while stmt hit")


def if_stmt():
    global inputString
    global nextToken

    lex()
    expression()
    if (nextToken == 'then'):
        stmt()
        if (nextToken == 'else'):
            stmt()

    else:
        print("Error: Expected then got ", nextToken)
        sys.exit(10)


def while_stmt():
    global inputString
    global nextToken
    lex()

    expression()
    if (nextToken == 'do'):
        nextToken = '<stmt>'
        stmt()

    else:
        print("Error: Expected do got ", nextToken)
        sys.exit(11)


def expression():
    global inputString
    global nextToken

    simple_expr()
    if (nextToken == '<relational_operator>'):
        lex()
        simple_expr()


def simple_expr():
    global inputString
    global nextToken

    if (nextToken == '<sign>'):
        lex()
    term()

    while (nextToken == '<adding_operator>'):
        lex()
        term()


def term():
    global inputString
    global nextToken

    factor()
    while (nextToken == '<multiplying_operator>'):
        lex()
        factor()


def factor():
    global inputString
    global nextToken

    if (nextToken == '('):
        lex()
        expression()
        if (nextToken != 'end'):
            nextToken = '<term>'
            lex()

    elif (nextToken == '<variable>' or nextToken == '<constant>'):
        nextToken = '<term>'
        lex()

    else:
        print("Error: expected an expression, <variable>, or <constant> got ", nextToken)
        sys.exit(12)


with open('test cases.txt') as tc:
    for inputString in tc:
        inputString = inputString.replace('\n', '')
        program()
        print("The string is syntactically correct! :)")
