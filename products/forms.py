from django import forms
from .models import Product, ProductUnit, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name_ar', 'name_en', 'manufacturer', 'description', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400'
            }),
            'name_ar': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': 'اسم المنتج بالعربي'
            }),
            'name_en': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': 'Product name in English'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': 'الشركة المصنعة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'rows': 3,
                'placeholder': 'وصف المنتج (اختياري)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'accent-blue-600'
            }),
        }
        labels = {
            'category': 'القسم',
            'name_ar': 'الاسم بالعربي',
            'name_en': 'الاسم بالإنجليزي',
            'manufacturer': 'الشركة المصنعة',
            'description': 'الوصف',
            'image': 'صورة المنتج',
            'is_active': 'نشط',
        }


class ProductUnitForm(forms.ModelForm):
    initial_stock = forms.IntegerField(
        min_value=0,
        initial=0,
        required=False,
        label='الكمية الابتدائية',
        widget=forms.NumberInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
            'placeholder': '0'
        })
    )

    class Meta:
        model = ProductUnit
        fields = ['size', 'name', 'qty_in_small', 'unit_price', 'wholesale_min_qty', 'wholesale_price', 'wholesale_mode']
        widgets = {
            'size': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': 'مثال: علبة، قطعة، كرتونة'
            }),
            'qty_in_small': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': '0.00'
            }),
            'wholesale_min_qty': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': '0'
            }),
            'wholesale_price': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400',
                'placeholder': '0.00'
            }),
            'wholesale_mode': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-blue-400'
            }),
        }
        labels = {
            'size': 'الحجم',
            'name': 'اسم الوحدة',
            'qty_in_small': 'الكمية في الوحدة الصغرى',
            'unit_price': 'سعر القطعة',
            'wholesale_min_qty': 'أقل كمية للجملة',
            'wholesale_price': 'سعر الجملة',
            'wholesale_mode': 'طريقة الجملة',
        }
