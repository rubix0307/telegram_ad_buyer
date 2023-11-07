from django import forms


class ChannelForm(forms.Form):
    participants__gte = forms.IntegerField(label='Подписчиков От', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '0'}))
    participants__lte = forms.IntegerField(label='Подписчиков До', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '1 000 000'}))
    views__gte = forms.IntegerField(label='Просмотров От', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '1 000'}))
    views__lte = forms.IntegerField(label='Просмотров До', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '20 000'}))
    er__gte = forms.IntegerField(label='Вовлеченность От', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '70'}))
    er__lte = forms.IntegerField(label='Вовлеченность До', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '100%'}))
    lang_code = forms.ChoiceField(label='Язык канала', choices=[('', 'Выберите...'), ('ru', 'Русский'), ('ua', 'Украинский')], required=False)
