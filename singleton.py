class Singleton:
   def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance