def unregister_all_models():
    """
    For testing only
    """
    from ormlite import orm

    orm.MODEL_TO_TABLE = dict()
    orm.TABLE_TO_MODEL = dict()
