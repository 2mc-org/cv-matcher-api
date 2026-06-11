from app.core.fields.created_at import CreatedAtField
from app.core.fields.id import IdField
from app.core.fields.updated_at import UpdatedAtField


class BaseFields(IdField, CreatedAtField, UpdatedAtField):
    pass
