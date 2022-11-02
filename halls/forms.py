from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['url']
        labels = {'url': "YouTube Url"}
    


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=200, label="Search video")

