class BaseListenerMixin:
    """Cooperative ``__declare_last__`` terminator for SQLAlchemy ORM listener mixins."""

    @classmethod
    def __declare_last__(cls) -> None:
        pass
