from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Order, AdvancePayment

# 1. شاشة المحاسب
@login_required
def dashboard(request):
    if not request.user.is_staff:
        return redirect('manager_dashboard')

    if request.method == "POST":
        if 'add_order' in request.POST:
            item_name = request.POST.get('item_name')
            price = request.POST.get('price')
            date_requested = request.POST.get('date_requested')
            Order.objects.create(item_name=item_name, price=price, date_requested=date_requested)
        
        elif 'add_advance' in request.POST:
            amount = request.POST.get('amount')
            date_received = request.POST.get('date_received')
            note = request.POST.get('note', '')
            AdvancePayment.objects.create(amount=amount, date_received=date_received, note=note)
            
        return redirect('dashboard')

    # التعديل هنا: الترتيب بالتاريخ الأحدث، ثم السعر الأغلى
    unsettled_orders = Order.objects.filter(is_settled=False).order_by('-date_requested', '-price')
    advances = AdvancePayment.objects.filter(is_settled=False).order_by('-date_received', '-amount')
    settled_orders = Order.objects.filter(is_settled=True).order_by('-date_requested', '-price')
    
    total_unsettled = unsettled_orders.aggregate(Sum('price'))['price__sum'] or 0
    total_advance = advances.aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_advance - total_unsettled

    return render(request, 'expenses/dashboard.html', {
        'unsettled_orders': unsettled_orders,
        'settled_orders': settled_orders,
        'advances': advances,
        'total_unsettled': total_unsettled,
        'total_advance': total_advance,
        'net_balance': net_balance,
    })

# 2. شاشة المدير 
@login_required
def manager_dashboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    unsettled = Order.objects.filter(is_settled=False)
    settled = Order.objects.filter(is_settled=True)
    advances = AdvancePayment.objects.filter(is_settled=False)

    if start_date:
        unsettled = unsettled.filter(date_requested__gte=start_date)
        settled = settled.filter(date_requested__gte=start_date)
        advances = advances.filter(date_received__gte=start_date)
    if end_date:
        unsettled = unsettled.filter(date_requested__lte=end_date)
        settled = settled.filter(date_requested__lte=end_date)
        advances = advances.filter(date_received__lte=end_date)

    total_unsettled = unsettled.aggregate(Sum('price'))['price__sum'] or 0
    total_settled = settled.aggregate(Sum('price'))['price__sum'] or 0
    total_advance = advances.aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_advance - total_unsettled

    # التعديل هنا برضه: الترتيب المزدوج
    context = {
        'unsettled_orders': unsettled.order_by('-date_requested', '-price'),
        'settled_orders': settled.order_by('-date_requested', '-price'),
        'advances': advances.order_by('-date_received', '-amount'),
        'total_unsettled': total_unsettled,
        'total_settled': total_settled,
        'total_advance': total_advance,
        'net_balance': net_balance,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'expenses/manager.html', context)

# 3. دالة تقفيل الأسبوع وتصفير الحساب
@login_required
def close_period(request):
    if request.user.is_staff:
        Order.objects.filter(is_settled=False).update(is_settled=True)
        AdvancePayment.objects.filter(is_settled=False).update(is_settled=True)
    return redirect('dashboard')

# 4. باقي الدوال (تعديل، مسح، تسديد فردي)
@login_required
def edit_order(request, order_id):
    if not request.user.is_staff:
        return redirect('manager_dashboard')
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.item_name = request.POST.get('item_name')
        order.price = request.POST.get('price')
        order.date_requested = request.POST.get('date_requested')
        order.is_settled = request.POST.get('is_settled') == 'on' 
        order.save()
        return redirect('dashboard')
    return render(request, 'expenses/edit_order.html', {'order': order})

@login_required
def delete_order(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
        order.delete()
    return redirect('dashboard')

@login_required
def settle_order(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
        order.is_settled = True
        order.save()
    return redirect('dashboard')