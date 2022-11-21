from tortoise import fields, models


class Store(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255, unique=True)
    registered_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=255, default='queued')
    conclusion = fields.CharField(max_length=255, null=True)
    rechunked_url = fields.CharField(max_length=255, null=True)

    def __str__(self):
        return self.url
