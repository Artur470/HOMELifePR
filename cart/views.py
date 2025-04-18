from django.shortcuts import render

# Create your views here.
from decimal import Decimal
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied
from django.utils.timezone import localtime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrderSerializer, ApplicationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum, F
from rest_framework.decorators import api_view
from product.models import Product
from .models import Cart, CartItem, Order
from .serializers import CartItemsSerializer

from .serializers import (OrderSummarySerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import  CartItem
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import   CartItem
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
import logging




logger = logging.getLogger(__name__)
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Получить список товаров в корзине пользователя.",
        responses={  # Описание возможных ответов
            200: openapi.Response(
                description="Список товаров в корзине пользователя",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'items': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID корзины"),
                                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Название товара"),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, description="URL изображения товара"),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество товара"),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Цена товара"),
                            },
                        )),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Общее количество товаров в корзине"),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Сумма без учета скидки"),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Итоговая стоимость товаров с учетом скидки"),
                    }
                ),
            ),
            404: openapi.Response(
                description="Корзина не найдена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            ),
        },
    )
    def get(self, request):
        user = request.user
        # Проверка роли через поле `role` у пользователя
        is_wholesale = user.role == 'wholesaler'  # Проверка, является ли пользователь оптовиком

        # Получаем корзину пользователя
        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        # Получаем товары в корзине и оптимизируем запросы
        queryset = CartItem.objects.filter(cart=cart).select_related('product')

        # Переменные для подсчета
        total_quantity = sum(item.quantity for item in queryset)
        subtotal = Decimal(0)  # Общая сумма без скидки
        total_price = Decimal(0)  # Итоговая стоимость с учетом скидки
        item_data_list = []  # Список для хранения данных о каждом товаре

        # Обрабатываем каждый элемент корзины
        for item in queryset:
            product = item.product
            product_price = Decimal(product.price)  # Обычная цена товара
            product_promotion = product.promotion  # Скидка товара, если есть

            # Если пользователь оптовик, используем оптовую цену и скидку
            if is_wholesale:
                product_price = Decimal(product.wholesale_price)  # Оптовая цена
                product_promotion = product.wholesale_promotion  # Оптовая скидка

            # Рассчитываем цену с учетом скидки
            if product_promotion:
                discounted_price = Decimal(product_promotion)  # Цена товара с учетом скидки
                price_to_return = discounted_price  # Цена с учетом скидки
            else:
                discounted_price = product_price  # Если скидки нет, используем обычную цену
                price_to_return = product_price  # Цена без скидки

            # Обновляем итоговые значения
            subtotal += product_price * item.quantity  # Сумма без скидки
            total_price += discounted_price * item.quantity  # Итоговая сумма с учетом скидки

            # Включаем цену с учетом скидки в сериализатор
            item_data = {
                'cart_id': cart.id,
                'product_id': product.id,
                'title': product.title,
                'image': product.image1.url if product.image1 else None,
                # Используйте image1 или другое поле изображения
                'quantity': item.quantity,
                'price': int(price_to_return),  # Преобразуем цену в float для JSON
            }
            item_data_list.append(item_data)

        # Сериализуем товары для ответа
        return Response({
            'items': item_data_list,
            'total_quantity': total_quantity,
            'subtotal': int(subtotal),  # Преобразуем Decimal в float для JSON ответа
            'totalPrice': int(total_price),
        })

    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Этот эндпоинт позволяет пользователю добавить товар в свою корзину. "
                              "Для этого нужно указать ID товара и его количество",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product:  id ': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара",
                                               required='product'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество товара",
                                           required='quantity'),
            },
        ),
        responses={
            201: openapi.Response(
                description="Товар добавлен в корзину",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                    'success': openapi.Schema(type=openapi.TYPE_STRING, description="Сообщение о результате операции"),
                }),
            ),
            400: openapi.Response(
                description="Ошибка при добавлении товара в корзину",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Сообщение об ошибке"),
                }),
            ),
        }
    )
    def post(self, request):
        data = request.data
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user, ordered=False)

        product = get_object_or_404(Product, id=data.get('product'))
        quantity = int(data.get('quantity', 1))

        if quantity <= 0:
            return Response({'error': 'Quantity must be greater than 0'}, status=400)

        if quantity > product.quantity:
            return Response({'error': 'Not enough stock available'}, status=400)

        # Calculate the price with promotion if applicable
        price = product.price
        promotion = product.promotion or 0
        if promotion > 0:
            price *= (1 - promotion / 100)

        # Get or create the CartItem
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'price': price, 'quantity': quantity, 'user': user}
        )

        if not created:
            # Update existing CartItem
            cart_item.quantity += quantity
            cart_item.price = price * cart_item.quantity
            cart_item.save()
        else:
            # Decrease product stock and save CartItem
            product.quantity -= quantity
            product.save()

        # Update cart total price
        cart.total_price = sum(item.price for item in CartItem.objects.filter(cart=cart))
        cart.save()

        return Response({'success': 'Item added to your cart'})

    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Обновить количество товара в корзине.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара в корзине"),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Новое количество товара", example=1),
            },
            required=['id', 'quantity']
        ),
        responses={
            200: openapi.Response(
                description="Товар обновлен успешно",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'items': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID корзины"),
                                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара"),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Название товара"),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, description="URL изображения товара"),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description="Количество товара"),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                        description="Цена товара"),
                            },
                        )),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                         description="Общее количество товаров в корзине"),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                   description="Сумма без учета скидки"),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                     description="Итоговая стоимость товаров с учетом скидки"),
                        'success': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="Сообщение об успешном обновлении товара"),
                    }
                ),
            ),
            400: openapi.Response(
                description="Неверное количество товара",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
            404: openapi.Response(
                description="Товар не найден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
        }
    )
    def put(self, request, *args, **kwargs):
        """
        Обновление количества товара в корзине.
        """
        # Получаем ID товара и новое количество из данных запроса
        product_id = request.data.get('id')
        new_quantity = int(request.data.get('quantity', 1))

        # Проверка корректности количества
        if new_quantity <= 0:
            return Response({'error': 'Invalid quantity. Quantity must be greater than 0.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Поиск элемента корзины
        cart_item = CartItem.objects.filter(cart__user=request.user, product__id=product_id).first()

        if not cart_item:
            return Response({'error': 'Product not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

        # Получаем текущее количество товара в корзине
        old_quantity = cart_item.quantity

        # Если количество в корзине изменилось, обновляем количество на складе
        if new_quantity < old_quantity:
            # Возвращаем разницу на склад
            cart_item.product.quantity += (old_quantity - new_quantity)
        elif new_quantity > old_quantity:
            # Проверяем наличие товара на складе
            if new_quantity > cart_item.product.quantity:
                return Response({'error': 'Not enough stock available.'}, status=status.HTTP_400_BAD_REQUEST)
            # Уменьшаем количество товара на складе
            cart_item.product.quantity -= (new_quantity - old_quantity)

        # Сохраняем изменения на складе
        cart_item.product.save()

        # Обновляем количество и цену товара в корзине
        product = cart_item.product
        if request.user.role == 'wholesaler':  # Если пользователь — оптовик
            base_price = product.wholesale_price
            promotion = product.wholesale_promotion
        else:  # Если пользователь — обычный клиент
            base_price = product.price
            promotion = product.promotion

        # Рассчитываем цену с учетом скидки
        if promotion and 0 <= promotion <= 100:
            price = base_price * (1 - (Decimal(promotion) / Decimal(100)))  # Применяем скидку
        else:
            price = base_price  # Если скидки нет или она некорректна, используем базовую цену

        # Проверка на отрицательную цену
        if price < 0:
            return Response({'error': 'Calculated price is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        # Обновляем количество и цену товара в корзине
        cart_item.quantity = new_quantity
        cart_item.price = round(price, 2)  # Сохраняем цену единицы товара с учетом скидки
        cart_item.save()

        # Пересчитываем общую стоимость корзины
        cart = cart_item.cart
        total_quantity = 0
        subtotal = Decimal(0)  # Сумма без скидки
        total_price = Decimal(0)  # Сумма с учетом скидки

        # Пересчитываем все товары в корзине
        for item in cart.items.all():  # Используем related_name 'items'
            # Получаем базовую цену и скидку в зависимости от роли пользователя
            if request.user.role == 'wholesaler':
                item_base_price = item.product.wholesale_price
                item_promotion = item.product.wholesale_promotion
            else:
                item_base_price = item.product.price
                item_promotion = item.product.promotion

            # Рассчитываем цену с учетом скидки
            if item_promotion and 0 <= item_promotion <= 100:
                item_price_with_discount = item_base_price * (1 - Decimal(item_promotion) / Decimal(100))
            else:
                item_price_with_discount = item_base_price

            # Обновляем цену товара в корзине
            item.price = round(item_price_with_discount, 2)
            item.save()

            # Добавляем к общей стоимости
            total_quantity += item.quantity
            subtotal += item_base_price * item.quantity  # Сумма без скидок (базовая цена * количество)
            total_price += promotion * item.quantity  # Сумма с учетом скидки (цена с скидкой * количество)

        # Обновляем данные корзины
        cart.total_quantity = total_quantity
        cart.subtotal = round(subtotal, 2)  # Стоимость без скидок
        cart.total_price = round(total_price, 2)  # Стоимость с учетом скидок
        cart.save()

        # Возвращаем обновленные данные корзины
        return Response({
            'items': CartItemsSerializer(cart.items.all(), many=True, context={'request': request}).data,
            'total_quantity': cart.total_quantity,
            'subtotal': round(cart.subtotal, 2),  # Стоимость без скидок
            'totalPrice': round(cart.total_price, 2),  # Стоимость с учетом скидок
            'success': 'Product updated successfully'
        })

    @swagger_auto_schema(
        tags=['cart'],
        operation_description="Удалить товар из корзины по ID товара.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID товара для удаления из корзины"),
            },
            required=['id']
        ),
        responses={
            204: openapi.Response(
                description="Товар успешно удален из корзины",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'items': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING),
                                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                                }
                            )
                        ),
                        'total_quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'subtotal': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                    }
                ),
            ),
            404: openapi.Response(
                description="Товар не найден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, description="Ошибка")}
                )
            ),
        }
    )
    # views.py
    def delete(self, request):
        data = request.data
        user = request.user
        product_id = data.get('id')

        # Получаем корзину пользователя
        cart = Cart.objects.filter(user=user, ordered=False).first()

        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        try:
            # Находим товар в корзине по product_id
            cart_item = CartItem.objects.get(cart=cart, product__id=product_id)

            # Возвращаем количество товара обратно на склад
            cart_item.product.quantity += cart_item.quantity
            cart_item.product.save()

            # Удаляем товар из корзины
            cart_item.delete()

        except CartItem.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        # Пересчитываем общую стоимость корзины после удаления товара
        cart.total_price = sum(item.price * item.quantity for item in CartItem.objects.filter(cart=cart))
        cart.save()

        return Response({
            'message': 'Delete successful',  # Сообщение о успешном удалении
            'total_quantity': sum(item.quantity for item in CartItem.objects.filter(cart=cart)),
            # Общее количество товаров в корзине
            'subtotal': cart.total_price,  # Общая стоимость
        }, status=204)


