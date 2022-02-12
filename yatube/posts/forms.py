from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) == 0:
            raise forms.ValidationError('Текст Пушкин будет писать?')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) == 0:
            raise forms.ValidationError('И это весь комментарий? Пиши ещё!')
        return data
