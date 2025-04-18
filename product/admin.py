from django.contrib import admin
from .models import Category, Product, Banner, Color, Brand
from django.core.exceptions import ValidationError
from django.forms import JSONField, ModelForm


class ProductAdminForm(ModelForm):
    """
    Форма для модели Product с проверкой количества характеристик.
    """
    main_characteristics = JSONField(
        required=False,
        help_text="Добавьте характеристики в формате JSON (не более 4)."
    )

    def clean_main_characteristics(self):
        main_characteristics = self.cleaned_data.get('main_characteristics', [])

        # Если main_characteristics не является списком, присваиваем пустой список
        if not isinstance(main_characteristics, list):
            main_characteristics = []

        if len(main_characteristics) > 4:
            raise ValidationError("Нельзя добавлять более 4 характеристик для одного товара.")

        # Преобразуем key в label
        for characteristic in main_characteristics:
            if "key" in characteristic:
                characteristic["label"] = characteristic.pop("key")

        return main_characteristics


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['title', 'category', 'price', 'quantity', 'is_active']
    fields = (
        'title',
        'image1',
        'image2',
        'image3',
        'image4',
        'image5',
        'category',
        'color',
        'price',
        'promotion',
        'wholesale_price',
        'wholesale_promotion',
        'brand',
        'quantity',
        'description',
        'main_characteristics',  # Используем новое поле
        'is_product_of_the_day',
        'is_active',
    )
    search_fields = ['title', 'category__name', 'brand__name']  # Добавлено для поиска
    list_filter = ['category', 'brand', 'is_active']  # Фильтры

    # Ограничиваем доступ к добавлению товаров через админку
    def has_add_permission(self, request):
        # Проверяем, что пользователь является администратором и имеет роль 'admin'
        return request.user.is_staff and getattr(request.user, 'role', '') == 'admin'

    def save_model(self, request, obj, form, change):
        """
        Проверка при сохранении из админки.
        """
        if len(obj.main_characteristics) > 4:
            raise ValidationError("Нельзя добавлять более 4 характеристик для одного товара.")

        # Убеждаемся, что в данных есть label вместо key
        for characteristic in obj.main_characteristics:
            if "key" in characteristic:
                characteristic["label"] = characteristic.pop("key")

        super().save_model(request, obj, form, change)


admin.site.register(Category)
admin.site.register(Banner)
admin.site.register(Color)
admin.site.register(Brand)
