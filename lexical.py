import argparse

SEPARATOR = [' ', '\n', '\t', '\b']
BRACKET = ['(', ')', '[', ']', '{', '}', ';', ',']
keyword_lists = ['boolean', 'break', 'continue', 'else', 'for', 'float', 'if', 'int', 'return', 'void', 'while']
boolean_const = ['false', 'true']


class CharacterType:

    def __init__(self, lines):
        """
        Init the mapping with a list of lines
        :param lines: A list of lines which use to define the character set for each token type
        """

        self.character2type = {}
        for i, line in enumerate(lines):
            for c in line.strip():
                self.character2type[c] = i

        self.n = len(lines)

    def get_edge(self, c):
        """

        :param c: input character
        :return:
            A number which indicates the the token type, is used for following the automata
        """
        if c in SEPARATOR:
            return self.n-1

        if c in BRACKET:
            return self.n-1

        i = self.character2type.get(c, -1)

        # We get an out of vocabulary character
        if i == -1:
            return self.n-1
        else:
            return i


class DFA:
    """
        Represent a DFA class
    """

    def __init__(self, input_file):
        """

        :param input_file: Init the DFA with the input file
        """

        # The graph is stored as an dictionary
        # for example: self.graph[0] represent a list of state when following each token types
        self.graph = {}

        with open(input_file, 'r') as f:
            line1 = f.readline()
            line1_int = [int(w) for w in line1.strip().split()]
            n = line1_int[0]
            d = line1_int[1]

            # Read transition graph
            for i in range(n):
                line = f.readline()
                tmp = [int(w) if w != 'x' else -1 for w in line.strip().split() ]
                self.graph[tmp[0]] = [0]*(d-1)
                for j in range(1, len(tmp)):
                    self.graph[tmp[0]][j-1] = tmp[j]

            # Read mapping character type
            list_character_types = []
            for i in range(d):
                list_character_types.append(f.readline().strip())

            self.parser_character = CharacterType(list_character_types[1:])

            # Read ending state
            line = f.readline().strip().split()
            line1 = f.readline().strip().split()
            list_ending_asterisk = [int(w) for w in line[1:]]
            name_ending_asterisk = [w for w in line1[1:]]

            # Register the ending states with asterisk
            self.ending_asterisk = dict([(list_ending_asterisk[i], name_ending_asterisk[i])
                                         for i in range(len(list_ending_asterisk))])

            line = f.readline().strip().split()
            line1 = f.readline().strip().split()
            list_ending = [int(w) for w in line[1:]]
            name_ending = [w for w in line1[1:]]
            # Register the normal ending states
            self.ending = dict([(list_ending[i], name_ending[i])
                                for i in range(len(list_ending))])

    def run_forward(self, word, input_state, ch):
        """

        :param word: the reading word
        :param input_state: the state
        :param ch: the next character
        :return: A tuple of (flag, next word, next state, info)
            info is the metadata which is used to retrieve the token, token type and the error information
        """
        c_type = self.parser_character.get_edge(ch)

        if c_type == -1:
            # Skip separator
            return True, word, input_state, {"token": "", "token_type": "NA", "error": False}
        else:
            edge = self.graph.get(input_state, [])
            if len(edge) == 0:
                # Going from a no-edge state
                if (ch not in SEPARATOR) and (ch not in BRACKET):
                    return False, word, 0, {"token": "", "token_type": "NA", "error": True}
                else:
                    return True, word, 0, {"token": "", "token_type": "NA", "error": False}

            output_st = edge[c_type]
            if output_st == -1:
                # Follow a no-edge connection
                if (ch not in SEPARATOR) and (ch not in BRACKET):
                    return False, word, 0, {"token": "", "token_type": "NA", "error": True}
                else:
                    return True, word, 0, {"token": "", "token_type": "NA", "error": False}

            elif output_st in self.ending:
                # Reach a normal ending state
                token = word + ch
                token_type = self.ending[output_st]
                return True, "", 0, {"token": token, "token_type": token_type, "error": False}
            elif output_st in self.ending_asterisk:
                # Reach an one-step-back ending state
                if ch not in SEPARATOR:
                    flag, next_word, next_state, info = self.run_forward("", 0, ch)
                    token = word
                    token_type = self.ending_asterisk[output_st]

                    return flag, next_word.strip(), next_state,\
                           {"token": token, "token_type": token_type, "error": info["error"]}
                else:
                    token = word
                    token_type = self.ending_asterisk[output_st]
                    return True, "", 0, {"token": token, "token_type": token_type, "error": False}

            return True, word+ch, output_st, {"token": "", "token_type": "NA", "error": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # General parameters
    parser.add_argument('--input_dfa', type=str, default='./dfa.dat',
                        help='Input transition table')
    parser.add_argument('--input_file', type=str, default='./test.vc',
                        help='Input source file')
    parser.add_argument('--output_file', type=str, default='./test.vctok',
                        help='Output lexical analysis result of the input source file')
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()

    dfa = DFA(args.input_dfa)

    input_file = args.input_file
    output_file = args.output_file
    # Debug flag
    DEBUG = args.debug

    token_set = set()

    line_number = 0
    with open(input_file, "r") as f:
        with open(output_file, "w") as fout:
            for line in f.readlines():
                line_number += 1

                word = ""
                input_state = 0

                i = 0
                for c in line:
                    i += 1
                    flag, next_word, next_state, info = dfa.run_forward(word, input_state, c)

                    if info["error"]:
                        # Output the lexical error and skip to next line
                        print("Compiler error at line %i, index %i" % (line_number, i))
                        word = ""
                        input_state = 0
                        break

                    token = info['token']
                    token_type = info['token_type']
                    if DEBUG:
                        print(c, flag, next_word, next_state, token)
                        if len(token) > 0:
                            print("-----------")
                            print("Parsing output = ", token, token_type)
                            print("-----------")

                    if len(token) > 0:
                        if token not in token_set:
                            if token_type == 'identifier':
                                # Check for special cases with identifier
                                if token in keyword_lists:
                                    token_type = token + "_keyword"
                                elif token in boolean_const:
                                    token_type = token + "_boolean_const"

                            fout.write("%s %s\n" % (token, token_type))
                            token_set.add(token)

                    word = next_word.strip()
                    input_state = next_state
