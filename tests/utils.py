def unregister_all_models():
    """
    For testing only
    """
    from ormlite.orm import Context

    Context.MODEL_TO_TABLE = dict()
    Context.TABLE_TO_MODEL = dict()