def send_order_notification(order, cart):
    subject = "Новый заказ на сайте Homelife"
    items_message = "Список товаров!\n"
    total_quantity = 0
    for item in cart.items.all():
        total_quantity += item.quantity

        product = item.product

        items_message += f"""
    Товар: {product.title}  
    Изображение: {product.image1.url if product.image1 else 'Изображение не доступно'}  
    Количество: {item.quantity}
    Цена: {item.price}c
    Общая стоимость: {item.price * item.quantity}c
    """


    message = f"""
    Заказ №{order.id}
   Дата заказа: {localtime(order.created_at).strftime("%Y-%m-%d %H:%M")}

    Email пользователя: {order.user.email}
    Имя пользователя: {order.user.username}
    Телефон пользователя: {order.user.number}
    Адрес: {order.address}
    """


    if order.by_card:
        message += "Онлайн оплата: Да\n"
    if order.by_cash:
        message += "Оплата наличными через курьера: Да\n"


    message += f"\n{items_message}"


    message += f"""
    Итог:
    Подитоговая сумма без скидки: {cart.subtotal}c
    Итоговая сумма с учетом скидки: {cart.total_price}c
    Количество товаров: {total_quantity}
    """


    admin_email = "homelife.site.kg@gmail.com"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )
    order.application = True
    order.save(update_fields=["application"])



