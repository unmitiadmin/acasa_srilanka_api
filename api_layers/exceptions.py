class NoRasterDataException(Exception):
    def __init__(self, message="No data available for the selected inputs in this region"):
        self.message = message
        super().__init__(self.message)


class LayerDataException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RasterFileNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
