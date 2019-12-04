from django import forms

# https://docs.djangoproject.com/en/2.2/topics/http/file-uploads/
class TempFileForm(forms.Form):
    file = forms.FileField()
