from tortoise import fields, models


class Store(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255, unique=True)
    status = fields.CharField(max_length=255, null=True)
    conclusion = fields.CharField(max_length=255, null=True)
    rechunked_url = fields.CharField(max_length=255, null=True)
    registered_at = fields.DatetimeField(auto_now_add=True)
    last_accessed_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.url
