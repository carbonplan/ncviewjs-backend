from tortoise import fields, models


class Store(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255, unique=True)
    registered_at = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=255, default='queued')
    conclusion = fields.CharField(max_length=255, default=None)
    rechunked_url = fields.CharField(max_length=255, default=None)

    def __str__(self):
        return self.url