class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=['order'],
        operation_description="Создание заказа для пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['address', 'by_card', 'by_cash'],
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Адрес доставки'),
                'by_card': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Оплата картой'),
                'by_cash': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Оплата наличными'),
            }
        ),
        responses={
            201: openapi.Response(
                description="Заказ успешно создан",
                examples={
                    'application/json': {
                        'message': 'Order created successfully',
                        'order_id': 123,
                        'address': '123 Main Street',
                        'by_card': True,
                        'by_cash': False,
                        'created_at': '14:30:00 14-02-2025'
                    }
                },
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                examples={
                    'application/json': {
                        'error': 'Все поля обязательны'
                    }
                }
            ),
            404: openapi.Response(
                description="Корзина не найдена",
                examples={
                    'application/json': {
                        'error': 'Cart not found'
                    }
                }
            ),
            401: openapi.Response(description="Ошибка авторизации"),
            500: openapi.Response(description="Ошибка сервера")
        }
    )
    def post(self, request):
        user = request.user
        data = request.data

        address = data.get('address')
        by_card = data.get('by_card')
        by_cash = data.get('by_cash')

        if not address or by_card is None or by_cash is None:
            return Response({'error': 'Все поля обязательны'}, status=400)

        if by_card and by_cash:
            return Response({'error': "Only one of 'by_card' or 'by_cash' can be True."}, status=400)

        if not by_card and not by_cash:
            return Response({'error': "At least one of 'by_card' or 'by_cash' must be True."}, status=400)

        # Получаем корзину пользователя, которая ещё не была оформлена
        cart = Cart.objects.filter(user=user, ordered=False).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=404)

        # Обновляем итоговую стоимость корзины перед созданием заказа
        cart.update_totals()  # Важно обновить итоги, чтобы получить актуальную цену

        # Создаём заказ с привязкой к корзине
        order = Order.objects.create(
            user=user,
            address=address,
            by_card=by_card,
            by_cash=by_cash,
            cart=cart,  # Привязываем корзину к заказу
            ordered=True  # Теперь заказ оформлен
        )

        # Обновляем статус корзины
        cart.ordered = True
        cart.save()

        # Формируем список продуктов для заказа
        products = []
        for item in cart.items.all():  # Используем related_name='items'
            product = item.product
            product_data = {
                'title': product.title,  # Правильный ключ без кавычек
                'quantity': item.quantity,
                'productTotalPrice': product.price * item.quantity
            }
            products.append(product_data)

        # Отправка уведомления о заказе (по необходимости)
        send_order_notification(order, cart)

        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'address': order.address,
            'by_card': order.by_card,
            'by_cash': order.by_cash,
            'totalPrice': cart.total_price,  # Передаем актуальную стоимость корзины
            'created_at': order.created_at.strftime("%H:%M:%S %d-%m-%Y"),
            'products': products  # Добавляем список товаров
        }, status=201)

