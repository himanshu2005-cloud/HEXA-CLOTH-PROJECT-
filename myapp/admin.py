from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from django.contrib.admin import AdminSite
from django.db.models import Sum
from .models import Addproduct, Addcart, Payment, Wishlist


class AddproductForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[('Men','Men'),('Women','Women'),('Kids','Kids')])

    class Meta:
        model = Addproduct
        fields = '__all__'

@admin.register(Addproduct)
class AddproductAdmin(admin.ModelAdmin):
    form = AddproductForm
    list_display = (
        'id', 'thumb', 'product_name', 'category', 'product_offerprice', 'product_price', 'edit_link'
    )
    search_fields = ('product_name', 'category')
    list_filter = ('category',)
    ordering = ('-id',)
    list_per_page = 25
    list_display_links = ('product_name', 'thumb')
    readonly_fields = ('preview',)
    fieldsets = (
        (None, {
            'fields': ('product_name', 'product_description', 'category')
        }),
        ('Pricing', {
            'fields': ('product_price', 'product_offerprice')
        }),
        ('Media', {
            'fields': ('image', 'preview')
        }),
    )

    def thumb(self, obj):
        return format_html('<img src="{}" width="48" height="48" style="object-fit:cover;border-radius:6px;" />', obj.image.url) if obj.image else ''

    def preview(self, obj):
        return format_html('<img src="{}" width="160" style="object-fit:cover;border-radius:8px;" />', obj.image.url) if obj.image else ''

    thumb.short_description = 'Image'
    preview.short_description = 'Preview'

    def edit_link(self, obj):
        url = reverse('admin:myapp_addproduct_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Edit</a>', url)

    edit_link.short_description = 'Edit'

    def save_model(self, request, obj, form, change):
        if obj.category:
            obj.category = obj.category.strip().title()
        super().save_model(request, obj, form, change)


@admin.register(Addcart)
class AddcartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'thumb', 'username', 'producti_name', 'producti_category', 'producti_qty', 'totalprice'
    )
    search_fields = ('username', 'producti_name', 'producti_category')
    list_filter = ('producti_category',)
    ordering = ('-id',)
    list_per_page = 25

    def thumb(self, obj):
        return format_html('<img src="{}" width="48" height="48" style="object-fit:cover;border-radius:6px;" />', obj.image.url) if obj.image else ''

    thumb.short_description = 'Image'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fullname', 'email', 'phone', 'payment_mode', 'amount'
    )
    search_fields = ('firstname', 'lastname', 'email', 'payment_mode')
    list_filter = ('payment_mode',)
    ordering = ('-id',)
    list_per_page = 25

    def fullname(self, obj):
        return f"{obj.firstname} {obj.lastname}"

    fullname.short_description = 'Name'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'thumb', 'username', 'product_name', 'product_category', 'product_offerprice'
    )
    search_fields = ('username', 'product_name', 'product_category')
    list_filter = ('product_category',)
    ordering = ('-id',)
    list_per_page = 25

    def thumb(self, obj):
        return format_html('<img src="{}" width="48" height="48" style="object-fit:cover;border-radius:6px;" />', obj.product_image.url) if obj.product_image else ''

    thumb.short_description = 'Image'

class HexaAdminSite(AdminSite):
    site_header = 'Hexashop Admin'
    site_title = 'Hexashop Admin'
    index_title = 'Administration'
    index_template = 'admin/custom_index.html'

    def each_context(self, request):
        ctx = super().each_context(request)
        try:
            orders_count = Payment.objects.count()
            products_count = Addproduct.objects.count()
            # Payment.amount is CharField, coerce to int where possible
            total_sales = 0
            for p in Payment.objects.all().only('amount'):
                try:
                    total_sales += int(str(p.amount).strip())
                except (ValueError, TypeError):
                    continue
            ctx.update({
                'total_sales': total_sales,
                'orders_count': orders_count,
                'products_count': products_count,
            })
        except Exception:
            pass
        return ctx

hexa_admin_site = HexaAdminSite(name='hexa_admin')

# Register models on custom admin site
hexa_admin_site.register(Addproduct, AddproductAdmin)
hexa_admin_site.register(Addcart, AddcartAdmin)
hexa_admin_site.register(Payment, PaymentAdmin)
hexa_admin_site.register(Wishlist, WishlistAdmin)
