from products.models import ProductUnit


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault("cart", {})

    def save(self):
        self.session.modified = True

    def add(self, unit_id, quantity=1):
        unit_id = str(unit_id)

        if unit_id not in self.cart:
            self.cart[unit_id] = {
                "quantity": 0,
                "wholesale": False,
            }

        self.cart[unit_id]["quantity"] += quantity
        self.save()

    def set_quantity(self, unit_id, quantity):
        unit_id = str(unit_id)

        if quantity <= 0:
            self.remove(unit_id)
            return

        if unit_id not in self.cart:
            self.cart[unit_id] = {}

        self.cart[unit_id]["quantity"] = quantity
        self.save()

    def set_wholesale(self, unit_id, is_wholesale):
        unit_id = str(unit_id)

        if unit_id not in self.cart:
            return

        self.cart[unit_id]["wholesale"] = bool(is_wholesale)
        self.save()

    def increase(self, unit_id):
        unit_id = str(unit_id)

        if unit_id in self.cart:
            self.cart[unit_id]["quantity"] += 1
            self.save()

    def decrease(self, unit_id):
        unit_id = str(unit_id)

        if unit_id in self.cart:
            self.cart[unit_id]["quantity"] -= 1

            if self.cart[unit_id]["quantity"] <= 0:
                self.remove(unit_id)
            else:
                self.save()

    def remove(self, unit_id):
        unit_id = str(unit_id)

        if unit_id in self.cart:
            del self.cart[unit_id]
            self.save()

    def clear(self):
        self.cart = {}
        self.session["cart"] = {}
        self.save()

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def count_items(self):
        return len(self.cart)

    def get_items(self):
        unit_ids = self.cart.keys()

        units = (
            ProductUnit.objects
            .filter(pk__in=unit_ids)
            .select_related("product")
        )

        items = []

        for unit in units:
            uid = str(unit.pk)

            quantity = self.cart[uid].get("quantity") or (
                self.cart[uid].get("retail_qty", 0) + self.cart[uid].get("wholesale_qty", 0)
            )
            force_wholesale = self.cart[uid].get("wholesale", False)

            if force_wholesale and unit.wholesale_price:
                # العميل طلب حساب الجملة بنفسه، حتى لو الكمية أقل من حد الجملة
                subtotal = unit.wholesale_price * quantity
                is_wholesale = True
            else:
                subtotal = unit.get_price(quantity)
                is_wholesale = bool(
                    unit.wholesale_min_qty
                    and unit.wholesale_price
                    and quantity >= unit.wholesale_min_qty
                )

            items.append({
                "unit": unit,
                "quantity": quantity,
                "unit_price": subtotal / quantity,
                "subtotal": subtotal,
                "is_wholesale": is_wholesale,
                "wholesale_forced": force_wholesale,
            })

        return items

    def get_total(self):
        return sum(item["subtotal"] for item in self.get_items())
