from django.contrib import admin
from .models import Product, CustomUser, Category


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'get_category_name')
    list_filter = ('category_id',)

    def get_category_name(self, obj):
        return obj.category_id.name
    get_category_name.short_description = 'Category'


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
