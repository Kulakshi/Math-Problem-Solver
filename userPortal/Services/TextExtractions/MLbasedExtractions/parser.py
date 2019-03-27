from pypeg2 import *
import re

number = re.compile(r"\d+")
AnyNumber = re.compile(r"(-?)\d+")
name = re.compile(r'[\w\d]+')
word = re.compile(r"[A-Z,a-z]\w*")
dots = r'[.]+'


class subsetOP:
    grammar = ['⸦', '⊆']

class supersetOP:
    grammar = ['⊃', '⊇']

class belongToOP:
    grammar = ['∈', '∉']

# ∈,  ∉ , ⊆, ⊈, ⸦, or ⊄ △ ⊙
class inequalityOp:
    grammar = ['<', '>', '≤', '≥', '≠']


class Primary(List):
    grammar = None

class Complement(List):
    grammar = Primary, '\''

class rhs(List):
    grammar = None

# class FullExpr(List):
#     grammar = [Complement, Primary, rhs]

class AndExpr(List):
    grammar = [Complement, Primary, rhs], maybe_some(['∩','/'], [Complement, Primary, rhs])

class OrExpr(List):
    grammar = ['∪','-'], AndExpr

class Expr(List):
    grammar = ['ξ', 'ℤ', 'ℕ', '𝜙', (AndExpr, maybe_some(OrExpr))]

Primary.grammar = [('(', Expr, ')'), word]

class CardExpr(List):
    grammar = [('n', optional(blank), '(', Expr, ')'), ('|', Expr, '|')]

class CardPrimary(List):
    grammar = None

class CardFactor(List):
    grammar = CardPrimary, maybe_some(optional(['x', '/']), CardPrimary)

class CardAddExpr(List):
    grammar = ['+','-'], CardFactor

class CompCardExpr(List):
    grammar = [(CardFactor, maybe_some(CardAddExpr)), ('(', CardFactor, maybe_some(CardAddExpr),')')]

CardPrimary.grammar = [CardExpr, ('(', CompCardExpr, ')'), number]

class CardEqn(List):
    # this doesn't cover both syntax and logical errors ( there can be two numbers in the equation) => should seperate logical errors
    grammar = [(CompCardExpr, maybe_some('=', CompCardExpr), optional('=', number), maybe_some('=', CompCardExpr)),
               (number, some('=', CompCardExpr))]



class Element(List):
    grammar = [('.',maybe_some('.')), AnyNumber, word]

class ElemRhs(List):
    grammar = '{', csl(Element), '}'





class inequality(list):
    grammar = [Expr, AnyNumber], some(inequalityOp, [Expr, AnyNumber])


class setRelationExpr(List):
    grammar = Expr, some([subsetOP,supersetOP], Expr)


class belongToExpr(List):
    grammar = [Expr, Element], some(belongToOP, Expr)

class relationExpr(List):
    grammar = [setRelationExpr, belongToExpr]

class quotes(List):
    grammar = ['\"', '“'], name, maybe_some(blank, name), ['\"', '”']

class Statement(List):
    # parse text, but does not give whole statement as the output
    grammar = [(name, some(blank, name, maybe_some(quotes))), inequality, relationExpr]

class StatementRhs(List):
    # parse text, but does not give whole statement as the output
    grammar = '{', Statement, '}'


class SetBuilderRhs(List):
    grammar = '{', optional(Statement), optional(Expr), some(optional(['|', ':', ',', ';', '&', 'and']), Statement), '}'


rhs.grammar = [StatementRhs, SetBuilderRhs,ElemRhs]


class Eqn(List):
    grammar = [(Expr, some('=', [Expr, rhs, '𝜙'])),relationExpr, CardEqn, Expr]


def parseStr(text):
    try:
        f = parse(text, Eqn)
        print(f)
    except ValueError:
        print("ValueError")
        print("ValueError when parsing " + text, sys.exc_info()[1])
        return False
    except:
        e = sys.exc_info()[1]
        print("error when parsing "+ text, e)
        return False
    return True

class Notes:
   def __init__(self, token_data):
     self.token_data = token_data
     self.current_dict = {}
     self.current_vals = []
     self.parse()
   def parse(self):
     while True:
       start = next(self.token_data, None)
       if not start or "}" in start:
         break
       if start.endswith('{'):
          note = Notes(self.token_data)
          final_result = filter(lambda x:x, note.current_vals + [note.current_dict]) if note.current_vals else note.current_dict
          self.current_dict[re.findall('[\w\s\-\.]+', re.sub('^\s+', '', start))[0]] = final_result[0] if isinstance(final_result, list) and len(final_result) == 1 else final_result
          self.token_data = note.token_data
       else:
          self.current_vals.append(re.sub('^\s+', '', start))