class ApplicationListView(APIView):
    serializer_class = ApplicationSerializer

    @swagger_auto_schema(
        operation_description="Получить все заявленные заказы, где заказ оформлен и успешно завершен. Также возвращает список товаров в корзине каждого заказа с их количеством и общей стоимостью.",
        responses={
            200: openapi.Response(
                description="Список заявок с деталями товаров",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID заказа'),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
                            'role': openapi.Schema(type=openapi.TYPE_STRING, description='Роль пользователя'),
                            'payment_method': openapi.Schema(type=openapi.TYPE_STRING, description='Метод оплаты'),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, description='Дата создания заказа'),
                            'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT,
                                                         description='Общая стоимость заказа'),
                            'products': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'product_title': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='Название товара'),
                                        'quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                   description='Количество товара'),
                                        'productTotalPrice': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                            format=openapi.FORMAT_FLOAT,
                                                                            description='Общая стоимость товара (с учетом количества и скидок)')
                                    }
                                )
                            )
                        }
                    )
                )
            ),
            400: "Неверные параметры запроса",
            404: "Заявки не найдены"
        }
    )

    def get(self, request):
        # Получаем заказанные заявки (где ordered=True и application=True)
        applications = self.get_queryset()
        serializer = self.serializer_class(applications, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Фильтруем заказы по полям ordered и application"""
        return Order.objects.filter(ordered=True, application=True).order_by('-id')
