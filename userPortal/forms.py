from django import forms
from .Services.Utils import util

INFO_TYPES = [
    (util.type1, 'Cardinality - Set notation'),
    (util.type2, 'Elements')
]
QUES_TYPES = [
    (util.type1, 'Cardinality'),
    (util.type2, 'Elements')
]
USE_ML = [
    (True, "ML based extraction"),
    (False, "Regex based extraction")
]


class ProbForm(forms.Form):
    use_ml = forms.CharField(label='Select Expression Extraction Method',
                                widget=forms.RadioSelect(choices=USE_ML))
    info_type = forms.CharField(label='Select Information Type',
                                widget=forms.RadioSelect(choices=INFO_TYPES))
    info = forms.CharField(label='Enter problem to solve', widget=forms.Textarea(attrs={'cols':120, 'rows': 8}))
    ques_type = forms.CharField(label='Select Question Type',
                                widget=forms.RadioSelect(choices=QUES_TYPES))
    question = forms.CharField(label='Enter question', widget=forms.Textarea(attrs={'cols':120, 'rows': 5}))
