from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TicketSoporteForm, MensajeSoporteForm
from .models import TicketSoporte


@login_required
def mis_tickets(request):
    if request.user.es_admin_traiber:
        tickets = TicketSoporte.objects.select_related('usuario').all()
    else:
        tickets = TicketSoporte.objects.filter(usuario=request.user)
    return render(request, 'soporte/mis_tickets.html', {'tickets': tickets})


@login_required
def crear_ticket(request):
    if request.method == 'POST':
        form = TicketSoporteForm(request.POST, usuario=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.usuario = request.user
            ticket.save()
            messages.success(request, 'Tu ticket fue creado. Te responderemos pronto.')
            return redirect('soporte:ver_ticket', ticket_id=ticket.id)
    else:
        form = TicketSoporteForm(usuario=request.user)
    return render(request, 'soporte/crear_ticket.html', {'form': form})


@login_required
def ver_ticket(request, ticket_id):
    ticket = get_object_or_404(TicketSoporte, pk=ticket_id)
    if ticket.usuario != request.user and not request.user.es_admin_traiber:
        return redirect('soporte:mis_tickets')

    if request.method == 'POST':
        form = MensajeSoporteForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.ticket = ticket
            mensaje.autor = request.user
            mensaje.es_staff = request.user.es_admin_traiber
            mensaje.save()
            if request.user.es_admin_traiber and ticket.estado == TicketSoporte.Estado.ABIERTO:
                ticket.estado = TicketSoporte.Estado.EN_PROCESO
                ticket.save(update_fields=['estado'])
            return redirect('soporte:ver_ticket', ticket_id=ticket.id)
    else:
        form = MensajeSoporteForm()

    return render(request, 'soporte/ver_ticket.html', {
        'ticket': ticket, 'mensajes': ticket.mensajes.select_related('autor'), 'form': form,
    })


@login_required
def cambiar_estado_ticket(request, ticket_id, estado):
    if not request.user.es_admin_traiber:
        return redirect('soporte:mis_tickets')
    ticket = get_object_or_404(TicketSoporte, pk=ticket_id)
    if estado in TicketSoporte.Estado.values:
        ticket.estado = estado
        ticket.save(update_fields=['estado'])
    return redirect('soporte:ver_ticket', ticket_id=ticket.id)
