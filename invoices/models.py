from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone_number = PhoneNumberField(blank=True)

    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,)

    def get_absolute_url(self):
        return reverse("client-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"Client: {self.first_name} {self.last_name}"


class Invoice(models.Model):

    title = models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    invoice_total = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, editable=False
    )
    create_date = models.DateField(auto_now_add=True)
    invoice_terms = models.TextField(
        blank=True,
        default="NET 30 Days. Finance Charge of 1.5% will be \
            made on unpaid balances after 30 days.",
    )

    class Meta:
        verbose_name: "Invoice"
        verbose_name_plural: "Invoices"  # noqa F821

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.title} - {self.invoice_total}"

    def __repr__(self):
        return f"<Invoice: {self.client} - {self.title}>"

    def get_invoice_total(self):
        total = 0
        total = sum([item.subtotal() for item in self.items.all()])
        return total

    def save(self, *args, **kwargs):
        self.invoice_total = self.get_invoice_total()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    # Invoice Line Items
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    item = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name: "Invoice Item"
        verbose_name_plural: "Invoice Items"

    def __str__(self):
        return f"{self.item} - {self.subtotal()}"

    def __repr__(self):
        return f"<Invoice Line Item: {self.item} - {self.subtotal()}>"

    def subtotal(self):
        return self.quantity * self.rate

    def save(self, *args, **kwargs):
        self.invoice.save()
        super().save(*args, **kwargs)
