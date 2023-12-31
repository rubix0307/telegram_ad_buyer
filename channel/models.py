from django.db import models

from user.models import CustomUser


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)
    link_telemetr = models.URLField()
    is_show = models.BooleanField(default=False)

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.title}'
    
    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'category'


class Manager(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    link_avatar = models.TextField(max_length=500, null=True)
    link_tg = models.TextField(max_length=500)

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.username}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'manager'


class Advertisement(models.Model):
    id = models.AutoField(primary_key=True)
    seller = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='ad_seller')
    buyer = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='buyer')
    date = models.DateTimeField()

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.seller.title}-{self.buyer.title}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'advertisement'


class Channel(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    link_tg = models.URLField()
    link_avatar = models.URLField()
    link_telemetr = models.URLField()
    description = models.TextField(null=True)
    participants = models.IntegerField(null=True)
    views = models.IntegerField(null=True)
    views24 = models.IntegerField(null=True)
    er = models.IntegerField(null=True)
    er24 = models.IntegerField(null=True)
    lang_code = models.CharField(max_length=5, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category)
    managers = models.ManyToManyField(Manager)
    advertisements = models.ForeignKey('Advertisement', on_delete=models.CASCADE, related_name='ad_seller', null=True)

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.title}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'channel'


class UserManagerHistory(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.user.email}-{self.manager.username}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'user_manager_history'
        ordering = ['user', 'category', 'date']


class UserBuyerHistory(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.user.email}-{self.manager.username}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'user_buyer_history'


