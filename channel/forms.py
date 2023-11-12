from django import forms


class ChannelForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.subscription = kwargs.pop('subscription', None)
        super(ChannelForm, self).__init__(*args, **kwargs)

        self.fields['ads_period_min'].widget.attrs['placeholder'] = str(self.subscription.ads_period_min) if self.subscription else '-'
        self.fields['ads_period_max'].widget.attrs['placeholder'] = str(self.subscription.ads_period_max) if self.subscription else '-'
        self.fields['limit'].widget.attrs['placeholder'] = 'Лимит'

        self.channel_filter_keys = [
            'participants__gte',
            'participants__lte',
            'views__gte',
            'views__lte',
            'er__gte',
            'er__lte',
            'lang_code',
        ]

    participants__gte = forms.IntegerField(label='Подписчиков От', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '0'}))
    participants__lte = forms.IntegerField(label='Подписчиков До', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '1 000 000'}))
    views__gte = forms.IntegerField(label='Просмотров От', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '0'}))
    views__lte = forms.IntegerField(label='Просмотров До', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '20 000'}))
    er__gte = forms.IntegerField(label='Вовлеченность От', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '0'}))
    er__lte = forms.IntegerField(label='Вовлеченность До', min_value=0, required=False, widget=forms.NumberInput(attrs={'placeholder': '100'}))

    ads_period_min = forms.IntegerField(label='Купили рекламу от (дней)', min_value=0, required=False)
    ads_period_max = forms.IntegerField(label='Купили рекламу до (дней)', min_value=0, required=False)

    limit = forms.IntegerField(label='Лимит', min_value=0, required=True)

    lang_code = forms.ChoiceField(label='Язык канала', choices=[('', 'Любой'), ('ru', 'Русский'), ('ua', 'Украинский')], required=False)


    def clean_ads_period_min(self):

        ads_period_min = self.cleaned_data.get('ads_period_min')

        if ads_period_min is None:
            ads_period_min = self.subscription.ads_period_min

        if ads_period_min < self.subscription.ads_period_min:
            ads_period_min = self.subscription.ads_period_min

        elif ads_period_min > self.subscription.ads_period_max:
            ads_period_min = self.subscription.ads_period_max

        return ads_period_min

    def clean_ads_period_max(self):

        ads_period_max = self.cleaned_data.get('ads_period_max')

        if ads_period_max is None:
            ads_period_max = self.subscription.ads_period_max

        if ads_period_max > self.subscription.ads_period_max:
            ads_period_max = self.subscription.ads_period_max

        elif ads_period_max < self.subscription.ads_period_min:
            ads_period_max = self.subscription.ads_period_min

        return ads_period_max
