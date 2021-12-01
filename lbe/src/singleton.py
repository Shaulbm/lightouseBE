class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        # below is remarked as __init__ should be called only once
        # else:
        #     cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]