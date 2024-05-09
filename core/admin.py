from django.contrib import admin
from .models import Category, Product, CartItem, CustomUser, Order, Favorite, OrderItem

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')

admin.site.register(CartItem, CartItemAdmin)
admin.site.register(CustomUser)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Favorite)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'address', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'address', 'phone']
    actions = ['accept_orders', 'reject_orders']
    inlines = [OrderItemInline]

    def accept_orders(self, request, queryset):
        queryset.update(status='Accepted')
    accept_orders.short_description = "Accept selected orders"

    def reject_orders(self, request, queryset):
        queryset.update(status='Rejected')
    reject_orders.short_description = "Reject selected orders"

admin.site.register(Order, OrderAdmin)