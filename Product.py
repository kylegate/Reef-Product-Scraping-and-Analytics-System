class Product:
    def __init__(self, name, brand, sku, category, sale_price, old_price, option):
        self.name = name
        self.brand = brand
        self.sku = sku
        self.category = category
        self.sale_price = sale_price
        self.old_price = old_price
        self.option = option
    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"Brand: {self.brand}\n"
            f"SKU: {self.sku}\n"
            f"Category: {self.category}\n"
            f"Sale Price: {self.sale_price}\n"
            f"Non-Sale Price: {self.old_price}\n"
            f"Option: {self.option}\n"
        )
