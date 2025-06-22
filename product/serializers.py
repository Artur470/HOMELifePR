from rest_framework import serializers
from django.db.models import Avg
from .models import Product, Category, Color, Brand, Review, Banner
from .utils import round_to_nearest_half
from cloudinary.forms import CloudinaryFileField
from django.conf import settings
from cloudinary.models import CloudinaryField
from rest_framework import serializers
from .models import Product, Brand, Category, Color
import time
from rest_framework import serializers
from cloudinary.utils import cloudinary_url
from .models import Banner
class CategorySerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Category  # Обратите внимание, что вы используете модель Category, а не Brand
        fields = ['id','label', 'value']

    def get_value(self, obj):
        translation = {
            'холодильник': 'refrigerator',
            'стиральная машина': 'washing machine',
            'посудомоечная машина': 'dishwasher',
            'микроволновая печь': 'microwave',
            'телевизор': 'television',
            'пылесос': 'vacuum cleaner',
            'кондиционер': 'air conditioner',
            'печь': 'oven',
            'фен': 'hair dryer',
            'тостер': 'toaster',
            'кофеварка': 'coffee maker',
            'электрический чайник': 'electric kettle',
            'утюг': 'iron',
            'блендер': 'blender',
            'соковыжималка': 'juicer',
            'сушилка для белья': 'clothes dryer',
            'кухонный комбайн': 'food processor',
            'вентилятор': 'fan',
            'холодильная камера': 'cold storage',
            'водонагреватель': 'water heater',
            'мясорубка': 'meat grinder',
            'вафельница': 'waffle maker',
            'суповарка': 'soup maker',
            'электрическая духовка': 'electric oven',
            'мясопереработчик': 'meat slicer',
            'бассейн': 'pool',
            'система фильтрации воды': 'water filtration system',
            'кухонные весы': 'kitchen scale',
            'размораживатель': 'defroster',
            'хлебопечка': 'bread maker',
        }

        # Если значение value уже есть, возвращаем его
        if obj.value:
            return translation.get(obj.value, obj.value).lower()

        # Если value нет, присваиваем его на основе label
        return translation.get(obj.label, obj.label).lower()

    def create(self, validated_data):
        label = validated_data.get('label')

        # Словарь перевода
        translation = {
             'холодильник': 'refrigerator',
            'стиральная машина': 'washing machine',
            'посудомоечная машина': 'dishwasher',
            'микроволновая печь': 'microwave',
            'телевизор': 'television',
            'пылесос': 'vacuum cleaner',
            'кондиционер': 'air conditioner',
            'печь': 'oven',
            'фен': 'hair dryer',
            'тостер': 'toaster',
            'кофеварка': 'coffee maker',
            'электрический чайник': 'electric kettle',
            'утюг': 'iron',
            'блендер': 'blender',
            'соковыжималка': 'juicer',
            'сушилка для белья': 'clothes dryer',
            'кухонный комбайн': 'food processor',
            'вентилятор': 'fan',
            'холодильная камера': 'cold storage',
            'водонагреватель': 'water heater',
            'мясорубка': 'meat grinder',
            'вафельница': 'waffle maker',
            'суповарка': 'soup maker',
            'электрическая духовка': 'electric oven',
            'мясопереработчик': 'meat slicer',
            'бассейн': 'pool',
            'система фильтрации воды': 'water filtration system',
            'кухонные весы': 'kitchen scale',
            'размораживатель': 'defroster',
            'хлебопечка': 'bread maker',
        }

        # Присваиваем value на основе label
        validated_data['value'] = translation.get(label, label).lower()  # Сохраняем значение в нижнем регистре

        # Создаем объект модели
        return super().create(validated_data)


class ColorSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Color
        fields = ['label', 'value']

    def get_value(self, obj):
        # Словарь для перевода значений на английский
        translation = {
              'белый': 'white',
            'черный': 'black',
            'красный': 'red',
            'синий': 'blue',
            'зеленый': 'green',
            'желтый': 'yellow',
            'оранжевый': 'orange',
            'пурпурный': 'purple',
            'розовый': 'pink',
            'серый': 'gray',
            'коричневый': 'brown',
            'бежевый': 'beige',
            'фиолетовый': 'violet',
            'голубой': 'light blue',
            'бирюзовый': 'turquoise',
            'мятный': 'mint',
            'лавандовый': 'lavender',
            'гранатовый': 'pomegranate',
            'песочный': 'sand',
            'оливковый': 'olive',
            'малахитовый': 'malachite',
            'медный': 'copper',
            'слоновая кость': 'ivory',
            'золотой': 'gold ',
            'серебристый': 'silver',
        }

        # Проверяем, есть ли значение
        if obj.value:
            # Возвращаем значение на английском, если оно есть в словаре
            return translation.get(obj.value, obj.value)

        # Если значения нет, возвращаем значение на английском по label
        return translation.get(obj.label.lower(), obj.label.lower())

    def create(self, validated_data):
        label = validated_data.get('label').lower()

        # Словарь для перевода значений на английский
        translation = {
            'белый': 'white',
            'черный': 'black',
            'красный': 'red',
            'синий': 'blue',
            'зеленый': 'green',
            'желтый': 'yellow',
            'оранжевый': 'orange',
            'пурпурный': 'purple',
            'розовый': 'pink',
            'серый': 'gray',
            'коричневый': 'brown',
            'бежевый': 'beige',
            'фиолетовый': 'violet',
            'голубой': 'light blue',
            'бирюзовый': 'turquoise',
            'мятный': 'mint',
            'лавандовый': 'lavender',
            'гранатовый': 'pomegranate',
            'песочный': 'sand',
            'оливковый': 'olive',
            'малахитовый': 'malachite',
            'медный': 'copper',
            'слоновая кость': 'ivory',
            'золотой': 'gold ',
            'серебристый': 'silver',

        }

        # Присваиваем value на основе label
        validated_data['value'] = translation.get(label, label)

        return super().create(validated_data)

class BrandSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['label', 'value']

    def get_value(self, obj):
        translation = {
            'Acer': 'ACER',
            'Amazon': 'AMAZON',
            'Apple': 'APPLE',
            'Asus': 'ASUS',
            'Barnes & Noble': 'BARNES & NOBLE',
            'Blackberry': 'BLACKBERRY',
            'Bosch': 'BOSCH',
            'Bose': 'BOSE',
            'Canon': 'CANON',
            'Dell': 'DELL',
            'Denon': 'DENON',
            'Garmin': 'GARMIN',
            'Hewlett Packard': 'HEWLETT PACKARD',
            'Htc': 'HTC',
            'Lenovo': 'LENOVO',
            'LG': 'LG',
            'Microsoft': 'MICROSOFT',
            'Motorola': 'MOTOROLA',
            'Newegg': 'NEWEGG',
            'Nexus': 'NEXUS',
            'Nikon': 'NIKON',
            'Nokia': 'NOKIA',
            'Olloclip': 'OLLOCLIP',
            'Olympus': 'OLYMPUS',
            'Panasonic': 'PANASONIC',
            'Philips': 'PHILIPS',
            'Pioneer': 'PIONEER',
            'Radioshack': 'RADIOSHACK',
            'Ricoh': 'RICOH',
            'Samsung': 'SAMSUNG',
            'Sharp': 'SHARP',
            'Sony': 'SONY',
            'Tomtom': 'TOMTOM',
            'Toshiba': 'TOSHIBA',
            'Xbox': 'XBOX',
        }

        # Если значение value уже есть
        if obj.value:
            return translation.get(obj.value, obj.value).upper()

        # Если value нет, присваиваем его на основе label
        return translation.get(obj.label, obj.label).upper()

    def create(self, validated_data):
        label = validated_data.get('label')

        translation = {
            'Acer': 'ACER',
            'Amazon': 'AMAZON',
            'Apple': 'APPLE',
            'Asus': 'ASUS',
            'Barnes & Noble': 'BARNES & NOBLE',
            'Blackberry': 'BLACKBERRY',
            'Bosch': 'BOSCH',
            'Bose': 'BOSE',
            'Canon': 'CANON',
            'Dell': 'DELL',
            'Denon': 'DENON',
            'Garmin': 'GARMIN',
            'Hewlett Packard': 'HEWLETT PACKARD',
            'Htc': 'HTC',
            'Lenovo': 'LENOVO',
            'LG': 'LG',
            'Microsoft': 'MICROSOFT',
            'Motorola': 'MOTOROLA',
            'Newegg': 'NEWEGG',
            'Nexus': 'NEXUS',
            'Nikon': 'NIKON',
            'Nokia': 'NOKIA',
            'Olloclip': 'OLLOCLIP',
            'Olympus': 'OLYMPUS',
            'Panasonic': 'PANASONIC',
            'Philips': 'PHILIPS',
            'Pioneer': 'PIONEER',
            'Radioshack': 'RADIOSHACK',
            'Ricoh': 'RICOH',
            'Samsung': 'SAMSUNG',
            'Sharp': 'SHARP',
            'Sony': 'SONY',
            'Tomtom': 'TOMTOM',
            'Toshiba': 'TOSHIBA',
            'Xbox': 'XBOX',
        }

        # Присваиваем value на основе label
        validated_data['value'] = translation.get(label, label).upper()

        return super().create(validated_data)

    def create(self, validated_data):
        label = validated_data.get('label')
        value = validated_data.get('value', label)  # Используем label для определения value
        # Тут можно расширить логику при необходимости
        return super().create(validated_data)
class ReviewSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comments','created']

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    main_characteristics = serializers.JSONField()
    price = serializers.SerializerMethodField()
    promotion = serializers.SerializerMethodField()

    # Используем StringRelatedField для отображения label вместо id
    category = serializers.StringRelatedField()
    color = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'category',  # Теперь будет отображаться как label
            'color',  # Теперь будет отображаться как label
            'images',
            'price',
            'promotion',
            'brand',  # Теперь будет отображаться как label
            'quantity',
            'description',
            'is_product_of_the_day',
            'is_active',
            'main_characteristics',
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        images = [
            obj.image1.url if obj.image1 else None,
            obj.image2.url if obj.image2 else None,
            obj.image3.url if obj.image3 else None,
            obj.image4.url if obj.image4 else None,
            obj.image5.url if obj.image5 else None,
        ]
        return [request.build_absolute_uri(image) for image in images if image] if request else images

    def validate_main_characteristics(self, value):
        if value is None:
            value = []

        if not isinstance(value, list):
            raise serializers.ValidationError("Характеристики должны быть списком.")

        if len(value) > 4:
            raise serializers.ValidationError("Нельзя добавлять более 4 характеристик.")

        for characteristic in value:
            if not isinstance(characteristic, dict):
                raise serializers.ValidationError(
                    "Каждая характеристика должна быть объектом (ключ: значение).")
            if 'key' not in characteristic or 'value' not in characteristic:
                raise serializers.ValidationError("Каждая характеристика должна содержать ключ и значение.")
            if not isinstance(characteristic['key'], str):
                raise serializers.ValidationError("Ключ характеристики должен быть строкой.")
            if not isinstance(characteristic['value'], (str, int, float)):
                raise serializers.ValidationError(
                    "Значение характеристики должно быть строкой, числом или числом с плавающей точкой.")

        return value

    def get_price(self, obj):
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':
                return obj.wholesale_price if obj.wholesale_price else obj.price
        return obj.price

    def get_promotion(self, obj):
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':
                return obj.wholesale_promotion if obj.wholesale_promotion else obj.promotion
        return obj.promotion

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Обработка main_characteristics
        main_characteristics = representation.get('main_characteristics', [])
        if isinstance(main_characteristics, list):
            updated_characteristics = []
            for characteristic in main_characteristics:
                if 'key' in characteristic:
                    characteristic['label'] = characteristic.pop('key')
                updated_characteristics.append(characteristic)
            representation['main_characteristics'] = updated_characteristics

        # Условие для wholesaler
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            if user.role == 'wholesaler':
                representation['price'] = instance.wholesale_price if instance.wholesale_price else instance.price
                representation[ 'promotion'] = instance.wholesale_promotion if instance.wholesale_promotion else instance.promotion

        # Добавляем логику для поля color
        color_instance = getattr(instance, 'color', None)
        if color_instance:
            # Если `color` связано с другой моделью
            representation['color'] = color_instance.value  # value — поле на английском в модели Color
        else:
            # Если просто строковое поле
            representation['color'] = instance.color if instance.color else None

        return representation


class ProductShortSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'images',
            'avg_rating',
            'title',
            'price',
            'promotion',
            'is_active',
        ]

    def get_avg_rating(self, obj):
        if obj.reviews.exists():
            avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg_rating, 1) if avg_rating else 0
        return 0

    def get_images(self, obj):
        images = [
            obj.image1,
            obj.image2,
            obj.image3,
            obj.image4,
            obj.image5,
        ]
        return [image.build_url() for image in images if image]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            user = request.user
            if hasattr(user, 'role') and user.role == 'wholesaler':
                representation['price'] = instance.wholesale_price if instance.wholesale_price else instance.price
                representation['promotion'] = instance.wholesale_promotion if instance.wholesale_promotion else instance.promotion
            else:
                representation['price'] = instance.price
                representation['promotion'] = instance.promotion

        return representation


