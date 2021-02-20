from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView
from django.http import HttpResponse

from .forms import ProductManagementForm
from apps.main.refectories.models import Refectory
from apps.main.products.models import Product
from apps.main.product_managements.models import ProductManagement


class ProductManagementListView(ListView):
    template_name = "product_managements/product_management_list.html"
    queryset = ProductManagement.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object_list'] = []
        context['refectory_data'] = []

        refectory = Refectory.objects.get(id=self.kwargs['pk'])
        product = Product.objects.filter(refectory=refectory.id).order_by('created')
        

        for j in product:
            query = ProductManagement.objects.filter(product_cod=j).order_by('created')
            
            for i in query:
                context['object_list'].append({
                        'id':i.id,
                        'product_name':j.product_name,
                        'operation_type':i.operation_type,
                        'product_quantity':i.product_quantity,
                        'product_unitary_amount':i.product_unitary_amount,
                        'product_total_amount':i.product_total_amount,
                        'created': i.created,
                        'created_by':i.created_by.profile.name,
                })
        try:
            context['refectory_data'].append({
                'id':refectory.id,
                'refectory_name': refectory.name,
                'refectory_address': refectory.address,
                })
        except:
            pass
        return context 


# class ProductManagementListSingleView(ListView):
#     template_name = "product_managements/product_management_list.html"
#     queryset = ProductManagement.objects.all()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         product = Product.objects.get(id=self.kwargs['pk'])
#         query = ProductManagement.objects.filter(product=product).order_by('created')
        
#         context['object_list'] = []
#         context['refectory_data'] = []

#         for i in query:
            
#             context['object_list'].append({
#                     'id':i.id,
#                     'product_name':i.product.product_name,
#                         'operation_type':i.operation_type,
#                         'product_quantity':i.product_quantity,
#                         'product_unitary_amount':i.product_unitary_amount,
#                         'product_total_ammount':i.product_total_amount,
#                         'created_by':i.created_by.profile.name,
#             })

#         context['refectory_data'].append({
#             'id':product.refectory.id,
#             'refectory_name': product.refectory.name,
#             'refectory_address': product.refectory.address,
#             })
#         return context 

class ProductManagementCreateView(CreateView):
    model = ProductManagement
    queryset = ProductManagement.objects.all()
    form_class = ProductManagementForm
    template_name = "product_managements/product_management_create.html"

    def get_success_url(self):
        success_url = reverse('dashboard:products:list_maintenance_product',kwargs={'pk':self.kwargs['pk']}) 
        return success_url

    def get_context_data(self, **kwargs):
        context = super(ProductManagementCreateView, self).get_context_data(**kwargs)
        query = Product.objects.filter(refectory_id=self.kwargs['pk']).order_by('product_name')

        context['product_info'] = []
        for i in query:
            context['product_info'].append({
                'product_name': i.product_name,
            })

        context['refectory'] = {
            'id' : self.kwargs['pk'],
        }
        return context 

    def post(self, request, *args, **kwargs):

        self.object = None
        form = self.get_form()
        product, created = Product.objects.get_or_create(product_name=form.data['product_cod'],refectory_id=self.kwargs['pk'])
        form.data._mutable = True
        form.data['product_cod'] = product.id
        form.data._mutable = False

        if form.is_valid():
            return self.form_valid(form, product, created)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, product, created):
        self.object = form.save(commit=False)
        self.object.product_name = product.product_name
        self.object.product_total_amount = self.object.product_quantity * self.object.product_unitary_amount
        #si no existia el producto, se creo en el get or create
        if created:
            product.total_product_quantity = self.object.product_quantity
            product.created_by = self.request.user
            product.refectory_id = self.kwargs['pk']
        #ya existia el producto
        else:
            if self.object.operation_type == 'ingreso':    
                product.total_product_quantity = product.total_product_quantity + self.object.product_quantity
                product.created_by = self.request.user
                product.refectory_id = self.kwargs['pk']                    
            else:
                #si intento sacar mas de lo que hay
                if self.object.product_quantity > product.total_product_quantity:
                    return self.form_invalid(form)
                product.total_product_quantity = product.total_product_quantity - self.object.product_quantity
                product.created_by = self.request.user
                product.refectory_id = self.kwargs['pk']                

        product.save()
        self.object.created_by = self.request.user
        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(
                form=form,
            )
        )
