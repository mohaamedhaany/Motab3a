from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Order

# 1. شاشة المحاسب (فيها الإضافة، العرض، والأرشيف)
@login_required
def dashboard(request):
    # لو المستخدم مش ستاف (زي المدير مثلاً) اطرده على شاشة المدير
    if not request.user.is_staff:
        return redirect('manager_dashboard')

    # إضافة طلب جديد
    if request.method == "POST":
        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        date_requested = request.POST.get('date_requested')
        Order.objects.create(item_name=item_name, price=price, date_requested=date_requested)
        return redirect('dashboard')

    # جلب الطلبات المعلقة والأرشيف
    unsettled_orders = Order.objects.filter(is_settled=False).order_by('-date_requested')
    settled_orders = Order.objects.filter(is_settled=True).order_by('-date_requested')
    
    # حساب الإجمالي
    total_unsettled = unsettled_orders.aggregate(Sum('price'))['price__sum'] or 0

    return render(request, 'expenses/dashboard.html', {
        'unsettled_orders': unsettled_orders,
        'settled_orders': settled_orders,
        'total_unsettled': total_unsettled,
    })

# 2. شاشة المدير (للعرض والفلترة فقط - مفيهاش أي تعديل)
@login_required
def manager_dashboard(request):
    # استقبال التواريخ من الفلتر
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # جلب الطلبات
    unsettled = Order.objects.filter(is_settled=False)
    settled = Order.objects.filter(is_settled=True)

    # تطبيق الفلتر لو المدير حدد فترة
    if start_date:
        unsettled = unsettled.filter(date_requested__gte=start_date)
        settled = settled.filter(date_requested__gte=start_date)
    if end_date:
        unsettled = unsettled.filter(date_requested__lte=end_date)
        settled = settled.filter(date_requested__lte=end_date)

    # حساب الإجماليات
    total_unsettled = unsettled.aggregate(Sum('price'))['price__sum'] or 0
    total_settled = settled.aggregate(Sum('price'))['price__sum'] or 0

    context = {
        'unsettled_orders': unsettled.order_by('-date_requested'),
        'settled_orders': settled.order_by('-date_requested'),
        'total_unsettled': total_unsettled,
        'total_settled': total_settled,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'expenses/manager.html', context)

# 3. دالة التعديل (للمحاسب فقط)
@login_required
def edit_order(request, order_id):
    # حماية: لو مش ستاف ممنوع يعدل
    if not request.user.is_staff:
        return redirect('manager_dashboard')
    
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.item_name = request.POST.get('item_name')
        order.price = request.POST.get('price')
        order.date_requested = request.POST.get('date_requested')
        
        # لو علم على checkbox بتاع "تم الدفع" في صفحة التعديل
        order.is_settled = request.POST.get('is_settled') == 'on' 
        order.save()
        return redirect('dashboard')
        
    return render(request, 'expenses/edit_order.html', {'order': order})

# 4. دالة الحذف (للمحاسب فقط)
@login_required
def delete_order(request, order_id):
    # حماية: لو مش ستاف ممنوع يحذف
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
        order.delete()
    return redirect('dashboard')

# 5. دالة التسديد السريع من زرار الجدول (للمحاسب فقط)
@login_required
def settle_order(request, order_id):
    # حماية: لو مش ستاف ممنوع يسدد
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
        order.is_settled = True
        order.save()
    return redirect('dashboard')