class ProductCreateSerializer(serializers.ModelSerializer):
    main_characteristics = serializers.JSONField(required=False)
    image1 = serializers.ImageField(required=False, allow_null=True)
    image2 = serializers.ImageField(required=False, allow_null=True)
    image3 = serializers.ImageField(required=False, allow_null=True)
    image4 = serializers.ImageField(required=False, allow_null=True)
    image5 = serializers.ImageField(required=False, allow_null=True)
    brand = serializers.SlugRelatedField(queryset=Brand.objects.all(), slug_field='value', required=True)
    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='value', required=True)
    color = serializers.SlugRelatedField(queryset=Color.objects.all(), slug_field='value', required=True)
    promotion = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'category',
            'color',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'price',
            'promotion',
            'wholesale_price',
            'wholesale_promotion',
            'brand',
            'quantity',
            'description',
            'is_product_of_the_day',
            'is_active',
            'main_characteristics',
        ]


    def create(self, validated_data):
        # Убедимся, что если promotion не передано, установим его в 0
        promotion = validated_data.get('promotion', 0)  # Если promotion не указано, установим 0
        validated_data['promotion'] = promotion  # Явно записываем значение promotion

        characteristics_data = validated_data.pop('main_characteristics', [])
        images_data = {key: validated_data.pop(key, None) for key in ['image1', 'image2', 'image3', 'image4', 'image5']}

        # Создаем продукт
        product = Product.objects.create(**validated_data)

        # Обработка изображений
        for key, value in images_data.items():
            if value:
                setattr(product, key, value)

        product.save()

        # Обработка характеристик продукта
        if characteristics_data:
            self._update_characteristics(product, characteristics_data)

        return product

    def update(self, instance, validated_data):
        # Проверяем и устанавливаем значение promotion, если оно не передано
        promotion = validated_data.get('promotion', 0)  # Если promotion не указано, установим 0
        validated_data['promotion'] = promotion  # Явно записываем значение promotion

        characteristics_data = validated_data.pop('main_characteristics', [])
        images_data = {key: validated_data.pop(key, None) for key in ['image1', 'image2', 'image3', 'image4', 'image5']}

        # Получаем значения для brand, category, color
        brand_value = validated_data.pop('brand', None)
        category_value = validated_data.pop('category', None)
        color_value = validated_data.pop('color', None)

        # Ищем объекты по значению 'value' и обновляем их
        if brand_value:
            instance.brand = self._get_or_create_object(Brand, brand_value, 'brand')
        if category_value:
            instance.category = self._get_or_create_object(Category, category_value, 'category')
        if color_value:
            instance.color = self._get_or_create_object(Color, color_value, 'color')

        # Обновление данных с помощью родительского метода
        instance = super().update(instance, validated_data)

        # Обработка изображений
        for key, value in images_data.items():
            if value:
                setattr(instance, key, value)

        instance.save()

        # Обработка характеристик продукта
        if characteristics_data:
            self._update_characteristics(instance, characteristics_data)

        return instance

    def _get_or_create_object(self, model, value, field_name):
        """Функция для поиска или создания объекта по значению value"""
        if value:
            try:
                obj = model.objects.get(value=value)
                return obj
            except model.DoesNotExist:
                raise serializers.ValidationError({
                    field_name: f"{model.__name__} with the specified value '{value}' does not exist."
                })
        return None

    def _update_characteristics(self, product, characteristics_data):
        """Обновление характеристик продукта в JSONField"""
        current_characteristics = product.main_characteristics or []
        characteristics_dict = {char['label']: char['value'] for char in current_characteristics}

        for char_data in characteristics_data:
            label = char_data.get('label')
            value = char_data.get('value')

            if label and value:
                characteristics_dict[label] = value

        product.main_characteristics = [{"label": label, "value": value} for label, value in characteristics_dict.items()]
        product.save()


class ReviewCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Review
        fields = ['id','product','rating','comments','created','updated',  'username',]



    def create(self, validated_data):
        # Добавляем текущего пользователя из запроса
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


from cloudinary.utils import cloudinary_url


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'image']

    def get_image(self, obj):
        # Обязательно возвращаем полный URL, а не относительный путь
        if obj.image:
            return obj.image.url
        return None