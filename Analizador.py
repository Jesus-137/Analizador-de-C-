from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Define the keywords, symbols, and regex patterns for tokens
KEYWORDS = {'for', 'int', 'return', 'include', 'iostream'}
SYMBOLS = {';', '{', '}', '(', ')', '<<', '>>', '<', '>', '::', '#'}
IDENTIFIER = r'[a-zA-Z_]\w*'
NUMBER = r'\d+'
STRING = r'".*?"'

# Adjust TOKEN_REGEX to handle multi-character symbols first
TOKEN_REGEX = re.compile(f'({"|".join(map(re.escape, SYMBOLS))}|{IDENTIFIER}|{NUMBER}|{STRING})')

def tokenize(code):
    tokens = []
    for match in TOKEN_REGEX.finditer(code):
        token = match.group(0)
        if token in KEYWORDS:
            tokens.append(('KEYWORD', token))
        elif token in SYMBOLS:
            tokens.append(('SYMBOL', token))
        elif re.match(NUMBER, token):
            tokens.append(('NUMBER', token))
        elif re.match(STRING, token):
            tokens.append(('STRING', token))
        else:
            tokens.append(('IDENTIFIER', token))
    return tokens

def syntactic_analysis(tokens):
    try:
        idx = 0

        # Parse #include <iostream>
        if tokens[idx] == ('SYMBOL', '#'):
            idx += 1
            if tokens[idx] != ('KEYWORD', 'include'):
                return "Error: Se esperaba include después de #"
            idx += 1
            if tokens[idx] != ('SYMBOL', '<'):
                return "Error: Se esperaba < después de include"
            idx += 1
            if tokens[idx][1] != 'iostream':
                return "Error: Se esperaba iostream después de <"
            idx += 1
            if tokens[idx] != ('SYMBOL', '>'):
                return "Error: Se esperaba >"
            idx += 1
        else:
            return "Error: Se esperaba # al inicio"

        # Parse int main()
        if tokens[idx] != ('KEYWORD', 'int'):
            return f"Error: Se esperaba int tiene: {tokens[idx]}"
        idx += 1
        if tokens[idx] != ('IDENTIFIER', 'main'):
            return f"Error: Se esperaba main tiene: {tokens[idx]}"
        idx += 1
        if tokens[idx] != ('SYMBOL', '('):
            return f"Error: Se esperaba ( tiene: {tokens[idx]}"
        idx += 1
        if tokens[idx] != ('SYMBOL', ')'):
            return f"Error: Se esperaba ) tiene: {tokens[idx]}"
        idx += 1
        if tokens[idx] != ('SYMBOL', '{'):
            return 'Error: Se esperaba { tiene: ' + str(tokens[idx])
        idx += 1

        # Parse statements
        while tokens[idx] != ('SYMBOL', '}'):
            # Parse std::cout << "Hola, mundo";
            if tokens[idx] == ('IDENTIFIER', 'std'):
                idx += 1
                if tokens[idx] != ('SYMBOL', '::'):
                    return f"Error: Se esperaba :: después de std tiene: {tokens[idx]}"
                idx += 1
                if tokens[idx] != ('IDENTIFIER', 'cout'):
                    return f"Error: Se esperaba cout tiene: {tokens[idx]}"
                idx += 1
                if tokens[idx] != ('SYMBOL', '<<'):
                    return f"Error: Se esperaba << tiene: {tokens[idx]}"
                idx += 1
                if tokens[idx][0] != 'STRING':
                    return f"Error: Se esperaba un string después de << tiene: {tokens[idx]}"
                idx += 1
                if tokens[idx] != ('SYMBOL', ';'):
                    return f"Error: Se esperaba ; al final de la línea tiene: {tokens[idx]}"
                idx += 1
            else:
                return f"Error: Se esperaba std::cout << tiene: {tokens[idx]}"

            # Parse return 0;
            if tokens[idx] == ('KEYWORD', 'return'):
                idx += 1
                if tokens[idx][0] != 'NUMBER':
                    return f"Error: Se esperaba un número después de return tiene: {type(tokens[idx])}"
                idx += 1
                if tokens[idx] != ('SYMBOL', ';'):
                    return f"Error: Se esperaba ; al final de return tiene: {tokens[idx]}"
                idx += 1
            else:
                return "Error: Se esperaba return"

        return "Sintaxis Correcta"
    except IndexError:
        return "Error: Sintaxis incompleta"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lexical', methods=['POST'])
def lexical():
    code = request.json['code']
    tokens = tokenize(code)
    result = "\n".join([f"Token: {token_type}, Value: {value}" for token_type, value in tokens])
    return jsonify(result=result)

@app.route('/syntactic', methods=['POST'])
def syntactic():
    code = request.json['code']
    tokens = tokenize(code)
    result = syntactic_analysis(tokens)
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)
