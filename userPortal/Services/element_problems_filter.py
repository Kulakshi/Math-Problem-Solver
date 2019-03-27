import re
roman_numbers = r'\((?=[MDCLXVI])M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})\)'


def hadle(info_text, ques_text, ques_type):
    info_text = info_text.replace('[', '(')
    ques_text = ques_text.replace('[', '(')
    info_text = info_text.replace(']', ')')
    ques_text = ques_text.replace(']', ')')

    if ques_type == 'elem':
        reg = re.compile(roman_numbers, re.IGNORECASE)
        results = reg.finditer(ques_text)
        if results is not None:
            for res in results:
                ques_text = ques_text.replace(res.group(), "# ")