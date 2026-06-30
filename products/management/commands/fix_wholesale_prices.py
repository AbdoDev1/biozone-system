from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import ProductUnit


# نسبة خصم جملة افتراضية معقولة لو محتاجين نولّد سعر جملة من الصفر
DEFAULT_WHOLESALE_DISCOUNT = Decimal('0.15')   # 15% أرخص من القطاعي
DEFAULT_WHOLESALE_MIN_QTY = 20                 # حد أدنى افتراضي معقول للجملة


def round_price(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Command(BaseCommand):
    help = (
        'يفحص كل وحدات المنتجات، ويصلّح أي سعر جملة معكوس (أكبر من أو يساوي سعر '
        'القطعة) أو ناقص رغم وجود حد أدنى للجملة، بأسعار افتراضية منطقية تجاريًا '
        '(خصم 15% تقريبًا). الأسعار السليمة أصلًا متتلمسش.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='يعرض اللي هيتغير من غير ما يحفظ فعليًا في قاعدة البيانات.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        units = ProductUnit.objects.select_related('product').all()

        fixed = []

        with transaction.atomic():
            for unit in units:
                problem = None

                if unit.wholesale_price is not None and unit.wholesale_price >= unit.unit_price:
                    problem = 'معكوس'
                elif unit.wholesale_min_qty and not unit.wholesale_price:
                    problem = 'ناقص'

                if not problem:
                    continue

                old_price = unit.wholesale_price
                old_min_qty = unit.wholesale_min_qty

                new_price = round_price(unit.unit_price * (1 - DEFAULT_WHOLESALE_DISCOUNT))
                new_min_qty = unit.wholesale_min_qty or DEFAULT_WHOLESALE_MIN_QTY

                fixed.append(
                    f'{unit.product.display_name} — {unit.name}: '
                    f'[{problem}] سعر الجملة {old_price} -> {new_price}، '
                    f'الحد الأدنى {old_min_qty} -> {new_min_qty} '
                    f'(سعر القطعة {unit.unit_price})'
                )

                if not dry_run:
                    unit.wholesale_price = new_price
                    unit.wholesale_min_qty = new_min_qty
                    unit.full_clean()
                    unit.save()

            if dry_run:
                # نلغي أي حفظ تم لو كان dry-run (مفيش فعليًا لأننا منعناه فوق، احتياطًا بس)
                transaction.set_rollback(True)

        if not fixed:
            self.stdout.write(self.style.SUCCESS('كل أسعار الجملة سليمة، مفيش حاجة محتاجة تصليح.'))
            return

        self.stdout.write(self.style.WARNING(f'{"(تجربة بدون حفظ) " if dry_run else ""}تم رصد {len(fixed)} وحدة محتاجة تصليح:'))
        for line in fixed:
            self.stdout.write(f'  - {line}')

        if not dry_run:
            self.stdout.write(self.style.SUCCESS('تم الحفظ في قاعدة البيانات.'))
        else:
            self.stdout.write(self.style.WARNING('شغّل الأمر من غير --dry-run عشان يتحفظ فعليًا.'))
