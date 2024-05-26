from django.db.models.fields.reverse_related import ManyToManyRel


def get_model_fields(model_class, name_only=True):
    """获取模型的字段信息"""

    model_fields = model_class._meta.get_fields()
    if name_only:
        return [f.name for f in model_fields if not isinstance(f, ManyToManyRel)]

    return model_fields
