from django import forms


class MailingForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    img = forms.ImageField()