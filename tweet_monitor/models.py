from django.db import models


class Hashtag(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Tweet(models.Model):
    provider_id = models.CharField(max_length=30, unique=True)
    text = models.CharField(max_length=150)
    owner = models.CharField(max_length=50)
    creation_date = models.DateTimeField()
    hashtags = models.ManyToManyField(Hashtag)

    def extract_hashtags(self):
        words = self.text.split()
        temp_list = [word for word in words if word[0] == "#"]

        for ht in temp_list:
            obj, created = Hashtag.objects.get_or_create(name=ht)
            self.hashtags.add(obj)

    def __str__(self):
        return "@{}: {} at {}".format(self.owner, self.text, self.creation_date)
